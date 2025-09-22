"""
CLI Commands for Knowledge Graph functionality in NetIntel-OCR v0.1.17

Provides command-line interface for KG operations.
"""

import os
import sys
import json
import asyncio
import logging
from typing import Optional

import click

from .falkordb_manager import FalkorDBManager
from .graph_constructor import KnowledgeGraphConstructor
from .hybrid_system import HybridSystem
from .embedding_trainer import KGEmbeddingTrainer
from .embedding_utils import EmbeddingAnalyzer, load_embeddings_from_falkordb

# Try to import EnhancedMiniRAG, but don't fail if MiniRAG is broken
try:
    from .enhanced_minirag import EnhancedMiniRAG
except Exception:
    # MiniRAG import failed, create a dummy class
    class EnhancedMiniRAG:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("MiniRAG is not properly installed. Please install: pip install minirag-hku json-repair tiktoken sentence-transformers nltk rouge rouge-score")

from .query_classifier import QueryIntentClassifier, QueryType
from .hybrid_retriever import HybridRetriever

logger = logging.getLogger(__name__)


@click.group(name='kg')
def kg_cli():
    """Knowledge Graph management commands for NetIntel-OCR v0.1.17"""
    pass


@kg_cli.command(name='check-requirements')
@click.option('--verbose', is_flag=True, help='Show detailed information')
def check_requirements(verbose):
    """Check if all KG requirements are installed and configured"""

    click.echo("🔍 Checking Knowledge Graph Requirements...")
    click.echo()

    all_ok = True

    # Check Python version
    import sys
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        click.echo(f"✅ Python {python_version} (>= 3.8 required)")
    else:
        click.echo(f"❌ Python {python_version} (>= 3.8 required)")
        all_ok = False

    # Check required packages
    packages = {
        'falkordb': 'FalkorDB client',
        'graphiti_core': 'Graphiti Core',
        'pykeen': 'PyKEEN',
        'torch': 'PyTorch',
        'numpy': 'NumPy',
        'pandas': 'Pandas',
        'click': 'Click CLI',
        'asyncio': 'AsyncIO'
    }

    click.echo("\n📦 Package Requirements:")
    for package, description in packages.items():
        try:
            if package == 'asyncio':
                import asyncio
            elif package == 'graphiti_core':
                import graphiti_core
            else:
                __import__(package)

            if verbose:
                try:
                    import importlib.metadata
                    version = importlib.metadata.version(package.replace('_', '-'))
                    click.echo(f"  ✅ {description} ({package} v{version})")
                except:
                    click.echo(f"  ✅ {description} ({package})")
            else:
                click.echo(f"  ✅ {description}")
        except ImportError:
            click.echo(f"  ❌ {description} ({package}) - Not installed")
            all_ok = False

    # Check MiniRAG (now mandatory)
    click.echo("\n📦 Required MiniRAG Package:")
    try:
        # Check if the package is installed
        import importlib.metadata
        try:
            version = importlib.metadata.version('minirag-hku')
            minirag_installed = True
            minirag_version = version
        except:
            minirag_installed = False
            minirag_version = None

        # Try to import it
        if minirag_installed:
            try:
                from minirag import MiniRAG
                if verbose:
                    click.echo(f"  ✅ MiniRAG (for enhanced retrieval) - minirag-hku v{minirag_version}")
                else:
                    click.echo(f"  ✅ MiniRAG (for enhanced retrieval)")
            except Exception as e:
                # Package is installed but broken
                click.echo(f"  ⚠️  MiniRAG (minirag-hku v{minirag_version}) - Installed but has import errors")
                click.echo(f"     Note: The package appears to have missing dependencies or bugs")
                click.echo(f"     Install dependencies: pip install json-repair tiktoken sentence-transformers nltk rouge rouge-score")
                if verbose:
                    click.echo(f"     Error: {str(e)}")
        else:
            click.echo(f"  ❌ MiniRAG (minirag-hku) - Not installed")
            click.echo(f"     Install with: pip install minirag-hku")
            click.echo(f"     Also install dependencies: pip install json-repair tiktoken sentence-transformers nltk rouge rouge-score")
            all_ok = False
    except Exception as e:
        click.echo(f"  ❌ MiniRAG check failed: {e}")
        all_ok = False

    # Check optional packages
    click.echo("\n📦 Optional Packages:")
    optional = {
        'matplotlib': 'Matplotlib (for visualization)',
        'plotly': 'Plotly (for interactive plots)',
        'scikit-learn': 'Scikit-learn (for clustering)'
    }

    for package, description in optional.items():
        try:
            if package == 'scikit-learn':
                import sklearn
            else:
                __import__(package)
            click.echo(f"  ✅ {description}")
        except ImportError:
            click.echo(f"  ⚠️  {description} - Not installed (optional)")

    # Check FalkorDB connection
    click.echo("\n🗄️  Database Connectivity:")
    try:
        host = os.environ.get('FALKORDB_HOST', 'localhost')
        port = int(os.environ.get('FALKORDB_PORT', '6379'))

        manager = FalkorDBManager(host=host, port=port)
        if manager.connect():
            click.echo(f"  ✅ FalkorDB connection successful ({host}:{port})")
            manager.close()
        else:
            click.echo(f"  ❌ Cannot connect to FalkorDB at {host}:{port}")
            all_ok = False
    except Exception as e:
        click.echo(f"  ❌ FalkorDB connection failed: {e}")
        all_ok = False

    # Check Ollama if configured
    click.echo("\n🤖 Ollama Server (for MiniRAG):")
    ollama_host = os.environ.get('OLLAMA_HOST', 'localhost')
    ollama_port = os.environ.get('OLLAMA_PORT', '11434')

    try:
        import requests
        response = requests.get(f"http://{ollama_host}:{ollama_port}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            click.echo(f"  ✅ Ollama server accessible ({ollama_host}:{ollama_port})")
            if verbose and models:
                click.echo(f"     Available models: {', '.join([m['name'] for m in models[:5]])}")
        else:
            click.echo(f"  ⚠️  Ollama server returned status {response.status_code}")
    except:
        click.echo(f"  ⚠️  Ollama server not accessible at {ollama_host}:{ollama_port} (optional)")

    # Check environment variables
    click.echo("\n🔧 Environment Variables:")
    env_vars = {
        'FALKORDB_HOST': 'FalkorDB host',
        'FALKORDB_PORT': 'FalkorDB port',
        'FALKORDB_PASSWORD': 'FalkorDB password',
        'OLLAMA_HOST': 'Ollama host',
        'OLLAMA_PORT': 'Ollama port',
        'KG_MODEL': 'Default KG model',
        'KG_EPOCHS': 'Default training epochs'
    }

    for var, description in env_vars.items():
        value = os.environ.get(var)
        if value:
            if 'PASSWORD' in var:
                click.echo(f"  ✅ {var} (set)")
            else:
                click.echo(f"  ✅ {var} = {value}")
        else:
            if var in ['FALKORDB_HOST', 'FALKORDB_PORT']:
                click.echo(f"  ⚠️  {var} not set (using defaults)")
            else:
                click.echo(f"  ⚠️  {var} not set (optional)")

    # Summary
    click.echo("\n" + "="*50)
    if all_ok:
        click.echo("✅ All required components are installed and configured!")
        click.echo("   You can start using Knowledge Graph features.")
    else:
        click.echo("❌ Some requirements are missing.")
        click.echo("\nTo install missing packages:")
        click.echo("  pip install falkordb graphiti-core pykeen torch minirag-hku")
        click.echo("\nTo install optional packages:")
        click.echo("  pip install matplotlib plotly scikit-learn")

    sys.exit(0 if all_ok else 1)


@kg_cli.command(name='init')
@click.option('--falkordb-host', default=None, envvar='FALKORDB_HOST',
              help='FalkorDB host (default: localhost)')
@click.option('--falkordb-port', default=None, type=int, envvar='FALKORDB_PORT',
              help='FalkorDB port (default: 6379)')
@click.option('--graph-name', default='netintel_kg',
              help='Graph database name')
@click.option('--password', default=None, envvar='FALKORDB_PASSWORD',
              help='FalkorDB password (optional)')
def init_kg(falkordb_host, falkordb_port, graph_name, password):
    """Initialize FalkorDB indices and schema for Knowledge Graph"""
    
    click.echo("🚀 Initializing Knowledge Graph system...")
    
    # Initialize FalkorDB manager
    manager = FalkorDBManager(
        host=falkordb_host,
        port=falkordb_port,
        password=password,
        graph_name=graph_name
    )
    
    # Connect to FalkorDB
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        click.echo(f"   Please ensure FalkorDB is running at {manager.host}:{manager.port}", err=True)
        sys.exit(1)
    
    click.echo(f"✅ Connected to FalkorDB at {manager.host}:{manager.port}")
    
    # Create indices
    async def create_indices():
        await manager.create_indices()
    
    try:
        asyncio.run(create_indices())
        click.echo("✅ Graph indices created successfully")
    except Exception as e:
        click.echo(f"❌ Failed to create indices: {e}", err=True)
        sys.exit(1)
    
    # Get initial statistics
    stats = manager.get_graph_statistics()
    click.echo("\n📊 Graph Statistics:")
    click.echo(f"   • Total nodes: {stats.get('total_nodes', 0)}")
    click.echo(f"   • Total edges: {stats.get('total_edges', 0)}")
    click.echo(f"   • Node types: {len(stats.get('node_counts', {}))}")
    
    manager.close()
    click.echo("\n✨ Knowledge Graph system initialized successfully!")


@kg_cli.command(name='stats')
@click.option('--falkordb-host', default=None, envvar='FALKORDB_HOST',
              help='FalkorDB host')
@click.option('--falkordb-port', default=None, type=int, envvar='FALKORDB_PORT',
              help='FalkorDB port')
@click.option('--format', 'output_format', 
              type=click.Choice(['json', 'table', 'summary']),
              default='summary',
              help='Output format')
def kg_stats(falkordb_host, falkordb_port, output_format):
    """Display Knowledge Graph statistics"""
    
    manager = FalkorDBManager(host=falkordb_host, port=falkordb_port)
    
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    stats = manager.get_graph_statistics()
    
    if output_format == 'json':
        click.echo(json.dumps(stats, indent=2))
    elif output_format == 'table':
        click.echo("\n📊 Knowledge Graph Statistics")
        click.echo("=" * 50)
        click.echo(f"Total Nodes: {stats['total_nodes']}")
        click.echo(f"Total Edges: {stats['total_edges']}")
        click.echo(f"Nodes with Embeddings: {stats.get('nodes_with_embeddings', 0)}")
        click.echo("\nNode Types:")
        for node_type, count in stats.get('node_counts', {}).items():
            click.echo(f"  • {node_type}: {count}")
        click.echo("\nEdge Types:")
        for edge_type, count in stats.get('edge_counts', {}).items():
            click.echo(f"  • {edge_type}: {count}")
    else:  # summary
        click.echo(f"📊 Graph: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
        if stats.get('nodes_with_embeddings', 0) > 0:
            click.echo(f"🔮 Embeddings: {stats['nodes_with_embeddings']} nodes with KG embeddings")
    
    manager.close()


@kg_cli.command(name='process')
@click.argument('document_path', type=click.Path(exists=True))
@click.option('--enable-kg/--no-kg', default=True,
              help='Enable knowledge graph generation')
@click.option('--enable-vector/--no-vector', default=True,
              help='Enable vector generation')
@click.option('--kg-model', default='RotatE',
              type=click.Choice(['TransE', 'RotatE', 'ComplEx', 'DistMult']),
              help='PyKEEN model for KG embeddings (Phase 2)')
def process_with_kg(document_path, enable_kg, enable_vector, kg_model):
    """Process document with Knowledge Graph generation"""
    
    click.echo(f"📄 Processing: {document_path}")
    click.echo(f"   • Knowledge Graph: {'✅ Enabled' if enable_kg else '❌ Disabled'}")
    click.echo(f"   • Vector Generation: {'✅ Enabled' if enable_vector else '❌ Disabled'}")
    
    if enable_kg:
        click.echo(f"   • KG Model: {kg_model} (Phase 2 - not yet implemented)")
    
    # Initialize hybrid system
    hybrid = HybridSystem(enable_kg=enable_kg)
    
    if enable_kg and not hybrid.enable_kg:
        click.echo("⚠️  Knowledge Graph disabled due to initialization failure", err=True)
    
    # Process document
    async def process():
        results = await hybrid.process_document(
            document_path,
            enable_vector=enable_vector,
            kg_config={'model': kg_model}
        )
        return results
    
    try:
        results = asyncio.run(process())
        
        if results['status'] == 'completed':
            click.echo("\n✅ Processing completed successfully!")
            
            if 'kg_results' in results:
                kg_res = results['kg_results']
                total_nodes = sum(len(g) for g in kg_res.get('network_graphs', []))
                total_entities = sum(len(e) for e in kg_res.get('text_entities', []))
                click.echo(f"   • Graph nodes created: {total_nodes}")
                click.echo(f"   • Text entities extracted: {total_entities}")
        else:
            click.echo(f"\n❌ Processing failed: {results.get('error', 'Unknown error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        hybrid.close()


@kg_cli.command(name='query')
@click.argument('cypher_query')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'table', 'csv']),
              default='table',
              help='Output format')
