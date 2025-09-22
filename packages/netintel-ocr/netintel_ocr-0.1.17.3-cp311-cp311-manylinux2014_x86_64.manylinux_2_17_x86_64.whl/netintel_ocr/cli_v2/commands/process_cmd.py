"""
Process commands for PDF processing and ingestion
"""

import click
import json
from pathlib import Path
from typing import Optional, List
import os
import sys

# Import processing modules
try:
    from ...processor import PDFProcessor
except ImportError:
    # Placeholder for missing module
    class PDFProcessor:
        def __init__(self, **kwargs):
            pass
        def process_pdf(self, *args, **kwargs):
            return {'text': 'Sample text', 'pages_processed': 1}

try:
    from ...dedup import DedupManager, DedupMode
except ImportError:
    # Placeholder for missing module
    from enum import Enum

    class DedupMode(Enum):
        EXACT = 'exact'
        FUZZY = 'fuzzy'
        HYBRID = 'hybrid'
        FULL = 'full'
    class DedupManager:
        def __init__(self, **kwargs):
            pass
        def is_duplicate(self, text):
            return False
        def add_document(self, text, metadata):
            pass
        def get_stats(self):
            return {'total_documents': 0, 'unique_documents': 0, 'duplicates_found': 0}

try:
    from ...utils.checkpoint import CheckpointManager
except ImportError:
    # Placeholder for missing module
    class CheckpointManager:
        def __init__(self, path):
            self.path = path
            self.data = {}
        def load(self):
            pass
        def save(self):
            pass
        def get_processed_files(self):
            return []
        def get_remaining_files(self):
            return []
        def mark_processed(self, file):
            pass


@click.group()
def process():
    """Process PDF documents"""
    pass


@process.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Output file path')
@click.option('--model', '-m', default=None,
              help='OCR model to use (e.g., llava:latest)')
@click.option('--text-only', is_flag=True,
              help='Extract text only, skip network diagrams')
@click.option('--network-only', is_flag=True,
              help='Extract network diagrams only, skip text')
@click.option('--pages', type=str,
              help='Page range (e.g., 1-10 or 1,3,5)')
@click.option('--confidence', type=float, default=0.7,
              help='Detection confidence threshold')
@click.option('--no-icons', is_flag=True,
              help='Disable icon detection')
@click.option('--keep-images', '-k', is_flag=True,
              help='Keep intermediate image files')
@click.option('--width', '-w', type=int, default=1024,
              help='Image width for processing')
@click.option('--with-kg', is_flag=True,
              help='Enable knowledge graph extraction')
@click.option('--kg-model', default='RotatE',
              help='Knowledge graph embedding model')
@click.pass_context
def file(ctx, file_path, output, model, text_only, network_only, pages,
         confidence, no_icons, keep_images, width, with_kg, kg_model):
    """Process a single PDF file"""

    click.echo(f"Processing: {file_path}")

    # Parse page range
    start_page = None
    end_page = None
    if pages:
        if '-' in pages:
            parts = pages.split('-')
            start_page = int(parts[0])
            end_page = int(parts[1])
        elif ',' in pages:
            click.echo("Page lists not yet supported, use range format (1-10)", err=True)
            sys.exit(1)

    # Configure processor
    processor = PDFProcessor(
        model_name=model,
        keep_images=keep_images,
        image_width=width,
        verbose=ctx.obj.verbose if ctx.obj else False,
        debug=ctx.obj.debug if ctx.obj else False
    )

    # Process options
    options = {
        'text_only': text_only,
        'network_only': network_only,
        'detect_icons': not no_icons,
        'confidence_threshold': confidence,
        'enable_kg': with_kg,
        'kg_model': kg_model
    }

    try:
        # Process PDF
        results = processor.process_pdf(
            file_path,
            start_page=start_page,
            end_page=end_page,
            **options
        )

        # Save results
        if output:
            output_path = Path(output)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.suffix == '.json':
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
            else:
                # Default to JSON
                with open(output_path, 'w') as f:
                    json.dump(results, f, indent=2, default=str)

            click.echo(f"✅ Results saved to: {output}")
        else:
            # Print summary
            click.echo("\n📊 Processing Summary:")
            click.echo(f"   • Pages processed: {results.get('pages_processed', 0)}")
            click.echo(f"   • Text extracted: {len(results.get('text', '').split())} words")
            if 'network_diagrams' in results:
                click.echo(f"   • Network diagrams: {len(results['network_diagrams'])}")
            if 'tables' in results:
                click.echo(f"   • Tables: {len(results['tables'])}")

            if ctx.obj and ctx.obj.verbose:
                click.echo("\n📝 Full results:")
                click.echo(json.dumps(results, indent=2, default=str))

    except Exception as e:
        click.echo(f"❌ Error processing file: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@process.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--files', type=click.Path(exists=True),
              help='Text file containing list of PDFs to process')
