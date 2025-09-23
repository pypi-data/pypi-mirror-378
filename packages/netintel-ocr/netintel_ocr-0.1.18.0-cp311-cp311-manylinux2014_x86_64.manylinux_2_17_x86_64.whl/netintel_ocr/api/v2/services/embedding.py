"""
Embedding Generation Service
"""

import numpy as np
from typing import List, Optional, Dict, Any, Union
import hashlib
import logging
from sentence_transformers import SentenceTransformer
import torch
from transformers import AutoTokenizer, AutoModel
import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache


logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings from text"""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: Optional[str] = None,
        cache_embeddings: bool = True,
        batch_size: int = 32,
        max_length: int = 512,
    ):
        """
        Initialize embedding service

        Args:
            model_name: Name of the model to use
            device: Device to use (cuda, cpu, or None for auto)
            cache_embeddings: Whether to cache embeddings
            batch_size: Batch size for encoding
            max_length: Maximum sequence length
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        self.cache_embeddings = cache_embeddings

        # Set device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        # Initialize model
        self._init_model()

        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Embedding cache
        self._embedding_cache = {} if cache_embeddings else None

        logger.info(f"Initialized EmbeddingService with model {model_name} on {self.device}")

    def _init_model(self):
        """Initialize the embedding model"""

        try:
            # Try to use sentence-transformers
            self.model = SentenceTransformer(self.model_name)
            self.model.to(self.device)
            self.model_type = "sentence_transformer"
            self.embedding_dim = self.model.get_sentence_embedding_dimension()

        except Exception as e:
            logger.warning(f"Failed to load as SentenceTransformer: {e}")

            # Fallback to transformers
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModel.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                self.model_type = "transformer"

                # Get embedding dimension from model config
                self.embedding_dim = self.model.config.hidden_size

            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""

        return hashlib.md5(f"{self.model_name}:{text}".encode()).hexdigest()

    def encode(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)

        Args:
            texts: Single text or list of texts
            normalize: Whether to normalize embeddings
            show_progress_bar: Whether to show progress bar

        Returns:
            Numpy array of embeddings
        """

        # Convert single text to list
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False

        # Check cache
        if self.cache_embeddings:
            cached_embeddings = []
            texts_to_encode = []
            cache_indices = []

            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self._embedding_cache:
                    cached_embeddings.append(self._embedding_cache[cache_key])
                else:
                    texts_to_encode.append(text)
                    cache_indices.append(i)

            # If all embeddings are cached
            if not texts_to_encode:
                embeddings = np.array(cached_embeddings)
                return embeddings[0] if single_text else embeddings

        else:
            texts_to_encode = texts
            cache_indices = list(range(len(texts)))

        # Generate embeddings
        if self.model_type == "sentence_transformer":
            embeddings = self._encode_sentence_transformer(
                texts_to_encode,
                normalize=normalize,
                show_progress_bar=show_progress_bar,
            )
        else:
            embeddings = self._encode_transformer(
                texts_to_encode,
                normalize=normalize,
            )

        # Cache embeddings
        if self.cache_embeddings:
            for text, embedding in zip(texts_to_encode, embeddings):
                cache_key = self._get_cache_key(text)
                self._embedding_cache[cache_key] = embedding

            # Combine cached and new embeddings
            if cached_embeddings:
                all_embeddings = np.zeros((len(texts), self.embedding_dim))
                cached_idx = 0
                new_idx = 0

                for i in range(len(texts)):
                    if i in cache_indices:
                        all_embeddings[i] = embeddings[new_idx]
                        new_idx += 1
                    else:
                        all_embeddings[i] = cached_embeddings[cached_idx]
                        cached_idx += 1

                embeddings = all_embeddings

        return embeddings[0] if single_text else embeddings

    def _encode_sentence_transformer(
        self,
        texts: List[str],
        normalize: bool = True,
        show_progress_bar: bool = False,
    ) -> np.ndarray:
        """Encode using sentence-transformers"""

        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=normalize,
            show_progress_bar=show_progress_bar,
            convert_to_numpy=True,
        )

        return embeddings

    def _encode_transformer(
        self,
        texts: List[str],
        normalize: bool = True,
    ) -> np.ndarray:
        """Encode using transformers"""

        embeddings = []

        with torch.no_grad():
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]

                # Tokenize
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=self.max_length,
                    return_tensors="pt",
                ).to(self.device)

                # Get embeddings
                outputs = self.model(**inputs)

                # Mean pooling
                attention_mask = inputs["attention_mask"]
                token_embeddings = outputs.last_hidden_state
                input_mask_expanded = (
                    attention_mask.unsqueeze(-1)
                    .expand(token_embeddings.size())
                    .float()
                )
                batch_embeddings = torch.sum(
                    token_embeddings * input_mask_expanded, 1
                ) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

                # Normalize if requested
                if normalize:
                    batch_embeddings = torch.nn.functional.normalize(
                        batch_embeddings, p=2, dim=1
                    )

                embeddings.append(batch_embeddings.cpu().numpy())

        embeddings = np.vstack(embeddings)
        return embeddings

    async def encode_async(
        self,
        texts: Union[str, List[str]],
        normalize: bool = True,
    ) -> np.ndarray:
        """Asynchronous embedding generation"""

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self.encode,
            texts,
            normalize,
        )

    def encode_batch(
        self,
        texts: List[str],
        batch_size: Optional[int] = None,
        normalize: bool = True,
        show_progress_bar: bool = True,
    ) -> np.ndarray:
        """
        Encode texts in batches

        Args:
            texts: List of texts
            batch_size: Batch size (uses default if None)
            normalize: Whether to normalize embeddings
            show_progress_bar: Whether to show progress

        Returns:
            Numpy array of embeddings
        """

        if batch_size is None:
            batch_size = self.batch_size

        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_embeddings = self.encode(
                batch,
                normalize=normalize,
                show_progress_bar=False,
            )
            embeddings.append(batch_embeddings)

        return np.vstack(embeddings)

    def similarity(
        self,
        embeddings1: np.ndarray,
        embeddings2: np.ndarray,
        metric: str = "cosine",
    ) -> np.ndarray:
        """
        Calculate similarity between embeddings

        Args:
            embeddings1: First set of embeddings
            embeddings2: Second set of embeddings
            metric: Similarity metric (cosine, euclidean, manhattan)

        Returns:
            Similarity scores
        """

        if metric == "cosine":
            # Normalize embeddings
            embeddings1 = embeddings1 / np.linalg.norm(embeddings1, axis=-1, keepdims=True)
            embeddings2 = embeddings2 / np.linalg.norm(embeddings2, axis=-1, keepdims=True)
            return np.dot(embeddings1, embeddings2.T)

        elif metric == "euclidean":
            return -np.linalg.norm(embeddings1[:, None] - embeddings2, axis=-1)

        elif metric == "manhattan":
            return -np.abs(embeddings1[:, None] - embeddings2).sum(axis=-1)

        else:
            raise ValueError(f"Unknown metric: {metric}")

    def clear_cache(self):
        """Clear embedding cache"""

        if self._embedding_cache:
            self._embedding_cache.clear()
            logger.info("Cleared embedding cache")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""

        if not self.cache_embeddings:
            return {"enabled": False}

        return {
            "enabled": True,
            "size": len(self._embedding_cache),
            "memory_usage_mb": sum(
                embedding.nbytes for embedding in self._embedding_cache.values()
            ) / (1024 * 1024),
        }

    @lru_cache(maxsize=128)
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""

        return {
            "model_name": self.model_name,
            "model_type": self.model_type,
            "embedding_dimension": self.embedding_dim,
            "device": self.device,
            "max_sequence_length": self.max_length,
            "batch_size": self.batch_size,
            "cache_enabled": self.cache_embeddings,
        }


# Global embedding service instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service(
    model_name: Optional[str] = None,
    **kwargs,
) -> EmbeddingService:
    """Get or create embedding service instance"""

    global _embedding_service

    if _embedding_service is None or (model_name and model_name != _embedding_service.model_name):
        _embedding_service = EmbeddingService(
            model_name=model_name or "sentence-transformers/all-MiniLM-L6-v2",
            **kwargs,
        )

    return _embedding_service