def execute_cypher(cypher_query, output_format):
    """Execute a Cypher query on the Knowledge Graph"""
    
    manager = FalkorDBManager()
    
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        result = manager.execute_cypher(cypher_query)
        
        if output_format == 'json':
            # Convert result to JSON-serializable format
            output = []
            for row in result.result_set:
                output.append([str(item) for item in row])
            click.echo(json.dumps(output, indent=2))
        elif output_format == 'csv':
            # Output as CSV
            for row in result.result_set:
                click.echo(','.join(str(item) for item in row))
        else:  # table
            # Output as table
            for row in result.result_set:
                click.echo(' | '.join(str(item) for item in row))
                
    except Exception as e:
        click.echo(f"❌ Query failed: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='train-embeddings')
@click.option('--model', default='RotatE',
              type=click.Choice(['TransE', 'RotatE', 'ComplEx', 'DistMult', 
                               'ConvE', 'TuckER', 'HolE', 'RESCAL']),
              help='PyKEEN model to use')
@click.option('--epochs', default=100, type=int,
              help='Number of training epochs')
@click.option('--batch-size', default=256, type=int,
              help='Training batch size')
@click.option('--embedding-dim', default=200, type=int,
              help='Dimension of embeddings')
@click.option('--learning-rate', default=0.001, type=float,
              help='Learning rate')
@click.option('--validation-split', default=0.1, type=float,
              help='Validation split fraction')
@click.option('--force', is_flag=True,
              help='Force retrain even if embeddings exist')
@click.option('--save-model/--no-save-model', default=True,
              help='Save trained model to disk')
@click.option('--model-path', type=click.Path(),
              help='Path to save/load model')
@click.option('--device', type=click.Choice(['cpu', 'cuda', 'auto']),
              default='auto',
              help='Device for training')
def train_embeddings(model, epochs, batch_size, embedding_dim, learning_rate,
                    validation_split, force, save_model, model_path, device):
    """Train or retrain KG embeddings using PyKEEN"""
    
    click.echo(f"🧠 Training KG embeddings with {model}")
    click.echo(f"   • Embedding dimension: {embedding_dim}")
    click.echo(f"   • Epochs: {epochs}")
    click.echo(f"   • Batch size: {batch_size}")
    click.echo(f"   • Learning rate: {learning_rate}")
    click.echo(f"   • Device: {device}")
    
    # Connect to FalkorDB
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    # Check if embeddings already exist
    stats = manager.get_graph_statistics()
    if stats.get('nodes_with_embeddings', 0) > 0 and not force:
        click.echo(f"⚠️  {stats['nodes_with_embeddings']} nodes already have embeddings")
        click.echo("   Use --force to retrain")
        if not click.confirm("Continue with retraining?"):
            manager.close()
            return
    
    # Check if graph has sufficient data
    if stats['total_nodes'] < 10 or stats['total_edges'] < 10:
        click.echo("❌ Insufficient graph data for training", err=True)
        click.echo(f"   Current: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
        click.echo("   Required: At least 10 nodes and 10 edges")
        manager.close()
        sys.exit(1)
    
    # Initialize trainer
    trainer = KGEmbeddingTrainer(
        model_name=model,
        embedding_dim=embedding_dim,
        device=device if device != 'auto' else None
    )
    
    # Train embeddings
    async def train():
        results = await trainer.train_embeddings(
            falkor_manager=manager,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            validation_split=validation_split,
            save_model=save_model,
            model_path=model_path
        )
        return results
    
    try:
        click.echo("\n🔄 Training started...")
        with click.progressbar(length=epochs, label='Training progress') as bar:
            # Note: In production, we'd update the progress bar during training
            results = asyncio.run(train())
            bar.update(epochs)
        
        if results['status'] == 'success':
            click.echo("\n✅ Training completed successfully!")
            click.echo(f"   • Entities with embeddings: {results['num_entities']}")
            click.echo(f"   • Relations with embeddings: {results['num_relations']}")
            click.echo(f"   • Embeddings stored: {results['embeddings_stored']}")
            
            # Display metrics if available
            if 'metrics' in results and results['metrics']:
                click.echo("\n📊 Training Metrics:")
                for metric, value in results['metrics'].items():
                    if value is not None:
                        click.echo(f"   • {metric}: {value:.4f}")
            
            if results.get('model_path'):
                click.echo(f"\n💾 Model saved to: {results['model_path']}")
                
        elif results['status'] == 'insufficient_data':
            click.echo(f"\n⚠️  Insufficient data: Only {results['num_triples']} triples found")
        else:
            click.echo(f"\n❌ Training failed: {results.get('error', 'Unknown error')}", err=True)
            
    except Exception as e:
        click.echo(f"❌ Training error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='similarity')
@click.argument('entity1')
@click.argument('entity2')
@click.option('--model-path', type=click.Path(exists=True),
              help='Path to saved model')
def compute_similarity(entity1, entity2, model_path):
    """Compute similarity between two entities using KG embeddings"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Get embeddings from FalkorDB
        query = """
        MATCH (e1 {id: $entity1})
        MATCH (e2 {id: $entity2})
        RETURN e1.kg_embedding as emb1, e2.kg_embedding as emb2,
               e1.name as name1, e2.name as name2
        """
        
        result = manager.execute_cypher(query, {
            'entity1': entity1,
            'entity2': entity2
        })
        
        if not result.result_set:
            click.echo(f"❌ Entities not found or don't have embeddings", err=True)
            sys.exit(1)
        
        row = result.result_set[0]
        emb1 = row[0]
        emb2 = row[1]
        name1 = row[2] or entity1
        name2 = row[3] or entity2
        
        if emb1 is None or emb2 is None:
            click.echo("❌ One or both entities don't have embeddings", err=True)
            click.echo("   Run 'kg train-embeddings' first")
            sys.exit(1)
        
        # Compute cosine similarity
        import numpy as np
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        
        click.echo(f"📊 Similarity Analysis:")
        click.echo(f"   • Entity 1: {name1} ({entity1})")
        click.echo(f"   • Entity 2: {name2} ({entity2})")
        click.echo(f"   • Cosine Similarity: {similarity:.4f}")
        
        # Interpret similarity
        if similarity > 0.8:
            click.echo("   • Interpretation: Very similar")
        elif similarity > 0.6:
            click.echo("   • Interpretation: Moderately similar")
        elif similarity > 0.4:
            click.echo("   • Interpretation: Somewhat similar")
        else:
            click.echo("   • Interpretation: Not very similar")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='find-similar')
@click.argument('entity')
@click.option('--limit', default=10, type=int,
              help='Number of similar entities to find')
@click.option('--threshold', default=0.5, type=float,
              help='Minimum similarity threshold')
def find_similar_entities(entity, limit, threshold):
    """Find entities similar to the given entity using KG embeddings"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Get the entity's embedding
        query = """
        MATCH (e {id: $entity})
        RETURN e.kg_embedding as embedding, e.name as name
        """
        
        result = manager.execute_cypher(query, {'entity': entity})
        
        if not result.result_set or result.result_set[0][0] is None:
            click.echo(f"❌ Entity '{entity}' not found or doesn't have embeddings", err=True)
            sys.exit(1)
        
        embedding = result.result_set[0][0]
        entity_name = result.result_set[0][1] or entity
        
        # Find similar entities
        async def search():
            return await manager.similarity_search_with_embeddings(
                query_embedding=embedding,
                limit=limit + 1,  # +1 because it will include the query entity
                threshold=threshold
            )

        similar = asyncio.run(search())
        
        # Filter out the query entity itself
        similar = [s for s in similar if s['id'] != entity][:limit]
        
        if not similar:
            click.echo(f"No similar entities found with threshold {threshold}")
        else:
            click.echo(f"🔍 Entities similar to '{entity_name}' ({entity}):")
            click.echo(f"   Threshold: {threshold}, Limit: {limit}\n")
            
            for i, sim in enumerate(similar, 1):
                click.echo(f"   {i}. {sim['name']} ({sim['id']})")
                click.echo(f"      Type: {sim['type']}")
                click.echo(f"      Similarity: {sim['similarity']:.4f}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='visualize')
@click.option('--output', '-o', type=click.Path(),
              help='Output file path for visualization')
@click.option('--method', type=click.Choice(['tsne', 'pca']),
              default='tsne',
              help='Dimensionality reduction method')
@click.option('--dimensions', type=click.Choice(['2d', '3d']),
              default='2d',
              help='Number of dimensions for visualization')
@click.option('--show-labels/--no-labels', default=False,
              help='Show entity labels (only for small graphs)')
@click.option('--color-by-type/--no-color', default=True,
              help='Color entities by type')
def visualize_embeddings(output, method, dimensions, show_labels, color_by_type):
    """Visualize KG embeddings in 2D or 3D space"""
    
    click.echo(f"📊 Visualizing KG embeddings...")
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Load embeddings from FalkorDB
        embeddings, entity_types = load_embeddings_from_falkordb(manager)
        
        if not embeddings:
            click.echo("❌ No embeddings found in graph", err=True)
            click.echo("   Run 'kg train-embeddings' first")
            sys.exit(1)
        
        click.echo(f"   • Loaded {len(embeddings)} embeddings")
        click.echo(f"   • Method: {method.upper()}")
        click.echo(f"   • Dimensions: {dimensions}")
        
        # Create analyzer
        analyzer = EmbeddingAnalyzer(embeddings, entity_types)
        
        # Generate visualization
        if dimensions == '2d':
            analyzer.visualize_embeddings(
                save_path=output,
                method=method,
                show_labels=show_labels,
                color_by_type=color_by_type
            )
        else:  # 3d
            analyzer.visualize_3d_embeddings(
                save_path=output,
                method=method
            )
        
        if output:
            click.echo(f"✅ Visualization saved to {output}")
        else:
            click.echo("✅ Visualization displayed")
            
    except Exception as e:
        click.echo(f"❌ Visualization failed: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='embedding-stats')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'table']),
              default='table',
              help='Output format')
def embedding_statistics(output_format):
    """Display statistics about KG embeddings"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Load embeddings
        embeddings, entity_types = load_embeddings_from_falkordb(manager)
        
        if not embeddings:
            click.echo("❌ No embeddings found", err=True)
            sys.exit(1)
        
        # Create analyzer and compute stats
        analyzer = EmbeddingAnalyzer(embeddings, entity_types)
        stats = analyzer.compute_embedding_statistics()
        
        if output_format == 'json':
            click.echo(json.dumps(stats, indent=2))
        else:  # table
            click.echo("\n📊 Embedding Statistics")
            click.echo("=" * 50)
            click.echo(f"Number of embeddings: {stats['num_embeddings']}")
            click.echo(f"Embedding dimension: {stats['embedding_dim']}")
            click.echo(f"\nNorm Statistics:")
            click.echo(f"  • Mean: {stats['mean_norm']:.4f}")
            click.echo(f"  • Std: {stats['std_norm']:.4f}")
            click.echo(f"  • Min: {stats['min_norm']:.4f}")
            click.echo(f"  • Max: {stats['max_norm']:.4f}")
            
            if 'mean_distance' in stats:
                click.echo(f"\nDistance Statistics:")
                click.echo(f"  • Mean: {stats['mean_distance']:.4f}")
                click.echo(f"  • Std: {stats['std_distance']:.4f}")
                click.echo(f"  • Min: {stats['min_distance']:.4f}")
                click.echo(f"  • Max: {stats['max_distance']:.4f}")
            
            if 'type_distribution' in stats:
                click.echo(f"\nEntity Type Distribution:")
                for entity_type, count in stats['type_distribution'].items():
                    click.echo(f"  • {entity_type}: {count}")
                    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='cluster')
@click.option('--n-clusters', default=5, type=int,
              help='Number of clusters')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for cluster assignments')
def cluster_embeddings(n_clusters, output):
    """Cluster entities based on their KG embeddings"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Load embeddings
        embeddings, entity_types = load_embeddings_from_falkordb(manager)
        
        if not embeddings:
            click.echo("❌ No embeddings found", err=True)
            sys.exit(1)
        
        click.echo(f"🔍 Clustering {len(embeddings)} entities into {n_clusters} clusters...")
        
        # Perform clustering
        analyzer = EmbeddingAnalyzer(embeddings, entity_types)
        cluster_assignments = analyzer.cluster_embeddings(n_clusters=n_clusters)
        
        # Display results
        cluster_counts = {}
        for cluster_id in cluster_assignments.values():
            cluster_counts[cluster_id] = cluster_counts.get(cluster_id, 0) + 1
        
        click.echo("\n📊 Clustering Results:")
        for cluster_id in sorted(cluster_counts.keys()):
            click.echo(f"   • Cluster {cluster_id}: {cluster_counts[cluster_id]} entities")
        
        # Save if requested
        if output:
            with open(output, 'w') as f:
                json.dump(cluster_assignments, f, indent=2)
            click.echo(f"\n✅ Cluster assignments saved to {output}")
        
        # Show sample entities from each cluster
        click.echo("\n📝 Sample entities per cluster:")
        for cluster_id in sorted(cluster_counts.keys()):
            entities_in_cluster = [e for e, c in cluster_assignments.items() if c == cluster_id][:3]
            click.echo(f"   Cluster {cluster_id}: {', '.join(entities_in_cluster)}")
            
    except Exception as e:
        click.echo(f"❌ Clustering failed: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='rag-query')
@click.argument('query_text')
@click.option('--mode', type=click.Choice(['minirag_only', 'kg_embedding_only', 'hybrid']),
              default='hybrid',
              help='Query mode')
@click.option('--limit', default=10, type=int,
              help='Maximum number of results')
@click.option('--llm-model', envvar='MINIRAG_LLM',
              help='LLM model for MiniRAG')
@click.option('--embedding-model', envvar='MINIRAG_EMBEDDING',
              help='Embedding model for MiniRAG')
@click.option('--explain/--no-explain', default=True,
              help='Include explanations for results')
def rag_query(query_text, mode, limit, llm_model, embedding_model, explain):
    """Query using Enhanced MiniRAG with KG embeddings"""
    
    click.echo(f"🔍 Querying with Enhanced MiniRAG")
    click.echo(f"   • Query: {query_text}")
    click.echo(f"   • Mode: {mode}")
    click.echo(f"   • Limit: {limit}")
    
    # Connect to FalkorDB
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Initialize Enhanced MiniRAG
        minirag = EnhancedMiniRAG(
            falkor_manager=manager,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        # Execute query
        async def run_query():
            results = await minirag.query_with_kg_embeddings(
                query_text=query_text,
                mode=mode,
                max_results=limit
            )
            return results
        
        click.echo("\n⏳ Processing query...")
        results = asyncio.run(run_query())
        
        if 'error' in results:
            click.echo(f"❌ Query failed: {results['error']}", err=True)
            sys.exit(1)
        
        # Display results
        click.echo(f"\n✅ Found {len(results['results'])} results")
        click.echo(f"   Strategy: {results['metadata'].get('strategy', 'unknown')}")
        click.echo("\n" + "=" * 60)
        
        for i, result in enumerate(results['results'], 1):
            click.echo(f"\n📍 Result {i}:")
            
            # Display entity info
            if 'entity' in result:
                click.echo(f"   Entity: {result['entity']}")
            
            # Display match type and score
            if 'match_type' in result:
                click.echo(f"   Match Type: {result['match_type']}")
            if 'score' in result:
                click.echo(f"   Score: {result['score']:.4f}")
            elif 'similarity_score' in result:
                click.echo(f"   Similarity: {result['similarity_score']:.4f}")
            elif 'importance_score' in result:
                click.echo(f"   Importance: {result['importance_score']:.4f}")
            
            # Display node data
            if 'node_data' in result and result['node_data']:
                node = result['node_data']
                click.echo(f"   Type: {', '.join(node.get('labels', ['Unknown']))}")
                if 'properties' in node:
                    props = node['properties']
                    if 'name' in props:
                        click.echo(f"   Name: {props['name']}")
                    if 'ip_address' in props:
                        click.echo(f"   IP: {props['ip_address']}")
            
            # Display context
            if 'context' in result:
                context = result['context']
                if 'neighbor_count' in context:
                    click.echo(f"   Connections: {context['neighbor_count']}")
            
            # Display content (for text results)
            if 'content' in result:
                content_preview = result['content'][:100] + '...' if len(result['content']) > 100 else result['content']
                click.echo(f"   Content: {content_preview}")
            
            # Display explanation if requested
            if explain:
                async def get_explanation():
                    return await minirag.explain_result(result)
                
                explanation = asyncio.run(get_explanation())
                click.echo(f"   📝 Explanation: {explanation}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='entity-context')
@click.argument('entity_id')
@click.option('--context-size', default=2, type=int,
              help='Hops for context extraction')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'summary']),
              default='summary',
              help='Output format')
@click.option('--llm-model', envvar='MINIRAG_LLM',
              help='LLM model for MiniRAG (e.g., ollama/gemma3:4b-it-qat)')
@click.option('--embedding-model', envvar='MINIRAG_EMBEDDING',
              help='Embedding model for MiniRAG (e.g., ollama/Qwen3-Embedding-8B)')
def entity_context(entity_id, context_size, output_format, llm_model, embedding_model):
    """Get rich context for an entity using MiniRAG"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Initialize Enhanced MiniRAG
        minirag = EnhancedMiniRAG(
            falkor_manager=manager,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        # Get entity context
        async def get_context():
            return await minirag.get_entity_context(entity_id, context_size)
        
        click.echo(f"📊 Getting context for entity: {entity_id}")
        context = asyncio.run(get_context())
        
        if output_format == 'json':
            # Remove embeddings for JSON output
            if 'node' in context and context['node']:
                if 'kg_embedding' in context['node'].get('properties', {}):
                    del context['node']['properties']['kg_embedding']
            click.echo(json.dumps(context, indent=2, default=str))
        else:  # summary
            click.echo(f"\n{'=' * 60}")
            
            # Display node info
            if context['node']:
                node = context['node']
                click.echo(f"📍 Entity: {entity_id}")
                click.echo(f"   Name: {node.get('name', 'N/A')}")
                click.echo(f"   Type: {', '.join(node.get('labels', ['Unknown']))}")
                
                if 'properties' in node:
                    props = node['properties']
                    if 'ip_address' in props:
                        click.echo(f"   IP: {props['ip_address']}")
                    if 'zone' in props:
                        click.echo(f"   Zone: {props['zone']}")
                    if 'status' in props:
                        click.echo(f"   Status: {props['status']}")
            else:
                click.echo(f"❌ Entity '{entity_id}' not found")
                sys.exit(1)
            
            # Display neighbors
            if context['neighbors']:
                click.echo(f"\n🔗 Connections ({len(context['neighbors'])} total):")
                for neighbor in context['neighbors'][:5]:  # Show first 5
                    click.echo(f"   • {neighbor['name']} ({neighbor['id']})")
                    click.echo(f"     Relationship: {neighbor['relationship']}")
            
            # Display subgraph statistics
            if context['subgraph']:
                subgraph = context['subgraph']
                click.echo(f"\n📈 Subgraph Statistics:")
                click.echo(f"   • Nodes: {len(subgraph['nodes'])}")
                click.echo(f"   • Edges: {len(subgraph['edges'])}")
            
            # Display embedding info
            if context['embeddings']:
                click.echo(f"\n🔮 Embeddings:")
                for emb_type, emb_info in context['embeddings'].items():
                    if emb_info.get('has_embedding'):
                        click.echo(f"   • {emb_type.upper()}: {emb_info['model']} ({emb_info['dim']}D)")
                        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='path-find')
@click.argument('source_id')
@click.argument('target_id')
@click.option('--max-length', default=5, type=int,
              help='Maximum path length')
def find_path(source_id, target_id, max_length):
    """Find paths between two entities"""
    
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        from .falkordb_storage import FalkorDBGraphStorage
        storage = FalkorDBGraphStorage(manager)
        
        # Find paths
        async def get_paths():
            return await storage.get_paths(source_id, target_id, max_length)
        
        click.echo(f"🔍 Finding paths from '{source_id}' to '{target_id}'")
        click.echo(f"   Max length: {max_length}")
        
        paths = asyncio.run(get_paths())
        
        if not paths:
            click.echo(f"\n❌ No paths found between '{source_id}' and '{target_id}'")
        else:
            click.echo(f"\n✅ Found {len(paths)} path(s):\n")
            
            for i, path in enumerate(paths, 1):
                click.echo(f"📍 Path {i} (length: {len([p for p in path if p['type'] == 'node'])})")
                
                path_str = []
                for element in path:
                    if element['type'] == 'node':
                        name = element.get('name', element['id'])
                        path_str.append(f"[{name}]")
                    elif element['type'] == 'edge':
                        path_str.append(f"-{element['rel_type']}-")
                
                # Join path elements
                path_display = ''.join(path_str)
                click.echo(f"   {path_display}")
                click.echo()
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='classify-query')
@click.argument('query_text')
@click.option('--verbose', is_flag=True,
              help='Show detailed classification scores')
def classify_query(query_text, verbose):
    """Classify query intent for optimal retrieval strategy"""
    
    classifier = QueryIntentClassifier()
    
    # Get classification with confidence
    query_type, confidence = classifier.classify_with_confidence(query_text)
    
    # Get query features
    features = classifier.get_query_features(query_text)
    
    click.echo(f"\n🔍 Query Classification")
    click.echo("=" * 60)
    click.echo(f"Query: {query_text}")
    click.echo(f"\n📊 Classification Results:")
    click.echo(f"   • Type: {query_type.value}")
    click.echo(f"   • Confidence: {confidence:.2%}")
    click.echo(f"   • Recommended Strategy: {features['recommended_strategy']}")
    
    if features['entities']:
        click.echo(f"\n🔖 Extracted Entities:")
        for entity in features['entities']:
            click.echo(f"   • {entity}")
    
    if features['relationships']:
        click.echo(f"\n🔗 Extracted Relationships:")
        for rel in features['relationships']:
            click.echo(f"   • {rel}")
    
    if verbose:
        click.echo(f"\n📈 Query Features:")
        click.echo(f"   • Query Length: {features['query_length']} words")
        click.echo(f"   • Has Path Query: {features['has_path_query']}")
        click.echo(f"   • Has Similarity Query: {features['has_similarity_query']}")
        click.echo(f"   • Has Aggregation: {features['has_aggregation']}")
        click.echo(f"   • Is Question: {features['has_question']}")


@kg_cli.command(name='hybrid-search')
@click.argument('query_text')
@click.option('--strategy', 
              type=click.Choice(['vector_first', 'graph_first', 'parallel', 'adaptive']),
              default='adaptive',
              help='Retrieval strategy')
@click.option('--limit', default=10, type=int,
              help='Maximum number of results')
@click.option('--rerank', 
              type=click.Choice(['score_based', 'diversity', 'relevance']),
              default='score_based',
              help='Reranking method')
@click.option('--explain/--no-explain', default=True,
              help='Include retrieval explanations')
@click.option('--stats/--no-stats', default=False,
              help='Show retrieval statistics')
@click.option('--llm-model', envvar='MINIRAG_LLM',
              help='LLM model for retriever (e.g., ollama/gemma3:4b-it-qat)')
@click.option('--embedding-model', envvar='MINIRAG_EMBEDDING',
              help='Embedding model for retriever (e.g., ollama/Qwen3-Embedding-8B)')
def hybrid_search(query_text, strategy, limit, rerank, explain, stats, llm_model, embedding_model):
    """Perform hybrid search with advanced retrieval strategies"""
    
    click.echo(f"🔍 Hybrid Search")
    click.echo(f"   • Query: {query_text}")
    click.echo(f"   • Strategy: {strategy}")
    click.echo(f"   • Limit: {limit}")
    
    # Connect to FalkorDB
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        # Initialize Hybrid Retriever
        retriever = HybridRetriever(
            falkor_manager=manager,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        # Perform hybrid search
        async def search():
            results = await retriever.hybrid_search(
                query=query_text,
                strategy=strategy,
                max_results=limit
            )
            
            # Rerank if requested
            if rerank != 'score_based':
                results['results'] = await retriever.rerank_results(
                    results['results'],
                    query_text,
                    method=rerank
                )
            
            return results
        
        click.echo("\n⏳ Searching...")
        search_results = asyncio.run(search())
        
        if 'error' in search_results:
            click.echo(f"❌ Search failed: {search_results['error']}", err=True)
            sys.exit(1)
        
        # Display metadata
        metadata = search_results['metadata']
        click.echo(f"\n✅ Search completed in {metadata['processing_time']:.2f}s")
        click.echo(f"   • Strategy Used: {metadata['strategy_used']}")
        click.echo(f"   • Query Type: {metadata['query_type']}")
        click.echo(f"   • Confidence: {metadata['confidence']:.2%}")
        click.echo(f"   • Results Found: {metadata['num_results']}")
        
        # Display results
        click.echo("\n" + "=" * 60)
        click.echo("Search Results:")
        click.echo("=" * 60)
        
        for i, result in enumerate(search_results['results'], 1):
            click.echo(f"\n📍 Result {i}:")
            
            # Basic info
            if 'entity' in result:
                click.echo(f"   Entity: {result['entity']}")
            
            # Scores
            if 'final_score' in result:
                click.echo(f"   Score: {result['final_score']:.3f}")
            if 'rrf_score' in result:
                click.echo(f"   RRF Score: {result['rrf_score']:.3f}")
            
            # Method and sources
            if 'retrieval_method' in result:
                click.echo(f"   Method: {result['retrieval_method']}")
            if 'sources' in result:
                click.echo(f"   Sources: {result['sources']}")
            
            # Node details
            if 'node_data' in result:
                node = result['node_data']
                if 'type' in node:
                    click.echo(f"   Type: {node['type']}")
                if 'properties' in node:
                    props = node['properties']
                    if 'name' in props:
                        click.echo(f"   Name: {props['name']}")
                    if 'ip_address' in props:
                        click.echo(f"   IP: {props['ip_address']}")
            
            # Explanation
            if explain:
                async def get_explanation():
                    return await retriever.explain_retrieval(result, query_text)
                
                explanation = asyncio.run(get_explanation())
                click.echo(f"   📝 {explanation}")
        
        # Display statistics if requested
        if stats:
            async def get_stats():
                return await retriever.get_retrieval_statistics(search_results['results'])
            
            statistics = asyncio.run(get_stats())
            
            click.echo("\n" + "=" * 60)
            click.echo("Retrieval Statistics:")
            click.echo("=" * 60)
            click.echo(f"Total Results: {statistics['total_results']}")
            
            click.echo("\nBy Retrieval Method:")
            for method, count in statistics['by_method'].items():
                click.echo(f"   • {method}: {count}")
            
            click.echo("\nBy Entity Type:")
            for entity_type, count in statistics['by_type'].items():
                click.echo(f"   • {entity_type}: {count}")
            
            click.echo("\nScore Distribution:")
            score_dist = statistics['score_distribution']
            click.echo(f"   • Min: {score_dist['min']:.3f}")
            click.echo(f"   • Max: {score_dist['max']:.3f}")
            click.echo(f"   • Mean: {score_dist['mean']:.3f}")
            click.echo(f"   • Std: {score_dist['std']:.3f}")
            
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='compare-strategies')
@click.argument('query_text')
@click.option('--limit', default=5, type=int,
              help='Results per strategy')
@click.option('--llm-model', envvar='MINIRAG_LLM',
              help='LLM model for retriever (e.g., ollama/gemma3:4b-it-qat)')
@click.option('--embedding-model', envvar='MINIRAG_EMBEDDING',
              help='Embedding model for retriever (e.g., ollama/Qwen3-Embedding-8B)')
def compare_strategies(query_text, limit, llm_model, embedding_model):
    """Compare different retrieval strategies for a query"""
    
    click.echo(f"🔬 Strategy Comparison")
    click.echo(f"   Query: {query_text}")
    click.echo(f"   Limit: {limit} results per strategy")
    
    # Connect to FalkorDB
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        retriever = HybridRetriever(
            falkor_manager=manager,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        
        strategies = ['vector_first', 'graph_first', 'parallel']
        all_results = {}
        
        click.echo("\n⏳ Running comparisons...")
        
        for strategy in strategies:
            async def search():
                return await retriever.hybrid_search(
                    query=query_text,
                    strategy=strategy,
                    max_results=limit
                )
            
            all_results[strategy] = asyncio.run(search())
        
        # Display comparison
        click.echo("\n" + "=" * 80)
        click.echo("Strategy Comparison Results:")
        click.echo("=" * 80)
        
        for strategy in strategies:
            results = all_results[strategy]
            metadata = results['metadata']
            
            click.echo(f"\n📊 {strategy.upper()} Strategy:")
            click.echo(f"   • Processing Time: {metadata['processing_time']:.3f}s")
            click.echo(f"   • Results Found: {metadata['num_results']}")
            
            # Show top entities
            click.echo(f"   • Top Entities:")
            for i, result in enumerate(results['results'][:3], 1):
                entity = result.get('entity', 'Unknown')
                score = result.get('final_score', 0)
                click.echo(f"      {i}. {entity} (score: {score:.3f})")
        
        # Find overlapping results
        click.echo("\n🔄 Result Overlap:")
        
        # Extract entity sets
        entity_sets = {}
        for strategy in strategies:
            entities = set()
            for result in all_results[strategy]['results']:
                if 'entity' in result:
                    entities.add(result['entity'])
            entity_sets[strategy] = entities
        
        # Calculate overlaps
        for i, strat1 in enumerate(strategies):
            for strat2 in strategies[i+1:]:
                overlap = entity_sets[strat1] & entity_sets[strat2]
                if overlap:
                    click.echo(f"   • {strat1} ∩ {strat2}: {len(overlap)} entities")
                    for entity in list(overlap)[:3]:
                        click.echo(f"      - {entity}")
        
        # Find unique results
        click.echo("\n🎯 Unique Results by Strategy:")
        for strategy in strategies:
            unique = entity_sets[strategy]
            for other in strategies:
                if other != strategy:
                    unique = unique - entity_sets[other]
            
            if unique:
                click.echo(f"   • {strategy}: {len(unique)} unique entities")
                for entity in list(unique)[:3]:
                    click.echo(f"      - {entity}")
                    
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='batch-query')
@click.argument('queries_file', type=click.Path(exists=True))
@click.option('--strategy', default='adaptive',
              help='Retrieval strategy')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for results')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'csv']),
              default='json',
              help='Output format')
@click.option('--llm-model', envvar='MINIRAG_LLM',
              help='LLM model for retriever (e.g., ollama/gemma3:4b-it-qat)')
@click.option('--embedding-model', envvar='MINIRAG_EMBEDDING',
              help='Embedding model for retriever (e.g., ollama/Qwen3-Embedding-8B)')
def batch_query(queries_file, strategy, output, output_format, llm_model, embedding_model):
    """Process batch queries from file"""
    
    # Read queries
    with open(queries_file, 'r') as f:
        queries = [line.strip() for line in f if line.strip()]
    
    click.echo(f"📋 Batch Query Processing")
    click.echo(f"   • Queries: {len(queries)}")
    click.echo(f"   • Strategy: {strategy}")
    
    # Connect to FalkorDB
    manager = FalkorDBManager()
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        retriever = HybridRetriever(
            falkor_manager=manager,
            llm_model=llm_model,
            embedding_model=embedding_model
        )
        all_results = []
        
        with click.progressbar(queries, label='Processing queries') as bar:
            for query in bar:
                async def search():
                    return await retriever.hybrid_search(
                        query=query,
                        strategy=strategy,
                        max_results=5
                    )
                
                result = asyncio.run(search())
                all_results.append({
                    'query': query,
                    'num_results': len(result.get('results', [])),
                    'query_type': result['query_features']['query_type'],
                    'top_results': [
                        {
                            'entity': r.get('entity'),
                            'score': r.get('final_score', 0)
                        }
                        for r in result.get('results', [])[:3]
                    ]
                })
        
        # Save or display results
        if output:
            if output_format == 'json':
                with open(output, 'w') as f:
                    json.dump(all_results, f, indent=2)
            else:  # csv
                import csv
                with open(output, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Query', 'Query Type', 'Num Results', 'Top Entity', 'Top Score'])
                    for result in all_results:
                        top = result['top_results'][0] if result['top_results'] else {}
                        writer.writerow([
                            result['query'],
                            result['query_type'],
                            result['num_results'],
                            top.get('entity', ''),
                            top.get('score', 0)
                        ])
            
            click.echo(f"\n✅ Results saved to {output}")
        else:
            # Display summary
            click.echo("\n📊 Batch Results Summary:")
            total_queries = len(all_results)
            total_results = sum(r['num_results'] for r in all_results)
            
            click.echo(f"   • Total Queries: {total_queries}")
            click.echo(f"   • Total Results: {total_results}")
            click.echo(f"   • Avg Results/Query: {total_results/total_queries:.1f}")
            
            # Query type distribution
            type_counts = {}
            for r in all_results:
                qt = r['query_type']
                type_counts[qt] = type_counts.get(qt, 0) + 1
            
            click.echo("\n   Query Type Distribution:")
            for qt, count in type_counts.items():
                click.echo(f"      • {qt}: {count}")
                
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


@kg_cli.command(name='export')
@click.option('--format', 'export_format',
              type=click.Choice(['cypher', 'graphml', 'json']),
              default='cypher',
              help='Export format')
@click.option('--output', '-o', type=click.Path(),
              required=True,
              help='Output file path')
@click.option('--include-embeddings', is_flag=True,
              help='Include KG embeddings in export')
def export_graph(export_format, output, include_embeddings):
    """Export Knowledge Graph to file"""
    
    click.echo(f"📤 Exporting graph to {output} (format: {export_format})")
    
    if include_embeddings:
        click.echo("   • Including KG embeddings")
    
    manager = FalkorDBManager()
    
    if not manager.connect():
        click.echo("❌ Failed to connect to FalkorDB", err=True)
        sys.exit(1)
    
    try:
        if export_format == 'cypher':
            # Export as Cypher CREATE statements
            query = """
            MATCH (n)
            RETURN 'CREATE (' + 
                   CASE WHEN n.id IS NOT NULL THEN ':' + labels(n)[0] + ' {id: "' + n.id + '"'
                   ELSE ':' + labels(n)[0] + ' {'
                   END +
                   CASE WHEN n.name IS NOT NULL THEN ', name: "' + n.name + '"' ELSE '' END +
                   '})' as cypher
            """
            result = manager.execute_cypher(query)
            
            with open(output, 'w') as f:
                for row in result.result_set:
                    f.write(row[0] + ';\n')
            
            # Export relationships
            rel_query = """
            MATCH (a)-[r]->(b)
            RETURN 'MATCH (a {id: "' + a.id + '"}), (b {id: "' + b.id + '"}) ' +
                   'CREATE (a)-[:' + type(r) + ']->(b)' as cypher
            """
            result = manager.execute_cypher(rel_query)
            
            with open(output, 'a') as f:
                f.write('\n// Relationships\n')
                for row in result.result_set:
                    f.write(row[0] + ';\n')
                    
        elif export_format == 'json':
            # Export as JSON
            nodes_query = "MATCH (n) RETURN n"
            edges_query = "MATCH (a)-[r]->(b) RETURN a.id, type(r), b.id, r"
            
            nodes_result = manager.execute_cypher(nodes_query)
            edges_result = manager.execute_cypher(edges_query)
            
            export_data = {
                'nodes': [],
                'edges': []
            }
            
            # Process nodes
            for row in nodes_result.result_set:
                node = row[0]
                node_data = {
                    'labels': node.labels,
                    'properties': node.properties
                }
                if not include_embeddings and 'kg_embedding' in node_data['properties']:
                    del node_data['properties']['kg_embedding']
                export_data['nodes'].append(node_data)
            
            # Process edges
            for row in edges_result.result_set:
                edge_data = {
                    'from': row[0],
                    'type': row[1],
                    'to': row[2],
                    'properties': row[3].properties if len(row) > 3 else {}
                }
                if not include_embeddings and 'kg_embedding' in edge_data['properties']:
                    del edge_data['properties']['kg_embedding']
                export_data['edges'].append(edge_data)
            
            with open(output, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
                
        else:  # graphml
            click.echo("⚠️  GraphML export not yet implemented", err=True)
            
        click.echo(f"✅ Graph exported to {output}")
        
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)
        sys.exit(1)
    finally:
        manager.close()


# Helper function to add KG commands to main CLI
def add_kg_commands(cli_group):
    """Add KG commands to the main CLI group."""
    cli_group.add_command(kg_cli)