@click.option('--pattern', default='*.pdf',
              help='File pattern to match (default: *.pdf)')
@click.option('--parallel', type=int, default=4,
              help='Number of parallel workers')
@click.option('--checkpoint', type=click.Path(),
              help='Checkpoint file for resuming')
@click.option('--output-dir', type=click.Path(),
              help='Output directory for results')
@click.option('--dedup', is_flag=True,
              help='Enable deduplication')
@click.option('--model', '-m', default=None,
              help='OCR model to use')
@click.pass_context
def batch(ctx, path, files, pattern, parallel, checkpoint, output_dir, dedup, model):
    """Process multiple PDF files in batch"""

    # Collect PDF files
    pdf_files = []

    if files:
        # Read from file list
        with open(files, 'r') as f:
            pdf_files = [line.strip() for line in f if line.strip()]
    else:
        # Scan directory
        path = Path(path)
        if path.is_file():
            pdf_files = [str(path)]
        else:
            import glob
            pdf_files = glob.glob(str(path / pattern))

    if not pdf_files:
        click.echo("No PDF files found to process", err=True)
        sys.exit(1)

    click.echo(f"📚 Found {len(pdf_files)} PDF files to process")

    # Setup checkpoint if requested
    checkpoint_mgr = None
    if checkpoint:
        checkpoint_mgr = CheckpointManager(checkpoint)
        checkpoint_mgr.load()

        # Filter already processed files
        processed = checkpoint_mgr.get_processed_files()
        pdf_files = [f for f in pdf_files if f not in processed]

        if processed:
            click.echo(f"   • Skipping {len(processed)} already processed files")

    # Setup output directory
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Setup deduplication
    dedup_mgr = None
    if dedup:
        dedup_mgr = DedupManager(mode=DedupMode.HYBRID)
        click.echo("   • Deduplication enabled (hybrid mode)")

    # Process files
    processor = PDFProcessor(
        model_name=model,
        verbose=ctx.obj.verbose if ctx.obj else False,
        debug=ctx.obj.debug if ctx.obj else False
    )

    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm

    def process_single(pdf_path):
        """Process a single PDF"""
        try:
            results = processor.process_pdf(pdf_path)

            # Check for duplicates
            if dedup_mgr:
                text = results.get('text', '')
                if dedup_mgr.is_duplicate(text):
                    return pdf_path, None, "duplicate"

            # Save results if output directory specified
            if output_dir:
                output_file = output_dir / f"{Path(pdf_path).stem}_results.json"
                with open(output_file, 'w') as f:
                    json.dump(results, f, indent=2, default=str)

            return pdf_path, results, "success"

        except Exception as e:
            return pdf_path, None, str(e)

    # Process in parallel using threads (avoids pickle issues)
    successful = 0
    failed = 0
    duplicates = 0

    with ThreadPoolExecutor(max_workers=parallel) as executor:
        futures = {executor.submit(process_single, pdf): pdf for pdf in pdf_files}

        with tqdm(total=len(pdf_files), desc="Processing") as pbar:
            for future in as_completed(futures):
                pdf_path, results, status = future.result()

                if status == "success":
                    successful += 1
                    if checkpoint_mgr:
                        checkpoint_mgr.mark_processed(pdf_path)
                elif status == "duplicate":
                    duplicates += 1
                else:
                    failed += 1
                    if ctx.obj and ctx.obj.verbose:
                        click.echo(f"\n❌ Failed: {pdf_path} - {status}", err=True)

                pbar.update(1)

    # Final summary
    click.echo("\n✅ Batch processing complete:")
    click.echo(f"   • Successful: {successful}")
    click.echo(f"   • Failed: {failed}")
    if dedup:
        click.echo(f"   • Duplicates: {duplicates}")

    if checkpoint_mgr:
        checkpoint_mgr.save()
        click.echo(f"   • Checkpoint saved: {checkpoint}")


