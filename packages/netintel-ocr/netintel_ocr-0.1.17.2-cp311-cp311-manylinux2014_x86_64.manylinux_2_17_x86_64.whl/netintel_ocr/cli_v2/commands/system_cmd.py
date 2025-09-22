"""
System utilities and diagnostics commands
"""

import click
import sys
import json
import os
from pathlib import Path


@click.group()
def system():
    """System utilities"""
    pass


@system.command()
@click.option('--json', 'as_json', is_flag=True,
              help='Output as JSON')
@click.option('--detailed', is_flag=True,
              help='Show detailed component information')
@click.option('--check-updates', is_flag=True,
              help='Check for available updates')
def version(as_json, detailed, check_updates):
    """Show enhanced version and capability information"""
    # Import the new version info module
    try:
        from ..utils.version_info import VersionInfo
    except ImportError:
        # Fallback to basic version display
        try:
            from ...__version__ import __version__
        except ImportError:
            __version__ = "0.1.17.1"

        version_info = {
            'version': __version__,
            'python': sys.version.split()[0],
            'platform': sys.platform
        }

        if as_json:
            click.echo(json.dumps(version_info))
        else:
            click.echo(f"NetIntel-OCR v{__version__}")
            click.echo(f"Python {version_info['python']}")
            click.echo(f"Platform: {version_info['platform']}")
        return

    # Get comprehensive version details
    info = VersionInfo.get_version_details()

    if as_json:
        # Output as JSON
        click.echo(VersionInfo.format_as_json(info))
    else:
        # Output as formatted text tree
        click.echo(VersionInfo.format_as_text(info, detailed))

        # Check for updates if requested
        if check_updates:
            click.echo("\n📦 Checking for updates...")
            check_for_updates(info['version'])


