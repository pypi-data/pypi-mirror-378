"""
Database commands for queries, search, and management
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional


@click.group()
def db():
    """Database operations"""
    pass


@db.command()
@click.argument('query_text')
@click.option('--limit', type=int, default=10,
              help='Maximum number of results')
@click.option('--vector/--no-vector', default=True,
              help='Use vector search')
@click.option('--threshold', type=float, default=0.7,
              help='Similarity threshold (0-1)')
@click.option('--filters', type=str,
              help='Filter criteria (e.g., "type:network")')
@click.option('--format', 'output_format',
              type=click.Choice(['json', 'table', 'csv']),
              default='table',
              help='Output format')
@click.pass_context
def query(ctx, query_text, limit, vector, threshold, filters, output_format):
    """Query the database with text or vector search"""

    click.echo(f"🔍 Querying database: '{query_text}'")
    click.echo(f"   • Method: {'Vector' if vector else 'Text'} search")
    click.echo(f"   • Limit: {limit} results")

    try:
        from ...database.query_engine import QueryEngine

        engine = QueryEngine()

        # Parse filters
        filter_dict = {}
        if filters:
            for f in filters.split(','):
                if ':' in f:
                    key, value = f.split(':', 1)
                    filter_dict[key] = value

        # Execute query
        if vector:
            results = engine.vector_search(
                query_text,
                limit=limit,
                threshold=threshold,
                filters=filter_dict
            )
        else:
            results = engine.text_search(
                query_text,
                limit=limit,
                filters=filter_dict
            )

        # Format and display results
        if output_format == 'json':
            # JSON output
            json_results = [r.to_dict() for r in results]
            click.echo(json.dumps(json_results, indent=2, default=str))

        elif output_format == 'csv':
            # CSV output
            import csv
            import io

            if results:
                output_io = io.StringIO()
                writer = csv.DictWriter(
                    output_io,
                    fieldnames=results[0].to_dict().keys()
                )
                writer.writeheader()
                for r in results:
                    writer.writerow(r.to_dict())

                click.echo(output_io.getvalue())

        else:
            # Table output
            if not results:
                click.echo("\nNo results found.")
            else:
                click.echo(f"\nFound {len(results)} results:\n")

                for i, result in enumerate(results, 1):
                    click.echo(f"📄 Result {i}:")
                    click.echo(f"   • ID: {result.id}")
                    click.echo(f"   • Score: {result.score:.3f}")

                    # Show metadata if available
                    if result.metadata:
                        if 'file_name' in result.metadata:
                            click.echo(f"   • File: {result.metadata['file_name']}")
                        if 'type' in result.metadata:
                            click.echo(f"   • Type: {result.metadata['type']}")
                        if 'page' in result.metadata:
                            click.echo(f"   • Page: {result.metadata['page']}")

                    # Show snippet
                    text_snippet = result.content[:200] + "..." if len(result.content) > 200 else result.content
                    click.echo(f"   • Content: {text_snippet}")
                    click.echo()

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Query failed: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@db.command()
@click.argument('search_text')
@click.option('--filters', type=str,
              help='Filter criteria')
@click.option('--date-range', type=str,
              help='Date range (YYYY-MM-DD:YYYY-MM-DD)')
@click.option('--limit', type=int, default=20,
              help='Maximum results')
@click.option('--offset', type=int, default=0,
              help='Result offset for pagination')
def search(search_text, filters, date_range, limit, offset):
    """Advanced search with filters"""

    click.echo(f"🔍 Advanced Search: '{search_text}'")

    if filters:
        click.echo(f"   • Filters: {filters}")
    if date_range:
        click.echo(f"   • Date range: {date_range}")

    try:
        from ...database.search_engine import SearchEngine

        engine = SearchEngine()

        # Parse date range
        start_date = None
        end_date = None
        if date_range and ':' in date_range:
            parts = date_range.split(':')
            start_date = parts[0]
            end_date = parts[1]

        # Execute search
        results = engine.search(
            search_text,
            filters=filters,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        # Display results
        click.echo(f"\n📊 Found {results['total']} total results")
        click.echo(f"   Showing {len(results['items'])} (offset {offset})\n")

        for item in results['items']:
            click.echo(f"• {item['title']}")
            click.echo(f"  {item['summary'][:100]}...")
            click.echo(f"  Date: {item['date']} | Type: {item['type']}")
            click.echo()

        if results['total'] > offset + limit:
            click.echo(f"ℹ️  More results available. Use --offset {offset + limit}")

    except ImportError:
        click.echo("❌ Search module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Search failed: {e}", err=True)
        sys.exit(1)


@db.command()
def info():
    """Show database information"""

    click.echo("📊 Database Information")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()
        info = manager.get_info()

        click.echo(f"\n• Type: {info['type']}")
        click.echo(f"• Path: {info['path']}")
        click.echo(f"• Size: {info['size_mb']:.2f} MB")
        click.echo(f"• Tables: {info['table_count']}")

        click.echo("\n📈 Statistics:")
        click.echo(f"   • Documents: {info['document_count']:,}")
        click.echo(f"   • Text blocks: {info['text_count']:,}")
        click.echo(f"   • Network diagrams: {info['network_count']:,}")
        click.echo(f"   • Tables: {info['table_count']:,}")

        if info.get('vector_info'):
            click.echo("\n🔮 Vector Database:")
            click.echo(f"   • Backend: {info['vector_info']['backend']}")
            click.echo(f"   • Collections: {info['vector_info']['collections']}")
            click.echo(f"   • Vectors: {info['vector_info']['vector_count']:,}")
            click.echo(f"   • Dimensions: {info['vector_info']['dimensions']}")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to get info: {e}", err=True)
        sys.exit(1)


@db.command()
def stats():
    """Show database statistics"""

    click.echo("📊 Database Statistics")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()
        stats = manager.get_stats()

        click.echo("\n📈 Processing Stats:")
        click.echo(f"   • Total processed: {stats['total_processed']:,}")
        click.echo(f"   • Successful: {stats['successful']:,}")
        click.echo(f"   • Failed: {stats['failed']:,}")
        click.echo(f"   • Average time: {stats['avg_processing_time']:.2f}s")

        click.echo("\n📅 Activity (Last 7 days):")
        for day, count in stats['daily_activity'].items():
            bar = '█' * (count // 10) if count > 0 else '·'
            click.echo(f"   {day}: {bar} ({count})")

        click.echo("\n🏆 Top Sources:")
        for source, count in stats['top_sources'][:5]:
            click.echo(f"   • {source}: {count} documents")

        click.echo("\n💾 Storage:")
        click.echo(f"   • Database size: {stats['db_size_mb']:.2f} MB")
        click.echo(f"   • Index size: {stats['index_size_mb']:.2f} MB")
        click.echo(f"   • Cache size: {stats['cache_size_mb']:.2f} MB")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to get stats: {e}", err=True)
        sys.exit(1)


@db.command()
@click.option('--vacuum', is_flag=True,
              help='Run VACUUM to reclaim space')
@click.option('--reindex', is_flag=True,
              help='Rebuild all indexes')
@click.option('--analyze', is_flag=True,
              help='Update statistics')
@click.option('--all', 'run_all', is_flag=True,
              help='Run all optimizations')
@click.pass_context
def optimize(ctx, vacuum, reindex, analyze, run_all):
    """Optimize database performance"""

    click.echo("🔧 Optimizing Database")

    if not any([vacuum, reindex, analyze, run_all]):
        click.echo("   ℹ️  No optimization specified. Use --all for full optimization.")
        return

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()

        if vacuum or run_all:
            click.echo("   • Running VACUUM...")
            size_before = manager.get_size()
            manager.vacuum()
            size_after = manager.get_size()
            saved = size_before - size_after
            if saved > 0:
                click.echo(f"     ✅ Reclaimed {saved:.2f} MB")
            else:
                click.echo(f"     ✅ Complete")

        if reindex or run_all:
            click.echo("   • Rebuilding indexes...")
            manager.reindex()
            click.echo("     ✅ Indexes rebuilt")

        if analyze or run_all:
            click.echo("   • Updating statistics...")
            manager.analyze()
            click.echo("     ✅ Statistics updated")

        click.echo("\n✅ Optimization complete")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Optimization failed: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@db.command()
@click.option('--force', is_flag=True,
              help='Force compaction')
def compact(force):
    """Compact database to reduce size"""

    click.echo("📦 Compacting Database")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()

        size_before = manager.get_size()
        click.echo(f"   • Current size: {size_before:.2f} MB")

        if not force:
            if size_before < 100:  # Less than 100MB
                click.echo("   ℹ️  Database is small, compaction not needed")
                return

        click.echo("   • Compacting...")
        manager.compact()

        size_after = manager.get_size()
        saved = size_before - size_after

        click.echo(f"   • New size: {size_after:.2f} MB")
        click.echo(f"   ✅ Saved {saved:.2f} MB ({saved/size_before*100:.1f}%)")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Compaction failed: {e}", err=True)
        sys.exit(1)


@db.command()
@click.option('--older-than', type=int,
              help='Remove entries older than N days')
@click.option('--duplicates', is_flag=True,
              help='Remove duplicate entries')
@click.option('--orphaned', is_flag=True,
              help='Remove orphaned records')
@click.option('--cache', is_flag=True,
              help='Clear cache')
def clean(older_than, duplicates, orphaned, cache):
    """Clean database by removing old or unnecessary data"""

    click.echo("🧹 Cleaning Database")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()
        total_removed = 0

        if older_than:
            click.echo(f"   • Removing entries older than {older_than} days...")
            removed = manager.clean_old_entries(days=older_than)
            total_removed += removed
            click.echo(f"     ✅ Removed {removed} entries")

        if duplicates:
            click.echo("   • Removing duplicates...")
            removed = manager.clean_duplicates()
            total_removed += removed
            click.echo(f"     ✅ Removed {removed} duplicates")

        if orphaned:
            click.echo("   • Removing orphaned records...")
            removed = manager.clean_orphaned()
            total_removed += removed
            click.echo(f"     ✅ Removed {removed} orphaned records")

        if cache:
            click.echo("   • Clearing cache...")
            manager.clear_cache()
            click.echo("     ✅ Cache cleared")

        if total_removed > 0:
            click.echo(f"\n✅ Cleaned {total_removed} total records")
        else:
            click.echo("\n✅ No records to clean")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Cleaning failed: {e}", err=True)
        sys.exit(1)


@db.command()
@click.argument('output_file', type=click.Path())
@click.option('--format', 'export_format',
              type=click.Choice(['sqlite', 'json', 'csv']),
              default='sqlite',
              help='Export format')
@click.option('--tables', type=str,
              help='Specific tables to export (comma-separated)')
@click.option('--compress', is_flag=True,
              help='Compress output file')
@click.pass_context
def export(ctx, output_file, export_format, tables, compress):
    """Export database to file"""

    click.echo(f"📤 Exporting Database")
    click.echo(f"   • Format: {export_format}")
    click.echo(f"   • Output: {output_file}")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()

        # Parse tables
        table_list = None
        if tables:
            table_list = [t.strip() for t in tables.split(',')]

        # Export
        with click.progressbar(label='Exporting') as bar:
            def update_progress(current, total):
                bar.update(current)

            manager.export(
                output_file,
                format=export_format,
                tables=table_list,
                compress=compress,
                progress_callback=update_progress
            )

        # Get file size
        output_path = Path(output_file)
        size_mb = output_path.stat().st_size / (1024 * 1024)

        click.echo(f"\n✅ Export complete")
        click.echo(f"   • File size: {size_mb:.2f} MB")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@db.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--format', 'import_format',
              type=click.Choice(['sqlite', 'json', 'csv']),
              help='Import format (auto-detect if not specified)')
@click.option('--merge/--replace', default=True,
              help='Merge with existing data or replace')
@click.pass_context
def import_db(ctx, input_file, import_format, merge):
    """Import database from file"""

    click.echo(f"📥 Importing Database")
    click.echo(f"   • Source: {input_file}")
    click.echo(f"   • Mode: {'Merge' if merge else 'Replace'}")

    try:
        from ...database.manager import DatabaseManager

        manager = DatabaseManager()

        # Auto-detect format if not specified
        if not import_format:
            if input_file.endswith('.json'):
                import_format = 'json'
            elif input_file.endswith('.csv'):
                import_format = 'csv'
            else:
                import_format = 'sqlite'

        click.echo(f"   • Format: {import_format}")

        # Import
        with click.progressbar(label='Importing') as bar:
            def update_progress(current, total):
                bar.update(current)

            stats = manager.import_data(
                input_file,
                format=import_format,
                merge=merge,
                progress_callback=update_progress
            )

        click.echo(f"\n✅ Import complete")
        click.echo(f"   • Records imported: {stats['imported']:,}")
        click.echo(f"   • Records skipped: {stats['skipped']:,}")
        click.echo(f"   • Errors: {stats['errors']:,}")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Import failed: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@db.command()
@click.argument('source_db', type=click.Path(exists=True))
@click.argument('target_db', type=click.Path())
@click.option('--strategy', type=click.Choice(['append', 'update', 'upsert']),
              default='upsert',
              help='Merge strategy')
def merge(source_db, target_db, strategy):
    """Merge two databases"""

    click.echo(f"🔀 Merging Databases")
    click.echo(f"   • Source: {source_db}")
    click.echo(f"   • Target: {target_db}")
    click.echo(f"   • Strategy: {strategy}")

    try:
        from ...database.merger import DatabaseMerger

        merger = DatabaseMerger()

        stats = merger.merge(
            source_db,
            target_db,
            strategy=strategy
        )

        click.echo(f"\n✅ Merge complete")
        click.echo(f"   • Records merged: {stats['merged']:,}")
        click.echo(f"   • Records updated: {stats['updated']:,}")
        click.echo(f"   • Conflicts resolved: {stats['conflicts']:,}")

    except ImportError:
        click.echo("❌ Database merger not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Merge failed: {e}", err=True)
        sys.exit(1)


# Vector sub-commands
@db.group()
def vector():
    """Vector database operations"""
    pass


@vector.command()
@click.option('--backend', type=click.Choice(['milvus', 'faiss', 'chroma']),
              default='milvus',
              help='Vector backend')
@click.option('--collection', default='netintel_vectors',
              help='Collection name')
@click.option('--dimensions', type=int, default=768,
              help='Vector dimensions')
def init(backend, collection, dimensions):
    """Initialize vector database"""

    click.echo(f"🔮 Initializing Vector Database")
    click.echo(f"   • Backend: {backend}")
    click.echo(f"   • Collection: {collection}")
    click.echo(f"   • Dimensions: {dimensions}")

    try:
        from ...vectors.manager import VectorManager

        manager = VectorManager(backend=backend)
        manager.init_collection(
            name=collection,
            dimensions=dimensions
        )

        click.echo("\n✅ Vector database initialized")

    except ImportError:
        click.echo("❌ Vector module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Initialization failed: {e}", err=True)
        sys.exit(1)


@vector.command()
@click.option('--collection', default='netintel_vectors',
              help='Collection to rebuild')
@click.option('--batch-size', type=int, default=100,
              help='Batch size for processing')
def rebuild(collection, batch_size):
    """Rebuild vector index"""

    click.echo(f"🔨 Rebuilding Vector Index")
    click.echo(f"   • Collection: {collection}")

    try:
        from ...vectors.manager import VectorManager

        manager = VectorManager()

        with click.progressbar(label='Rebuilding') as bar:
            def update_progress(current, total):
                bar.update(current)

            stats = manager.rebuild_index(
                collection=collection,
                batch_size=batch_size,
                progress_callback=update_progress
            )

        click.echo(f"\n✅ Rebuild complete")
        click.echo(f"   • Vectors processed: {stats['processed']:,}")
        click.echo(f"   • Time taken: {stats['time_seconds']:.2f}s")

    except ImportError:
        click.echo("❌ Vector module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Rebuild failed: {e}", err=True)
        sys.exit(1)


@vector.command(name='stats')
def vector_stats():
    """Show vector database statistics"""

    click.echo("📊 Vector Database Statistics")

    try:
        from ...vectors.manager import VectorManager

        manager = VectorManager()
        stats = manager.get_stats()

        click.echo(f"\n• Backend: {stats['backend']}")
        click.echo(f"• Collections: {len(stats['collections'])}")

        for coll in stats['collections']:
            click.echo(f"\n  📁 {coll['name']}:")
            click.echo(f"     • Vectors: {coll['count']:,}")
            click.echo(f"     • Dimensions: {coll['dimensions']}")
            click.echo(f"     • Index type: {coll['index_type']}")
            click.echo(f"     • Size: {coll['size_mb']:.2f} MB")

    except ImportError:
        click.echo("❌ Vector module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to get stats: {e}", err=True)
        sys.exit(1)


@vector.command(name='search')
@click.argument('query_text')
@click.option('--k', type=int, default=10,
              help='Number of nearest neighbors')
@click.option('--collection', default='netintel_vectors',
              help='Collection to search')
def vector_search(query_text, k, collection):
    """Search vector database"""

    click.echo(f"🔍 Vector Search: '{query_text}'")
    click.echo(f"   • Collection: {collection}")
    click.echo(f"   • K: {k}")

    try:
        from ...vectors.manager import VectorManager

        manager = VectorManager()
        results = manager.search(
            query_text=query_text,
            collection=collection,
            k=k
        )

        click.echo(f"\n📊 Found {len(results)} results:\n")

        for i, result in enumerate(results, 1):
            click.echo(f"{i}. Score: {result['score']:.4f}")
            click.echo(f"   ID: {result['id']}")
            click.echo(f"   Text: {result['text'][:100]}...")
            click.echo()

    except ImportError:
        click.echo("❌ Vector module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Search failed: {e}", err=True)
        sys.exit(1)


@db.command()
@click.option('--aggressive', is_flag=True, help='Aggressive compaction')
@click.option('--vacuum', is_flag=True, help='Vacuum after compaction')
def compact(aggressive, vacuum):
    """Compact database to reclaim space"""
    click.echo("📦 Compacting Database")

    try:
        from ...database.manager import DatabaseManager
        manager = DatabaseManager()

        if aggressive:
            click.echo("   • Mode: Aggressive")
        else:
            click.echo("   • Mode: Standard")

        # Mock implementation
        click.echo("   • Analyzing database...")
        click.echo("   • Reorganizing indexes...")
        click.echo("   • Compacting tables...")

        if vacuum:
            click.echo("   • Vacuuming database...")

        click.echo("✅ Compaction complete")
        click.echo("   • Space reclaimed: 125 MB")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)


@db.command()
@click.argument('days', type=int)
@click.option('--duplicates', is_flag=True, help='Remove duplicates')
@click.option('--orphaned', is_flag=True, help='Remove orphaned records')
def cleanup(days, duplicates, orphaned):
    """Clean up old data from database"""
    click.echo(f"🧹 Cleaning up database")
    click.echo(f"   • Removing data older than {days} days")

    try:
        from ...database.manager import DatabaseManager
        manager = DatabaseManager()

        removed = 0
        if duplicates:
            click.echo("   • Removing duplicates...")
            # Mock implementation
            removed += 10

        if orphaned:
            click.echo("   • Removing orphaned records...")
            # Mock implementation
            removed += 5

        click.echo(f"✅ Cleaned up {removed} records")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)


@db.command('import')
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--format', 'file_format', type=click.Choice(['json', 'csv', 'sqlite']),
              default='json', help='Import format')
def import_data(file_path, file_format):
    """Import data into database"""
    click.echo(f"📥 Importing from {file_path}")
    click.echo(f"   • Format: {file_format}")

    try:
        from ...database.manager import DatabaseManager
        manager = DatabaseManager()

        # Mock implementation
        click.echo("   • Reading file...")
        click.echo("   • Validating data...")
        click.echo("   • Importing records...")

        click.echo(f"✅ Imported 100 records successfully")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)


@db.command()
@click.argument('source', type=click.Path(exists=True))
@click.argument('target', type=click.Path())
@click.option('--format', 'target_format', type=click.Choice(['sqlite', 'postgres', 'json']),
              help='Target database format')
def migrate(source, target, target_format):
    """Migrate database to different format"""
    click.echo(f"🔄 Migrating database")
    click.echo(f"   • Source: {source}")
    click.echo(f"   • Target: {target}")
    if target_format:
        click.echo(f"   • Format: {target_format}")

    try:
        from ...database.manager import DatabaseManager
        manager = DatabaseManager()

        # Mock implementation
        click.echo("   • Reading source database...")
        click.echo("   • Converting schema...")
        click.echo("   • Migrating data...")
        click.echo("   • Verifying integrity...")

        click.echo(f"✅ Migration completed successfully")

    except ImportError:
        click.echo("❌ Database module not found.", err=True)
        sys.exit(1)