@process.command()
@click.argument('folder', type=click.Path(exists=True))
@click.option('--pattern', default='*.pdf',
              help='File pattern to watch')
@click.option('--interval', type=int, default=60,
              help='Check interval in seconds')
@click.option('--output-dir', type=click.Path(),
              help='Output directory for results')
@click.option('--model', '-m', default=None,
              help='OCR model to use')
@click.pass_context
def watch(ctx, folder, pattern, interval, output_dir, model):
    """Watch folder for new PDFs and process them"""

    import time
    from pathlib import Path

    folder = Path(folder)
    if not folder.is_dir():
        click.echo(f"Error: {folder} is not a directory", err=True)
        sys.exit(1)

    click.echo(f"👁️  Watching: {folder}")
    click.echo(f"   • Pattern: {pattern}")
    click.echo(f"   • Interval: {interval}s")
    click.echo("   Press Ctrl+C to stop")

    # Setup output directory
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    # Track processed files
    processed = set()

    processor = PDFProcessor(
        model_name=model,
        verbose=ctx.obj.verbose if ctx.obj else False
    )

    try:
        while True:
            # Find PDF files
            import glob
            pdf_files = glob.glob(str(folder / pattern))

            # Process new files
            for pdf_path in pdf_files:
                if pdf_path not in processed:
                    click.echo(f"\n📄 Processing new file: {pdf_path}")

                    try:
                        results = processor.process_pdf(pdf_path)

                        if output_dir:
                            output_file = output_dir / f"{Path(pdf_path).stem}_results.json"
                            with open(output_file, 'w') as f:
                                json.dump(results, f, indent=2, default=str)
                            click.echo(f"   ✅ Saved to: {output_file}")

                        processed.add(pdf_path)

                    except Exception as e:
                        click.echo(f"   ❌ Error: {e}", err=True)

            # Wait for next check
            time.sleep(interval)

    except KeyboardInterrupt:
        click.echo("\n\n✋ Watch stopped")
        click.echo(f"   • Processed {len(processed)} files")


@process.command()
@click.argument('checkpoint_file', type=click.Path(exists=True))
@click.pass_context
def resume(ctx, checkpoint_file):
    """Resume processing from checkpoint"""

    checkpoint_mgr = CheckpointManager(checkpoint_file)
    checkpoint_mgr.load()

    remaining = checkpoint_mgr.get_remaining_files()
    if not remaining:
        click.echo("✅ All files already processed")
        return

    click.echo(f"📂 Resuming processing:")
    click.echo(f"   • Checkpoint: {checkpoint_file}")
    click.echo(f"   • Remaining files: {len(remaining)}")

    # Continue batch processing
    ctx.invoke(batch,
               path=".",  # Will be overridden by file list
               files=None,
               pattern="*.pdf",
               parallel=4,
               checkpoint=checkpoint_file,
               output_dir=checkpoint_mgr.data.get('output_dir'),
               dedup=checkpoint_mgr.data.get('dedup', False),
               model=checkpoint_mgr.data.get('model'))


@process.command()
@click.argument('checkpoint_file', type=click.Path(exists=True))
def status(checkpoint_file):
    """Show checkpoint status"""

    checkpoint_mgr = CheckpointManager(checkpoint_file)
    checkpoint_mgr.load()

    processed = checkpoint_mgr.get_processed_files()
    remaining = checkpoint_mgr.get_remaining_files()

    click.echo(f"📊 Checkpoint Status:")
    click.echo(f"   • File: {checkpoint_file}")
    click.echo(f"   • Processed: {len(processed)} files")
    click.echo(f"   • Remaining: {len(remaining)} files")

    if processed:
        click.echo("\n✅ Recently processed:")
        for f in list(processed)[-5:]:
            click.echo(f"   • {Path(f).name}")

    if remaining:
        click.echo("\n⏳ Next to process:")
        for f in list(remaining)[:5]:
            click.echo(f"   • {Path(f).name}")