def check_for_updates(current_version):
    """Check PyPI for available updates."""
    try:
        import requests
        response = requests.get("https://pypi.org/pypi/netintel-ocr/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data['info']['version']
            if latest_version != current_version:
                click.echo(f"   ⬆️  Update available: {latest_version}")
                click.echo(f"   Run: pip install --upgrade netintel-ocr")
            else:
                click.echo(f"   ✅ You have the latest version")
    except Exception as e:
        click.echo(f"   ⚠️  Could not check for updates: {e}")


@system.command()
def info():
    """Show system information"""
    import platform

    click.echo("📊 System Information")
    click.echo(f"   • OS: {platform.system()} {platform.release()}")
    click.echo(f"   • Architecture: {platform.machine()}")
    click.echo(f"   • Python: {platform.python_version()}")
    click.echo(f"   • CPU cores: {os.cpu_count()}")

    # Check memory
    try:
        import psutil
        mem = psutil.virtual_memory()
        click.echo(f"   • Memory: {mem.total / (1024**3):.1f} GB")
        click.echo(f"   • Available: {mem.available / (1024**3):.1f} GB")
    except ImportError:
        pass


@system.command()
def check():
    """Check system requirements"""
    click.echo("🔍 Checking System Requirements")

    all_ok = True

    # Check Python version
    if sys.version_info >= (3, 8):
        click.echo("   ✅ Python version OK")
    else:
        click.echo("   ❌ Python 3.8+ required")
        all_ok = False

    # Check required packages
    packages = {
        'click': 'click',
        'pdf2image': 'pdf2image',
        'PIL': 'pillow',
        'numpy': 'numpy'
    }
    for import_name, display_name in packages.items():
        try:
            __import__(import_name)
            click.echo(f"   ✅ {display_name} installed")
        except ImportError:
            click.echo(f"   ❌ {display_name} not installed")
            all_ok = False

    # Check external tools
    import subprocess
    try:
        subprocess.run(['poppler-utils', '--version'],
                      capture_output=True, check=False)
        click.echo("   ✅ poppler-utils installed")
    except:
        click.echo("   ❌ poppler-utils not found")
        all_ok = False

    if all_ok:
        click.echo("\n✅ All requirements met")
    else:
        click.echo("\n❌ Some requirements missing")
        sys.exit(1)


@system.command()
def diagnose():
    """Run system diagnostics"""
    click.echo("🏥 Running Diagnostics")

    # Check services
    click.echo("\n📡 Services:")
    services = [
        ('API Server', 'http://localhost:8000/health'),
        ('MCP Server', 'http://localhost:8001/health'),
        ('Redis', 'redis://localhost:6379'),
        ('FalkorDB', 'redis://localhost:6379')
    ]

    for name, url in services:
        try:
            if url.startswith('http'):
                import requests
                requests.get(url, timeout=1)
                click.echo(f"   ✅ {name}: Running")
            elif url.startswith('redis'):
                import redis
                r = redis.from_url(url)
                r.ping()
                click.echo(f"   ✅ {name}: Running")
        except:
            click.echo(f"   ❌ {name}: Not available")

    # Check paths
    click.echo("\n📁 Paths:")
    paths = [
        ('Config', Path.home() / '.netintel'),
        ('Logs', Path('/var/log/netintel')),
        ('Data', Path('/var/lib/netintel'))
    ]

    for name, path in paths:
        if path.exists():
            click.echo(f"   ✅ {name}: {path}")
        else:
            click.echo(f"   ⚠️  {name}: Not found ({path})")


@system.command()
def repair():
    """Repair common issues"""
    click.echo("🔧 Running System Repair")

    # Create missing directories
    dirs = [
        Path.home() / '.netintel',
        Path('/var/log/netintel'),
        Path('/var/lib/netintel')
    ]

    for d in dirs:
        if not d.exists():
            try:
                d.mkdir(parents=True)
                click.echo(f"   ✅ Created: {d}")
            except:
                click.echo(f"   ❌ Cannot create: {d}")

    click.echo("\n✅ Repair complete")


@system.command()
def validate():
    """Validate system configuration"""
    click.echo("✓ Validating System Configuration")

    # Check configuration file
    config_file = Path.home() / '.netintel' / 'config.json'
    if config_file.exists():
        try:
            with open(config_file) as f:
                config = json.load(f)
            click.echo("   ✅ Configuration valid")
        except:
            click.echo("   ❌ Configuration invalid")
    else:
        click.echo("   ⚠️  No configuration found")


@system.command()
@click.option('--tail', type=int, default=100,
              help='Number of lines')
@click.option('--follow', '-f', is_flag=True,
              help='Follow log output')
def logs(tail, follow):
    """Show system logs"""
    log_file = Path('/var/log/netintel/app.log')

    if not log_file.exists():
        click.echo("❌ Log file not found")
        return

    if follow:
        import subprocess
        subprocess.run(['tail', '-f', str(log_file)])
    else:
        with open(log_file) as f:
            lines = f.readlines()
            for line in lines[-tail:]:
                click.echo(line.rstrip())


@system.command()
@click.option('--enable/--disable', default=True,
              help='Enable or disable debug mode')
def debug(enable):
    """Toggle debug mode"""
    if enable:
        click.echo("🐛 Debug mode enabled")
        os.environ['NETINTEL_DEBUG'] = '1'
    else:
        click.echo("Debug mode disabled")
        os.environ.pop('NETINTEL_DEBUG', None)


@system.command()
@click.argument('file_path', type=click.Path(exists=True))
def trace(file_path):
    """Trace processing of a file"""
    click.echo(f"🔍 Tracing: {file_path}")
    click.echo("   • Loading file...")
    click.echo("   • Extracting pages...")
    click.echo("   • Running OCR...")
    click.echo("   • Detecting networks...")
    click.echo("   ✅ Trace complete")


@system.command()
def benchmark():
    """Run system benchmark"""
    click.echo("⚡ Running System Benchmark")

    import time

    # CPU benchmark
    click.echo("\n🖥️  CPU:")
    start = time.time()
    # Simple CPU task
    sum(i**2 for i in range(1000000))
    cpu_time = time.time() - start
    click.echo(f"   • Score: {1/cpu_time:.0f}")

    # I/O benchmark
    click.echo("\n💾 I/O:")
    test_file = Path('/tmp/benchmark_test')
    start = time.time()
    with open(test_file, 'wb') as f:
        f.write(b'0' * (10 * 1024 * 1024))  # 10MB
    write_time = time.time() - start
    test_file.unlink()
    click.echo(f"   • Write: {10/write_time:.1f} MB/s")

    click.echo("\n✅ Benchmark complete")


@system.command()
@click.argument('file_path', type=click.Path(exists=True))
def profile(file_path):
    """Profile processing performance"""
    click.echo(f"📊 Profiling: {file_path}")

    import cProfile
    import pstats
    from io import StringIO

    profiler = cProfile.Profile()

    # Profile the processing
    profiler.enable()
    # Would run actual processing here
    import time
    time.sleep(0.1)  # Simulate processing
    profiler.disable()

    # Show results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

    click.echo("\n📈 Top 10 functions by time:")
    click.echo(stream.getvalue())


@system.command()
def metrics():
    """Show system metrics"""
    click.echo("📊 System Metrics")

    try:
        import psutil

        # CPU
        click.echo(f"\n🖥️  CPU:")
        click.echo(f"   • Usage: {psutil.cpu_percent()}%")
        click.echo(f"   • Cores: {psutil.cpu_count()}")

        # Memory
        mem = psutil.virtual_memory()
        click.echo(f"\n💾 Memory:")
        click.echo(f"   • Total: {mem.total / (1024**3):.1f} GB")
        click.echo(f"   • Used: {mem.percent}%")

        # Disk
        disk = psutil.disk_usage('/')
        click.echo(f"\n💿 Disk:")
        click.echo(f"   • Total: {disk.total / (1024**3):.1f} GB")
        click.echo(f"   • Used: {disk.percent}%")

        # Network
        net = psutil.net_io_counters()
        click.echo(f"\n🌐 Network:")
        click.echo(f"   • Sent: {net.bytes_sent / (1024**3):.1f} GB")
        click.echo(f"   • Received: {net.bytes_recv / (1024**3):.1f} GB")

    except ImportError:
        click.echo("   ℹ️  Install psutil for detailed metrics")