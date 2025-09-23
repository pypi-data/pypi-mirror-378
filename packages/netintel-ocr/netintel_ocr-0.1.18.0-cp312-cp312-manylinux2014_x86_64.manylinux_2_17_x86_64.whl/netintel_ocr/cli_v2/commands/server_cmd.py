"""
Server commands for API, MCP, and worker management
"""

import click
import sys
import os
from pathlib import Path


@click.group()
def server():
    """Server operations"""
    pass


@server.command()
@click.option('--host', default='0.0.0.0',
              help='API server host')
@click.option('--port', type=int, default=8000,
              help='API server port')
@click.option('--workers', type=int, default=4,
              help='Number of worker processes')
@click.option('--embedded', is_flag=True,
              help='Run workers embedded in API process')
@click.option('--reload', is_flag=True,
              help='Enable auto-reload for development')
@click.option('--cors', is_flag=True, default=True,
              help='Enable CORS')
@click.pass_context
def api(ctx, host, port, workers, embedded, reload, cors):
    """Start API server"""

    click.echo(f"🚀 Starting API Server")
    click.echo(f"   • Host: {host}:{port}")
    click.echo(f"   • Workers: {workers} {'(embedded)' if embedded else '(separate)'}")
    click.echo(f"   • CORS: {'enabled' if cors else 'disabled'}")

    try:
        from ...api.server import run_api_server
    except ImportError:
        def run_api_server(**kwargs):
            click.echo("API server module not yet implemented")
            click.echo("This would start the API server with the provided configuration")

    try:
        config = {
            'host': host,
            'port': port,
            'workers': workers,
            'embedded_workers': embedded,
            'reload': reload,
            'cors_enabled': cors,
            'debug': ctx.obj.debug if ctx.obj else False
        }

        # Load from config file if available
        if ctx.obj and ctx.obj.config_data:
            server_config = ctx.obj.config_data.get('server', {}).get('api', {})
            config.update(server_config)

        run_api_server(**config)

    except ImportError:
        click.echo("❌ API server module not found. Please install API dependencies.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start API server: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@server.command()
@click.option('--host', default='0.0.0.0',
              help='MCP server host')
@click.option('--port', type=int, default=8001,
              help='MCP server port')
@click.option('--auth', is_flag=True,
              help='Enable authentication')
@click.option('--token', envvar='MCP_AUTH_TOKEN',
              help='Authentication token')
@click.pass_context
def mcp(ctx, host, port, auth, token):
    """Start Model Context Protocol (MCP) server"""

    click.echo(f"🤖 Starting MCP Server")
    click.echo(f"   • Host: {host}:{port}")
    click.echo(f"   • Auth: {'enabled' if auth else 'disabled'}")

    try:
        from ...mcp.server import run_mcp_server

        config = {
            'host': host,
            'port': port,
            'auth_enabled': auth,
            'auth_token': token,
            'debug': ctx.obj.debug if ctx.obj else False
        }

        # Load from config file if available
        if ctx.obj and ctx.obj.config_data:
            mcp_config = ctx.obj.config_data.get('server', {}).get('mcp', {})
            config.update(mcp_config)

        run_mcp_server(**config)

    except ImportError:
        click.echo("❌ MCP server module not found. Please install MCP dependencies.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start MCP server: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@server.command()
@click.option('--api-port', type=int, default=8000,
              help='API server port')
@click.option('--mcp-port', type=int, default=8001,
              help='MCP server port')
@click.option('--workers', type=int, default=4,
              help='Number of worker processes')
@click.pass_context
def all(ctx, api_port, mcp_port, workers):
    """Start all services (API + MCP + Workers)"""

    click.echo(f"🚀 Starting All Services")
    click.echo(f"   • API: 0.0.0.0:{api_port}")
    click.echo(f"   • MCP: 0.0.0.0:{mcp_port}")
    click.echo(f"   • Workers: {workers}")

    try:
        import multiprocessing
        from ...api.server import run_api_server
        from ...mcp.server import run_mcp_server

        # Start API server in a process
        api_process = multiprocessing.Process(
            target=run_api_server,
            kwargs={
                'host': '0.0.0.0',
                'port': api_port,
                'workers': workers,
                'embedded_workers': True
            }
        )

        # Start MCP server in a process
        mcp_process = multiprocessing.Process(
            target=run_mcp_server,
            kwargs={
                'host': '0.0.0.0',
                'port': mcp_port
            }
        )

        api_process.start()
        mcp_process.start()

        click.echo("\n✅ All services started")
        click.echo("   Press Ctrl+C to stop all services")

        try:
            api_process.join()
            mcp_process.join()
        except KeyboardInterrupt:
            click.echo("\n\n✋ Stopping all services...")
            api_process.terminate()
            mcp_process.terminate()
            api_process.join(timeout=5)
            mcp_process.join(timeout=5)
            click.echo("✅ All services stopped")

    except ImportError as e:
        click.echo(f"❌ Required server modules not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start services: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@server.command()
@click.option('--host', default='0.0.0.0',
              help='Server host')
@click.option('--port', type=int, default=8000,
              help='Server port')
@click.option('--reload', is_flag=True,
              help='Enable auto-reload')
@click.option('--debug-toolbar', is_flag=True,
              help='Enable debug toolbar')
@click.pass_context
def dev(ctx, host, port, reload, debug_toolbar):
    """Start development server with hot reload"""

    click.echo(f"🔧 Starting Development Server")
    click.echo(f"   • Host: {host}:{port}")
    click.echo(f"   • Auto-reload: enabled")
    click.echo(f"   • Debug: enabled")

    os.environ['NETINTEL_ENV'] = 'development'

    try:
        from ...api.server import run_api_server

        run_api_server(
            host=host,
            port=port,
            reload=True,
            debug=True,
            debug_toolbar=debug_toolbar,
            embedded_workers=True,
            workers=1
        )

    except ImportError:
        click.echo("❌ API server module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start dev server: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@server.command()
@click.option('--count', type=int, default=4,
              help='Number of workers')
@click.option('--queue', type=click.Choice(['redis', 'rabbitmq', 'sqlite']),
              default='redis',
              help='Queue backend')
@click.option('--concurrency', type=int, default=1,
              help='Concurrent tasks per worker')
@click.option('--embedded', is_flag=True,
              help='Run workers embedded in main process')
@click.pass_context
def worker(ctx, count, queue, concurrency, embedded):
    """Start PDF processing workers"""

    click.echo(f"👷 Starting Workers")
    click.echo(f"   • Count: {count}")
    click.echo(f"   • Queue: {queue}")
    click.echo(f"   • Concurrency: {concurrency} tasks/worker")
    if embedded:
        click.echo(f"   • Mode: Embedded")

    try:
        from ...workers.runner import run_workers

        config = {
            'worker_count': count,
            'queue_backend': queue,
            'concurrency': concurrency,
            'embedded': embedded,
            'debug': ctx.obj.debug if ctx.obj else False
        }

        # Load from config file if available
        if ctx.obj and ctx.obj.config_data:
            worker_config = ctx.obj.config_data.get('server', {}).get('workers', {})
            config.update(worker_config)

        run_workers(**config)

    except ImportError:
        click.echo("❌ Worker module not found.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to start workers: {e}", err=True)
        if ctx.obj and ctx.obj.debug:
            raise
        sys.exit(1)


@server.command()
def status():
    """Show server status"""

    click.echo("📊 Server Status")

    # Check API server
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=2)
        if response.status_code == 200:
            click.echo("   ✅ API Server: Running (port 8000)")
        else:
            click.echo(f"   ⚠️  API Server: Unhealthy ({response.status_code})")
    except:
        click.echo("   ❌ API Server: Not running")

    # Check MCP server
    try:
        import requests
        response = requests.get('http://localhost:8001/health', timeout=2)
        if response.status_code == 200:
            click.echo("   ✅ MCP Server: Running (port 8001)")
        else:
            click.echo(f"   ⚠️  MCP Server: Unhealthy ({response.status_code})")
    except:
        click.echo("   ❌ MCP Server: Not running")

    # Check Redis (queue)
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        queue_size = r.llen('netintel:queue:pdf')
        click.echo(f"   ✅ Redis Queue: Running ({queue_size} pending)")
    except:
        click.echo("   ❌ Redis Queue: Not available")

    # Check workers
    try:
        # This would check worker status from Redis or database
        click.echo("   ℹ️  Workers: Status check not implemented")
    except:
        pass


@server.command()
def health():
    """Check health of all services"""

    click.echo("🏥 Health Check")

    health_status = {
        'api': False,
        'mcp': False,
        'queue': False,
        'database': False
    }

    # Check API
    try:
        import requests
        response = requests.get('http://localhost:8000/health', timeout=2)
        health_data = response.json()
        health_status['api'] = health_data.get('status') == 'healthy'
        status_msg = health_data.get('status', 'unknown') if isinstance(health_data, dict) else str(health_data)
        click.echo(f"   • API: {status_msg}")
    except:
        click.echo("   • API: Cannot connect")

    # Check MCP
    try:
        import requests
        response = requests.get('http://localhost:8001/health', timeout=2)
        health_data = response.json()
        health_status['mcp'] = health_data.get('status') == 'healthy'
        status_msg = health_data.get('status', 'unknown') if isinstance(health_data, dict) else str(health_data)
        click.echo(f"   • MCP: {status_msg}")
    except:
        click.echo("   • MCP: Cannot connect")

    # Overall status
    all_healthy = all(health_status.values())
    if all_healthy:
        click.echo("\n✅ All services healthy")
    else:
        click.echo("\n⚠️  Some services are unhealthy")
        sys.exit(1)


@server.command()
@click.option('--tail', type=int, default=100,
              help='Number of lines to show')
@click.option('--follow', '-f', is_flag=True,
              help='Follow log output')
@click.option('--service', type=click.Choice(['api', 'mcp', 'worker', 'all']),
              default='all',
              help='Service to show logs for')
def logs(tail, follow, service):
    """Show server logs"""

    click.echo(f"📜 Server Logs ({service})")

    log_paths = {
        'api': '/var/log/netintel/api.log',
        'mcp': '/var/log/netintel/mcp.log',
        'worker': '/var/log/netintel/worker.log'
    }

    if service == 'all':
        services = ['api', 'mcp', 'worker']
    else:
        services = [service]

    for svc in services:
        log_path = Path(log_paths[svc])

        if log_path.exists():
            click.echo(f"\n--- {svc.upper()} ---")

            if follow:
                # Use tail -f
                import subprocess
                try:
                    subprocess.run(['tail', '-f', str(log_path)])
                except KeyboardInterrupt:
                    break
            else:
                # Show last N lines
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-tail:]:
                        click.echo(line.rstrip())
        else:
            click.echo(f"\n--- {svc.upper()} ---")
            click.echo(f"   Log file not found: {log_path}")


@server.command()
@click.option('--service', type=click.Choice(['api', 'mcp', 'worker', 'all']),
              default='all',
              help='Service to stop')
@click.option('--force', is_flag=True,
              help='Force stop (kill -9)')
def stop(service, force):
    """Stop server services"""

    click.echo(f"🛑 Stopping {service} service(s)")

    import subprocess
    import signal

    sig = signal.SIGKILL if force else signal.SIGTERM

    if service in ['api', 'all']:
        try:
            subprocess.run(['pkill', '-f', 'netintel.*api'], check=False)
            click.echo("   ✅ API server stopped")
        except:
            click.echo("   ⚠️  Could not stop API server")

    if service in ['mcp', 'all']:
        try:
            subprocess.run(['pkill', '-f', 'netintel.*mcp'], check=False)
            click.echo("   ✅ MCP server stopped")
        except:
            click.echo("   ⚠️  Could not stop MCP server")

    if service in ['worker', 'all']:
        try:
            subprocess.run(['pkill', '-f', 'netintel.*worker'], check=False)
            click.echo("   ✅ Workers stopped")
        except:
            click.echo("   ⚠️  Could not stop workers")