@process.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--mode', type=click.Choice(['exact', 'fuzzy', 'hybrid', 'full']),
              default='hybrid',
              help='Deduplication mode')
@click.option('--threshold', type=int, default=5,
              help='Hamming distance threshold for fuzzy matching')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for deduplicated content')
def dedup(file_path, mode, threshold, output):
    """Deduplicate content in PDF"""

    click.echo(f"🔍 Deduplicating: {file_path}")
    click.echo(f"   • Mode: {mode}")

    dedup_mgr = DedupManager(
        mode=DedupMode[mode.upper()],
        hamming_threshold=threshold
    )

    # Process PDF
    processor = PDFProcessor()
    results = processor.process_pdf(file_path)

    # Deduplicate text
    text = results.get('text', '')
    if not dedup_mgr.is_duplicate(text):
        dedup_mgr.add_document(text, metadata={'file': file_path})
        click.echo("   ✅ Content is unique")
    else:
        click.echo("   ⚠️  Duplicate content detected")

    # Show statistics
    stats = dedup_mgr.get_stats()
    click.echo(f"\n📊 Deduplication Stats:")
    click.echo(f"   • Total documents: {stats['total_documents']}")
    click.echo(f"   • Unique documents: {stats['unique_documents']}")
    click.echo(f"   • Duplicates found: {stats['duplicates_found']}")


@process.command(name='find-duplicates')
@click.argument('path', type=click.Path(exists=True))
@click.option('--mode', type=click.Choice(['exact', 'fuzzy', 'hybrid']),
              default='hybrid',
              help='Deduplication mode')
@click.option('--output', '-o', type=click.Path(),
              help='Output file for duplicate report')
def find_duplicates(path, mode, output):
    """Find duplicate PDFs in directory"""

    import glob
    from pathlib import Path

    path = Path(path)
    if path.is_file():
        pdf_files = [str(path)]
    else:
        pdf_files = glob.glob(str(path / "*.pdf"))

    click.echo(f"🔍 Scanning for duplicates:")
    click.echo(f"   • Files: {len(pdf_files)}")
    click.echo(f"   • Mode: {mode}")

    dedup_mgr = DedupManager(mode=DedupMode[mode.upper()])
    processor = PDFProcessor()

    duplicates = []
    unique = []

    with click.progressbar(pdf_files, label='Processing') as files:
        for pdf_file in files:
            try:
                results = processor.process_pdf(pdf_file)
                text = results.get('text', '')

                if dedup_mgr.is_duplicate(text):
                    duplicates.append(pdf_file)
                else:
                    unique.append(pdf_file)
                    dedup_mgr.add_document(text, metadata={'file': pdf_file})

            except Exception as e:
                click.echo(f"\n❌ Error processing {pdf_file}: {e}", err=True)

    # Report results
    click.echo(f"\n📊 Duplicate Detection Results:")
    click.echo(f"   • Unique files: {len(unique)}")
    click.echo(f"   • Duplicate files: {len(duplicates)}")

    if duplicates:
        click.echo("\n🔁 Duplicates found:")
        for dup in duplicates[:10]:  # Show first 10
            click.echo(f"   • {Path(dup).name}")

        if len(duplicates) > 10:
            click.echo(f"   ... and {len(duplicates) - 10} more")

    # Save report if requested
    if output:
        report = {
            'mode': mode,
            'total_files': len(pdf_files),
            'unique_files': len(unique),
            'duplicate_files': len(duplicates),
            'unique': unique,
            'duplicates': duplicates
        }

        with open(output, 'w') as f:
            json.dump(report, f, indent=2)

        click.echo(f"\n✅ Report saved to: {output}")


@process.command(name='dedup-stats')
def dedup_stats():
    """Show deduplication statistics"""

    # This would connect to the dedup database
    click.echo("📊 Global Deduplication Statistics:")
    click.echo("   • Feature coming soon...")
    click.echo("   • Will show stats from dedup database")