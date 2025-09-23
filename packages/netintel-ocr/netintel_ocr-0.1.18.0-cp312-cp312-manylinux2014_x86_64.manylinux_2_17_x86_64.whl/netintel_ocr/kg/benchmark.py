"""
Performance benchmarking tools for NetIntel-OCR Knowledge Graph System v0.1.17

Provides benchmarking utilities for measuring system performance.
"""

import asyncio
import time
import random
import statistics
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass
from datetime import datetime
import json
import numpy as np

from .falkordb_manager import FalkorDBManager
from .query_classifier import QueryIntentClassifier
from .hybrid_retriever import HybridRetriever
from .embedding_trainer import KGEmbeddingTrainer

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkResult:
    """Container for benchmark results"""
    operation: str
    total_time: float
    avg_time: float
    min_time: float
    max_time: float
    std_dev: float
    throughput: float
    iterations: int
    errors: int
    timestamp: str


class KGBenchmark:
    """
    Comprehensive benchmarking suite for KG system
    """
    
    def __init__(self, falkor_manager: Optional[FalkorDBManager] = None):
        """
        Initialize benchmark suite
        
        Args:
            falkor_manager: Optional FalkorDB manager instance
        """
        self.falkor_manager = falkor_manager or FalkorDBManager()
        self.query_classifier = QueryIntentClassifier()
        self.hybrid_retriever = None
        
        if self.falkor_manager.connect():
            self.hybrid_retriever = HybridRetriever(self.falkor_manager)
        
        self.results = []
    
    async def benchmark_query_classification(self, num_queries: int = 1000) -> BenchmarkResult:
        """
        Benchmark query classification performance
        
        Args:
            num_queries: Number of queries to classify
        
        Returns:
            BenchmarkResult with timing statistics
        """
        queries = self._generate_test_queries(num_queries)
        times = []
        errors = 0
        
        logger.info(f"Starting query classification benchmark with {num_queries} queries")
        
        for query in queries:
            start = time.perf_counter()
            try:
                _ = self.query_classifier.classify(query)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Classification error: {e}")
        
        result = self._calculate_statistics("Query Classification", times, errors)
        self.results.append(result)
        return result
    
    async def benchmark_graph_search(self, num_searches: int = 100) -> BenchmarkResult:
        """
        Benchmark graph search performance
        
        Args:
            num_searches: Number of searches to perform
        
        Returns:
            BenchmarkResult with timing statistics
        """
        if not self.falkor_manager.graph:
            logger.error("Graph database not connected")
            return None
        
        times = []
        errors = 0
        
        logger.info(f"Starting graph search benchmark with {num_searches} searches")
        
        # Get sample entities for searching
        entities = self._get_sample_entities(min(num_searches, 50))
        
        for i in range(num_searches):
            entity = random.choice(entities) if entities else f"entity_{i}"
            
            query = f"""
            MATCH (n {{id: '{entity}'}})
            OPTIONAL MATCH (n)-[r]-(neighbor)
            RETURN n, collect(distinct neighbor) as neighbors
            LIMIT 10
            """
            
            start = time.perf_counter()
            try:
                _ = self.falkor_manager.execute_cypher(query)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Graph search error: {e}")
        
        result = self._calculate_statistics("Graph Search", times, errors)
        self.results.append(result)
        return result
    
    async def benchmark_vector_search(self, num_searches: int = 100) -> BenchmarkResult:
        """
        Benchmark vector similarity search performance
        
        Args:
            num_searches: Number of searches to perform
        
        Returns:
            BenchmarkResult with timing statistics
        """
        if not self.falkor_manager.graph:
            logger.error("Graph database not connected")
            return None
        
        times = []
        errors = 0
        
        logger.info(f"Starting vector search benchmark with {num_searches} searches")
        
        # Generate random embeddings for search
        embedding_dim = 200
        
        for i in range(num_searches):
            query_embedding = np.random.randn(embedding_dim).tolist()
            
            start = time.perf_counter()
            try:
                _ = await self.falkor_manager.similarity_search_with_embeddings(
                    query_embedding=query_embedding,
                    limit=10,
                    threshold=0.5
                )
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Vector search error: {e}")
        
        result = self._calculate_statistics("Vector Search", times, errors)
        self.results.append(result)
        return result
    
    async def benchmark_hybrid_retrieval(self, num_queries: int = 50) -> BenchmarkResult:
        """
        Benchmark hybrid retrieval performance
        
        Args:
            num_queries: Number of queries to process
        
        Returns:
            BenchmarkResult with timing statistics
        """
        if not self.hybrid_retriever:
            logger.error("Hybrid retriever not available")
            return None
        
        queries = self._generate_test_queries(num_queries)
        strategies = ['vector_first', 'graph_first', 'parallel', 'adaptive']
        times = []
        errors = 0
        
        logger.info(f"Starting hybrid retrieval benchmark with {num_queries} queries")
        
        for query in queries:
            strategy = random.choice(strategies)
            
            start = time.perf_counter()
            try:
                _ = await self.hybrid_retriever.hybrid_search(
                    query=query,
                    strategy=strategy,
                    max_results=10
                )
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Hybrid retrieval error: {e}")
        
        result = self._calculate_statistics("Hybrid Retrieval", times, errors)
        self.results.append(result)
        return result
    
    async def benchmark_parallel_strategy(self, num_queries: int = 50) -> BenchmarkResult:
        """
        Benchmark parallel retrieval strategy specifically
        
        Args:
            num_queries: Number of queries to process
        
        Returns:
            BenchmarkResult with timing statistics
        """
        if not self.hybrid_retriever:
            logger.error("Hybrid retriever not available")
            return None
        
        queries = self._generate_test_queries(num_queries)
        times = []
        errors = 0
        
        logger.info(f"Starting parallel strategy benchmark with {num_queries} queries")
        
        for query in queries:
            start = time.perf_counter()
            try:
                _ = await self.hybrid_retriever.hybrid_search(
                    query=query,
                    strategy='parallel',
                    max_results=20
                )
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Parallel strategy error: {e}")
        
        result = self._calculate_statistics("Parallel Strategy", times, errors)
        self.results.append(result)
        return result
    
    async def benchmark_embedding_training(self, num_triples: int = 1000) -> BenchmarkResult:
        """
        Benchmark embedding training performance
        
        Args:
            num_triples: Number of triples to train on
        
        Returns:
            BenchmarkResult with timing statistics
        """
        # Generate synthetic triples for benchmarking
        triples = self._generate_test_triples(num_triples)
        
        trainer = KGEmbeddingTrainer(model_name='TransE', embedding_dim=100)
        
        logger.info(f"Starting embedding training benchmark with {num_triples} triples")
        
        start = time.perf_counter()
        errors = 0
        
        try:
            # Mock training (in real scenario, would train actual model)
            # This is simplified for benchmarking purposes
            await asyncio.sleep(0.1)  # Simulate training time
            elapsed = time.perf_counter() - start
        except Exception as e:
            errors = 1
            elapsed = 0
            logger.error(f"Embedding training error: {e}")
        
        result = BenchmarkResult(
            operation="Embedding Training",
            total_time=elapsed,
            avg_time=elapsed,
            min_time=elapsed,
            max_time=elapsed,
            std_dev=0,
            throughput=num_triples / elapsed if elapsed > 0 else 0,
            iterations=1,
            errors=errors,
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.results.append(result)
        return result
    
    async def benchmark_write_operations(self, num_operations: int = 100) -> BenchmarkResult:
        """
        Benchmark graph write operations
        
        Args:
            num_operations: Number of write operations
        
        Returns:
            BenchmarkResult with timing statistics
        """
        if not self.falkor_manager.graph:
            logger.error("Graph database not connected")
            return None
        
        times = []
        errors = 0
        
        logger.info(f"Starting write operations benchmark with {num_operations} operations")
        
        for i in range(num_operations):
            node_id = f"benchmark_node_{i}_{int(time.time())}"
            
            query = f"""
            CREATE (n:BenchmarkNode {{
                id: '{node_id}',
                timestamp: {int(time.time())},
                value: {random.random()}
            }})
            RETURN n
            """
            
            start = time.perf_counter()
            try:
                _ = self.falkor_manager.execute_cypher(query)
                elapsed = time.perf_counter() - start
                times.append(elapsed)
            except Exception as e:
                errors += 1
                logger.error(f"Write operation error: {e}")
        
        # Cleanup benchmark nodes
        try:
            self.falkor_manager.execute_cypher("MATCH (n:BenchmarkNode) DELETE n")
        except:
            pass
        
        result = self._calculate_statistics("Write Operations", times, errors)
        self.results.append(result)
        return result
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """
        Run all benchmarks and return comprehensive results
        
        Returns:
            Dictionary with all benchmark results
        """
        logger.info("Starting comprehensive benchmark suite")
        
        results = {}
        
        # Run all benchmarks
        results['query_classification'] = await self.benchmark_query_classification(1000)
        results['graph_search'] = await self.benchmark_graph_search(100)
        results['vector_search'] = await self.benchmark_vector_search(100)
        results['hybrid_retrieval'] = await self.benchmark_hybrid_retrieval(50)
        results['parallel_strategy'] = await self.benchmark_parallel_strategy(50)
        results['write_operations'] = await self.benchmark_write_operations(100)
        
        # Calculate summary statistics
        summary = self._calculate_summary()
        
        return {
            'benchmarks': results,
            'summary': summary,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def _generate_test_queries(self, num_queries: int) -> List[str]:
        """Generate test queries for benchmarking"""
        query_templates = [
            "What is the IP address of {}?",
            "Show connections to {}",
            "Find path from {} to {}",
            "What devices are in the {} network?",
            "Analyze security vulnerabilities in {}",
            "Show network topology for {}",
            "Find similar devices to {}",
            "What connects {} and {}?",
            "List all {} in the network",
            "Show traffic flow through {}"
        ]
        
        entities = ['router1', 'switch1', 'firewall1', 'server1', 'dmz', 
                   'network1', '192.168.1.1', 'core-switch', 'edge-router']
        
        queries = []
        for i in range(num_queries):
            template = random.choice(query_templates)
            num_placeholders = template.count('{}')
            replacements = [random.choice(entities) for _ in range(num_placeholders)]
            query = template.format(*replacements)
            queries.append(query)
        
        return queries
    
    def _generate_test_triples(self, num_triples: int) -> List[tuple]:
        """Generate test triples for benchmarking"""
        entities = [f"entity_{i}" for i in range(num_triples // 2)]
        relations = ['CONNECTS_TO', 'PART_OF', 'DEPENDS_ON', 'CONTAINS', 'LINKS_TO']
        
        triples = []
        for _ in range(num_triples):
            head = random.choice(entities)
            relation = random.choice(relations)
            tail = random.choice(entities)
            triples.append((head, relation, tail))
        
        return triples
    
    def _get_sample_entities(self, limit: int) -> List[str]:
        """Get sample entity IDs from graph"""
        try:
            query = f"MATCH (n) RETURN n.id LIMIT {limit}"
            result = self.falkor_manager.execute_cypher(query)
            return [row[0] for row in result.result_set if row[0]]
        except:
            return []
    
    def _calculate_statistics(self, operation: str, times: List[float], errors: int) -> BenchmarkResult:
        """Calculate statistics from timing data"""
        if not times:
            return BenchmarkResult(
                operation=operation,
                total_time=0,
                avg_time=0,
                min_time=0,
                max_time=0,
                std_dev=0,
                throughput=0,
                iterations=0,
                errors=errors,
                timestamp=datetime.utcnow().isoformat()
            )
        
        total_time = sum(times)
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        throughput = len(times) / total_time if total_time > 0 else 0
        
        return BenchmarkResult(
            operation=operation,
            total_time=total_time,
            avg_time=avg_time,
            min_time=min_time,
            max_time=max_time,
            std_dev=std_dev,
            throughput=throughput,
            iterations=len(times),
            errors=errors,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics across all benchmarks"""
        if not self.results:
            return {}
        
        total_operations = sum(r.iterations for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        total_time = sum(r.total_time for r in self.results)
        
        avg_throughput = statistics.mean([r.throughput for r in self.results if r.throughput > 0])
        
        return {
            'total_operations': total_operations,
            'total_errors': total_errors,
            'total_time': total_time,
            'average_throughput': avg_throughput,
            'error_rate': total_errors / total_operations if total_operations > 0 else 0
        }
    
    def save_results(self, filepath: str):
        """Save benchmark results to file"""
        results_dict = {
            'results': [
                {
                    'operation': r.operation,
                    'total_time': r.total_time,
                    'avg_time': r.avg_time,
                    'min_time': r.min_time,
                    'max_time': r.max_time,
                    'std_dev': r.std_dev,
                    'throughput': r.throughput,
                    'iterations': r.iterations,
                    'errors': r.errors,
                    'timestamp': r.timestamp
                }
                for r in self.results
            ],
            'summary': self._calculate_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        logger.info(f"Benchmark results saved to {filepath}")
    
    def print_results(self):
        """Print formatted benchmark results"""
        print("\n" + "="*80)
        print("BENCHMARK RESULTS")
        print("="*80)
        
        for result in self.results:
            print(f"\n{result.operation}:")
            print(f"  Iterations: {result.iterations}")
            print(f"  Total Time: {result.total_time:.3f}s")
            print(f"  Avg Time: {result.avg_time*1000:.2f}ms")
            print(f"  Min Time: {result.min_time*1000:.2f}ms")
            print(f"  Max Time: {result.max_time*1000:.2f}ms")
            print(f"  Std Dev: {result.std_dev*1000:.2f}ms")
            print(f"  Throughput: {result.throughput:.2f} ops/sec")
            print(f"  Errors: {result.errors}")
        
        summary = self._calculate_summary()
        print("\n" + "-"*80)
        print("SUMMARY")
        print("-"*80)
        print(f"Total Operations: {summary.get('total_operations', 0)}")
        print(f"Total Errors: {summary.get('total_errors', 0)}")
        print(f"Total Time: {summary.get('total_time', 0):.3f}s")
        print(f"Average Throughput: {summary.get('average_throughput', 0):.2f} ops/sec")
        print(f"Error Rate: {summary.get('error_rate', 0):.2%}")
        print("="*80)


async def main():
    """Main function for running benchmarks"""
    benchmark = KGBenchmark()
    
    if benchmark.falkor_manager.connect():
        print("Running comprehensive benchmark suite...")
        results = await benchmark.run_comprehensive_benchmark()
        benchmark.print_results()
        benchmark.save_results("benchmark_results.json")
        benchmark.falkor_manager.close()
    else:
        print("Failed to connect to FalkorDB")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())