"""
Document Versioning System
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass, asdict
from enum import Enum


logger = logging.getLogger(__name__)


class VersionChangeType(str, Enum):
    """Types of version changes"""
    CREATED = "created"
    CONTENT_UPDATE = "content_update"
    METADATA_UPDATE = "metadata_update"
    REPROCESSED = "reprocessed"
    SCHEMA_MIGRATION = "schema_migration"
    MANUAL_EDIT = "manual_edit"
    AUTO_CORRECTION = "auto_correction"


@dataclass
class DocumentVersion:
    """Represents a document version"""
    version_id: str
    document_id: str
    version_number: int
    created_at: datetime
    created_by: Optional[str]
    change_type: VersionChangeType
    change_description: Optional[str]
    content_hash: str
    metadata_hash: str
    file_path: Optional[str]
    processing_params: Optional[Dict[str, Any]]
    parent_version_id: Optional[str]
    is_current: bool
    tags: List[str]
    size_bytes: Optional[int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["change_type"] = self.change_type.value
        return data


class DocumentVersioningService:
    """Service for managing document versions"""

    def __init__(self, storage_path: str = "/tmp/netintel_versions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # In-memory version tracking (should be persisted in production)
        self.versions: Dict[str, List[DocumentVersion]] = {}
        self.current_versions: Dict[str, str] = {}  # document_id -> current_version_id

    def create_version(
        self,
        document_id: str,
        content: bytes,
        metadata: Dict[str, Any],
        change_type: VersionChangeType = VersionChangeType.CREATED,
        change_description: Optional[str] = None,
        created_by: Optional[str] = None,
        processing_params: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> DocumentVersion:
        """Create a new version of a document"""

        # Generate version ID
        version_id = self._generate_version_id(document_id)

        # Get version number
        existing_versions = self.versions.get(document_id, [])
        version_number = len(existing_versions) + 1

        # Calculate hashes
        content_hash = hashlib.sha256(content).hexdigest()
        metadata_hash = hashlib.sha256(
            json.dumps(metadata, sort_keys=True).encode()
        ).hexdigest()

        # Get parent version
        parent_version_id = None
        if existing_versions:
            parent_version_id = existing_versions[-1].version_id

        # Store content
        version_file_path = self._store_version_content(
            document_id,
            version_id,
            content,
        )

        # Create version object
        version = DocumentVersion(
            version_id=version_id,
            document_id=document_id,
            version_number=version_number,
            created_at=datetime.utcnow(),
            created_by=created_by,
            change_type=change_type,
            change_description=change_description,
            content_hash=content_hash,
            metadata_hash=metadata_hash,
            file_path=str(version_file_path),
            processing_params=processing_params,
            parent_version_id=parent_version_id,
            is_current=True,
            tags=tags or [],
            size_bytes=len(content),
        )

        # Update current flags
        for v in existing_versions:
            v.is_current = False

        # Store version
        if document_id not in self.versions:
            self.versions[document_id] = []
        self.versions[document_id].append(version)
        self.current_versions[document_id] = version_id

        # Store metadata
        self._store_version_metadata(version, metadata)

        logger.info(f"Created version {version_id} for document {document_id}")

        return version

    def get_version(
        self,
        document_id: str,
        version_id: Optional[str] = None,
        version_number: Optional[int] = None,
    ) -> Optional[DocumentVersion]:
        """Get a specific version of a document"""

        if document_id not in self.versions:
            return None

        versions = self.versions[document_id]

        if version_id:
            for version in versions:
                if version.version_id == version_id:
                    return version
        elif version_number:
            for version in versions:
                if version.version_number == version_number:
                    return version
        else:
            # Return current version
            current_version_id = self.current_versions.get(document_id)
            if current_version_id:
                for version in versions:
                    if version.version_id == current_version_id:
                        return version

        return None

    def get_current_version(self, document_id: str) -> Optional[DocumentVersion]:
        """Get the current version of a document"""
        return self.get_version(document_id)

    def list_versions(
        self,
        document_id: str,
        include_metadata: bool = False,
    ) -> List[Dict[str, Any]]:
        """List all versions of a document"""

        if document_id not in self.versions:
            return []

        versions = []
        for version in self.versions[document_id]:
            version_dict = version.to_dict()

            if include_metadata:
                metadata = self._load_version_metadata(version)
                version_dict["metadata"] = metadata

            versions.append(version_dict)

        return sorted(versions, key=lambda x: x["version_number"], reverse=True)

    def compare_versions(
        self,
        document_id: str,
        version1_id: str,
        version2_id: str,
    ) -> Dict[str, Any]:
        """Compare two versions of a document"""

        v1 = self.get_version(document_id, version_id=version1_id)
        v2 = self.get_version(document_id, version_id=version2_id)

        if not v1 or not v2:
            raise ValueError("One or both versions not found")

        # Load content
        content1 = self._load_version_content(v1)
        content2 = self._load_version_content(v2)

        # Load metadata
        metadata1 = self._load_version_metadata(v1)
        metadata2 = self._load_version_metadata(v2)

        # Calculate differences
        comparison = {
            "version1": {
                "version_id": v1.version_id,
                "version_number": v1.version_number,
                "created_at": v1.created_at.isoformat(),
                "content_hash": v1.content_hash,
                "metadata_hash": v1.metadata_hash,
                "size_bytes": v1.size_bytes,
            },
            "version2": {
                "version_id": v2.version_id,
                "version_number": v2.version_number,
                "created_at": v2.created_at.isoformat(),
                "content_hash": v2.content_hash,
                "metadata_hash": v2.metadata_hash,
                "size_bytes": v2.size_bytes,
            },
            "content_changed": v1.content_hash != v2.content_hash,
            "metadata_changed": v1.metadata_hash != v2.metadata_hash,
            "size_difference": (v2.size_bytes or 0) - (v1.size_bytes or 0),
            "time_difference": (v2.created_at - v1.created_at).total_seconds(),
        }

        # Add metadata differences
        if comparison["metadata_changed"]:
            comparison["metadata_diff"] = self._compute_metadata_diff(
                metadata1,
                metadata2,
            )

        return comparison

    def rollback_version(
        self,
        document_id: str,
        target_version_id: str,
        reason: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> DocumentVersion:
        """Rollback to a previous version"""

        target_version = self.get_version(document_id, version_id=target_version_id)
        if not target_version:
            raise ValueError(f"Version {target_version_id} not found")

        # Load target version content and metadata
        content = self._load_version_content(target_version)
        metadata = self._load_version_metadata(target_version)

        # Create new version as rollback
        new_version = self.create_version(
            document_id=document_id,
            content=content,
            metadata=metadata,
            change_type=VersionChangeType.CONTENT_UPDATE,
            change_description=f"Rollback to version {target_version.version_number}: {reason}",
            created_by=created_by,
            processing_params=target_version.processing_params,
            tags=["rollback"],
        )

        logger.info(f"Rolled back document {document_id} to version {target_version_id}")

        return new_version

    def merge_versions(
        self,
        document_id: str,
        version_ids: List[str],
        merge_strategy: str = "latest",
        created_by: Optional[str] = None,
    ) -> DocumentVersion:
        """Merge multiple versions"""

        versions = []
        for version_id in version_ids:
            version = self.get_version(document_id, version_id=version_id)
            if version:
                versions.append(version)

        if len(versions) < 2:
            raise ValueError("At least 2 versions required for merge")

        # Sort by version number
        versions.sort(key=lambda x: x.version_number)

        # Apply merge strategy
        if merge_strategy == "latest":
            # Use the latest version's content
            merged_content = self._load_version_content(versions[-1])
            merged_metadata = self._load_version_metadata(versions[-1])
        else:
            raise ValueError(f"Unknown merge strategy: {merge_strategy}")

        # Create merged version
        merged_version = self.create_version(
            document_id=document_id,
            content=merged_content,
            metadata=merged_metadata,
            change_type=VersionChangeType.CONTENT_UPDATE,
            change_description=f"Merged versions: {', '.join([v.version_id for v in versions])}",
            created_by=created_by,
            tags=["merged"],
        )

        return merged_version

    def delete_version(
        self,
        document_id: str,
        version_id: str,
        hard_delete: bool = False,
    ) -> bool:
        """Delete a version"""

        if document_id not in self.versions:
            return False

        # Find version
        version = None
        version_index = None
        for i, v in enumerate(self.versions[document_id]):
            if v.version_id == version_id:
                version = v
                version_index = i
                break

        if not version:
            return False

        # Don't delete current version unless it's the only one
        if version.is_current and len(self.versions[document_id]) > 1:
            raise ValueError("Cannot delete current version")

        if hard_delete:
            # Delete files
            if version.file_path and Path(version.file_path).exists():
                Path(version.file_path).unlink()

            metadata_path = self._get_metadata_path(version)
            if metadata_path.exists():
                metadata_path.unlink()

            # Remove from list
            del self.versions[document_id][version_index]
        else:
            # Soft delete - mark as deleted
            version.tags.append("deleted")

        logger.info(f"Deleted version {version_id} (hard={hard_delete})")

        return True

    def _generate_version_id(self, document_id: str) -> str:
        """Generate a unique version ID"""
        timestamp = datetime.utcnow().isoformat()
        data = f"{document_id}:{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def _store_version_content(
        self,
        document_id: str,
        version_id: str,
        content: bytes,
    ) -> Path:
        """Store version content to disk"""

        # Create document directory
        doc_dir = self.storage_path / document_id
        doc_dir.mkdir(parents=True, exist_ok=True)

        # Store content
        content_path = doc_dir / f"{version_id}.content"
        content_path.write_bytes(content)

        return content_path

    def _load_version_content(self, version: DocumentVersion) -> bytes:
        """Load version content from disk"""

        if version.file_path and Path(version.file_path).exists():
            return Path(version.file_path).read_bytes()

        # Fallback to storage path
        content_path = self.storage_path / version.document_id / f"{version.version_id}.content"
        if content_path.exists():
            return content_path.read_bytes()

        raise FileNotFoundError(f"Content not found for version {version.version_id}")

    def _store_version_metadata(
        self,
        version: DocumentVersion,
        metadata: Dict[str, Any],
    ):
        """Store version metadata"""

        metadata_path = self._get_metadata_path(version)
        metadata_path.write_text(json.dumps(metadata, indent=2))

    def _load_version_metadata(self, version: DocumentVersion) -> Dict[str, Any]:
        """Load version metadata"""

        metadata_path = self._get_metadata_path(version)
        if metadata_path.exists():
            return json.loads(metadata_path.read_text())
        return {}

    def _get_metadata_path(self, version: DocumentVersion) -> Path:
        """Get metadata file path for a version"""
        return self.storage_path / version.document_id / f"{version.version_id}.metadata.json"

    def _compute_metadata_diff(
        self,
        metadata1: Dict[str, Any],
        metadata2: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Compute differences between two metadata dictionaries"""

        diff = {
            "added": {},
            "removed": {},
            "modified": {},
        }

        # Find added and modified keys
        for key, value in metadata2.items():
            if key not in metadata1:
                diff["added"][key] = value
            elif metadata1[key] != value:
                diff["modified"][key] = {
                    "old": metadata1[key],
                    "new": value,
                }

        # Find removed keys
        for key, value in metadata1.items():
            if key not in metadata2:
                diff["removed"][key] = value

        return diff

    def get_version_history(
        self,
        document_id: str,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Get version history with pagination"""

        if document_id not in self.versions:
            return {
                "document_id": document_id,
                "total_versions": 0,
                "versions": [],
            }

        all_versions = self.versions[document_id]
        total = len(all_versions)

        # Sort by version number descending
        sorted_versions = sorted(
            all_versions,
            key=lambda x: x.version_number,
            reverse=True,
        )

        # Apply pagination
        paginated = sorted_versions[offset:offset + limit]

        return {
            "document_id": document_id,
            "total_versions": total,
            "current_version_id": self.current_versions.get(document_id),
            "versions": [v.to_dict() for v in paginated],
            "has_more": offset + limit < total,
        }


# Global versioning service instance
versioning_service = DocumentVersioningService()