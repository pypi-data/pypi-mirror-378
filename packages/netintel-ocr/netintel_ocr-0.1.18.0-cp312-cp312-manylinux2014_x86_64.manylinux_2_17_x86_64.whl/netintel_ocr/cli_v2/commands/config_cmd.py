"""
Configuration management commands
"""

import click
import json
import os
from pathlib import Path
from typing import Dict, Any


CONFIG_DIR = Path.home() / '.netintel'
CONFIG_FILE = CONFIG_DIR / 'config.json'
PROFILES_DIR = CONFIG_DIR / 'profiles'


@click.group()
def config():
    """Configuration management"""
    pass


@config.command()
@click.option('--template', type=click.Choice([
    'minimal', 'development', 'staging', 'production', 'enterprise', 'cloud'
]), help='Use a configuration template')
@click.option('--output', '-o', type=click.Path(),
              help='Output file (default: ~/.netintel/config.json)')
def init(template, output):
    """Initialize configuration"""

    output_path = Path(output) if output else CONFIG_FILE

    click.echo(f"🎯 Initializing Configuration")

    # Create config directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Load template or create default
    config_data = get_template(template) if template else get_default_config()

    # Save configuration
    with open(output_path, 'w') as f:
        json.dump(config_data, f, indent=2)

    click.echo(f"✅ Configuration created: {output_path}")

    if template:
        click.echo(f"   • Template: {template}")


@config.command()
@click.option('--format', type=click.Choice(['json', 'yaml']),
              default='json', help='Output format')
@click.option('--effective', is_flag=True,
              help='Show effective configuration (merged with defaults)')
def show(format, effective):
    """Show current configuration"""

    if not CONFIG_FILE.exists():
        click.echo("❌ No configuration found. Run 'netintel-ocr config init' first.", err=True)
        return

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    if effective:
        # Merge with defaults
        defaults = get_default_config()
        config_data = deep_merge(defaults, config_data)

    if format == 'yaml':
        try:
            import yaml
            output = yaml.dump(config_data, default_flow_style=False)
        except ImportError:
            click.echo("⚠️  PyYAML not installed, showing JSON format")
            output = json.dumps(config_data, indent=2)
    else:
        output = json.dumps(config_data, indent=2)

    click.echo(output)


@config.command()
@click.argument('config_file', type=click.Path(exists=True))
def load(config_file):
    """Load configuration from file"""

    click.echo(f"📥 Loading configuration: {config_file}")

    # Validate configuration
    with open(config_file, 'r') as f:
        config_data = json.load(f)

    # Save as current config
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

    click.echo("✅ Configuration loaded")


@config.command()
@click.argument('config_file', type=click.Path(exists=True))
def use(config_file):
    """Set configuration as default"""

    click.echo(f"📌 Setting default configuration: {config_file}")

    # Copy to default location
    import shutil
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(config_file, CONFIG_FILE)

    click.echo("✅ Configuration set as default")


@config.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate(config_file):
    """Validate configuration file"""

    click.echo(f"🔍 Validating: {config_file}")

    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)

        # Check required fields
        required = ['version', 'models', 'server', 'database']
        missing = [r for r in required if r not in config_data]

        if missing:
            click.echo(f"❌ Missing required fields: {', '.join(missing)}", err=True)
            return

        # Validate version
        if config_data['version'] not in ['0.1.17', '0.1.17.1']:
            click.echo(f"⚠️  Version mismatch: {config_data['version']} (expected 0.1.17.1)")

        click.echo("✅ Configuration is valid")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)


@config.command()
@click.argument('key')
def get(key):
    """Get configuration value"""

    if not CONFIG_FILE.exists():
        click.echo("❌ No configuration found", err=True)
        return

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    # Navigate nested keys
    value = config_data
    for k in key.split('.'):
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            click.echo(f"❌ Key not found: {key}", err=True)
            return

    if isinstance(value, (dict, list)):
        click.echo(json.dumps(value, indent=2))
    else:
        click.echo(value)


@config.command()
@click.argument('key')
@click.argument('value')
def set(key, value):
    """Set configuration value"""

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Load existing config or create new
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            config_data = json.load(f)
    else:
        config_data = {}

    # Parse value
    try:
        # Try to parse as JSON first
        parsed_value = json.loads(value)
    except:
        # Keep as string
        parsed_value = value

    # Navigate and set nested keys
    keys = key.split('.')
    current = config_data

    for k in keys[:-1]:
        if k not in current:
            current[k] = {}
        current = current[k]

    current[keys[-1]] = parsed_value

    # Save configuration
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

    click.echo(f"✅ Set {key} = {parsed_value}")


@config.command()
@click.argument('key')
def unset(key):
    """Unset configuration value"""

    if not CONFIG_FILE.exists():
        click.echo("❌ No configuration found", err=True)
        return

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    # Navigate and delete nested keys
    keys = key.split('.')
    current = config_data

    for k in keys[:-1]:
        if k in current:
            current = current[k]
        else:
            click.echo(f"❌ Key not found: {key}", err=True)
            return

    if keys[-1] in current:
        del current[keys[-1]]
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
        click.echo(f"✅ Unset {key}")
    else:
        click.echo(f"❌ Key not found: {key}", err=True)


# Profile commands
@config.group()
def profile():
    """Configuration profiles"""
    pass


@profile.command(name='list')
def profile_list():
    """List configuration profiles"""

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profiles = list(PROFILES_DIR.glob('*.json'))

    if not profiles:
        click.echo("No profiles found")
        return

    click.echo("📁 Configuration Profiles:")
    for p in profiles:
        name = p.stem
        # Check if it's the current profile
        is_current = CONFIG_FILE.exists() and CONFIG_FILE.samefile(p)
        marker = " (current)" if is_current else ""
        click.echo(f"   • {name}{marker}")


@profile.command()
@click.argument('name')
def create(name):
    """Create new profile"""

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    profile_path = PROFILES_DIR / f"{name}.json"

    if profile_path.exists():
        click.echo(f"❌ Profile '{name}' already exists", err=True)
        return

    # Copy current config or create default
    if CONFIG_FILE.exists():
        import shutil
        shutil.copy2(CONFIG_FILE, profile_path)
    else:
        config_data = get_default_config()
        with open(profile_path, 'w') as f:
            json.dump(config_data, f, indent=2)

    click.echo(f"✅ Profile created: {name}")


@profile.command(name='use')
@click.argument('name')
def profile_use(name):
    """Switch to profile"""

    profile_path = PROFILES_DIR / f"{name}.json"

    if not profile_path.exists():
        click.echo(f"❌ Profile '{name}' not found", err=True)
        return

    import shutil
    shutil.copy2(profile_path, CONFIG_FILE)

    click.echo(f"✅ Switched to profile: {name}")


@profile.command(name='export')
@click.argument('name')
@click.option('--output', '-o', type=click.Path(),
              required=True, help='Output file')
def profile_export(name, output):
    """Export profile to file"""

    profile_path = PROFILES_DIR / f"{name}.json"

    if not profile_path.exists():
        click.echo(f"❌ Profile '{name}' not found", err=True)
        return

    import shutil
    shutil.copy2(profile_path, output)

    click.echo(f"✅ Profile exported: {output}")


@profile.command(name='import')
@click.argument('file', type=click.Path(exists=True))
@click.option('--name', help='Profile name (default: filename)')
def profile_import(file, name):
    """Import profile from file"""

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)

    if not name:
        name = Path(file).stem

    profile_path = PROFILES_DIR / f"{name}.json"

    import shutil
    shutil.copy2(file, profile_path)

    click.echo(f"✅ Profile imported: {name}")


# Utility commands
@config.command()
@click.argument('base_config', type=click.Path(exists=True))
@click.argument('custom_config', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              required=True, help='Output file')
def merge(base_config, custom_config, output):
    """Merge two configuration files"""

    with open(base_config, 'r') as f:
        base_data = json.load(f)

    with open(custom_config, 'r') as f:
        custom_data = json.load(f)

    merged = deep_merge(base_data, custom_data)

    with open(output, 'w') as f:
        json.dump(merged, f, indent=2)

    click.echo(f"✅ Configurations merged: {output}")


@config.command()
@click.argument('config1', type=click.Path(exists=True))
@click.argument('config2', type=click.Path(exists=True))
def diff(config1, config2):
    """Show differences between configurations"""

    with open(config1, 'r') as f:
        data1 = json.load(f)

    with open(config2, 'r') as f:
        data2 = json.load(f)

    diffs = find_differences(data1, data2)

    if not diffs:
        click.echo("✅ Configurations are identical")
    else:
        click.echo("📊 Configuration Differences:")
        for key, (val1, val2) in diffs.items():
            click.echo(f"\n{key}:")
            click.echo(f"  {config1}: {val1}")
            click.echo(f"  {config2}: {val2}")


# Template commands
@config.group()
def template():
    """Configuration templates"""
    pass


@template.command(name='list')
def template_list():
    """List available templates"""

    # Try to load from template directory first
    template_dir = Path(__file__).parent.parent / 'templates'
    templates = []

    if template_dir.exists():
        for template_file in sorted(template_dir.glob('*.json')):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                    name = template_file.stem
                    desc = data.get('description', 'No description')
                    templates.append((name, desc))
            except:
                pass

    # Add hardcoded templates if no file templates found
    if not templates:
        templates = [
            ('minimal', 'Single-user local setup'),
            ('development', 'Development environment'),
            ('staging', 'Staging server configuration'),
            ('production', 'Production deployment'),
            ('enterprise', 'Full enterprise features'),
            ('cloud', 'Cloud-native deployment')
        ]

    click.echo("📋 Available Templates:")
    for name, desc in templates:
        click.echo(f"   • {name}: {desc}")


@template.command(name='show')
@click.argument('name')
def template_show(name):
    """Show template configuration"""

    template_data = get_template(name)
    if template_data:
        click.echo(json.dumps(template_data, indent=2))
    else:
        click.echo(f"❌ Template '{name}' not found", err=True)


@template.command(name='apply')
@click.argument('name')
@click.option('--output', '-o', type=click.Path(),
              required=True, help='Output file')
def template_apply(name, output):
    """Apply template to create configuration"""

    template_data = get_template(name)
    if not template_data:
        click.echo(f"❌ Template '{name}' not found", err=True)
        return

    with open(output, 'w') as f:
        json.dump(template_data, f, indent=2)

    click.echo(f"✅ Template applied: {output}")


# Environment variable commands
@config.group()
def env():
    """Environment variable management"""
    pass


@env.command(name='export')
@click.option('--output', '-o', type=click.Path(),
              help='Output file (default: stdout)')
def env_export(output):
    """Export configuration as environment variables"""

    if not CONFIG_FILE.exists():
        click.echo("❌ No configuration found", err=True)
        return

    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    env_vars = config_to_env(config_data)

    if output:
        with open(output, 'w') as f:
            for key, value in env_vars.items():
                f.write(f"export {key}={value}\n")
        click.echo(f"✅ Environment variables exported: {output}")
    else:
        for key, value in env_vars.items():
            click.echo(f"export {key}={value}")


@env.command(name='generate')
@click.option('--from', 'config_file', type=click.Path(exists=True),
              help='Configuration file')
@click.option('--output', '-o', type=click.Path(),
              default='.env',
              help='Output file path (default: .env)')
def env_generate(config_file, output):
    """Generate .env file from configuration"""

    config_path = Path(config_file) if config_file else CONFIG_FILE

    if not config_path.exists():
        click.echo("❌ Configuration file not found", err=True)
        return

    with open(config_path, 'r') as f:
        config_data = json.load(f)

    env_vars = config_to_env(config_data)

    output_path = Path(output)
    with open(output_path, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

    click.echo(f"✅ Generated environment file: {output_path}")


# Helper functions
def get_default_config() -> Dict[str, Any]:
    """Get default configuration"""
    return {
        "version": "0.1.17.1",
        "name": "default",
        "models": {
            "ocr": "llava:latest",
            "network": "yolo:latest",
            "embedding": "nomic-embed-text",
            "llm": "gemma3:4b"
        },
        "server": {
            "api": {"host": "0.0.0.0", "port": 8000},
            "mcp": {"host": "0.0.0.0", "port": 8001},
            "workers": {"count": 4}
        },
        "database": {
            "path": "/var/lib/netintel/db",
            "vector": {
                "backend": "milvus",
                "host": "localhost",
                "port": 19530
            }
        },
        "processing": {
            "batch_size": 10,
            "parallel": True
        }
    }


def get_template(name: str) -> Dict[str, Any]:
    """Get configuration template"""
    # Try to load from template files first
    import os
    template_dir = Path(__file__).parent.parent / 'templates'
    template_file = template_dir / f"{name}.json"

    if template_file.exists():
        try:
            with open(template_file, 'r') as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback to hardcoded templates
    templates = {
        'minimal': {
            "version": "0.1.17.1",
            "name": "minimal",
            "models": {"ocr": "llava:latest"},
            "server": {"api": {"port": 8000}},
            "database": {"type": "sqlite"}
        },
        'production': {
            "version": "0.1.17.1",
            "name": "production",
            "models": {
                "ocr": "llava:13b",
                "network": "yolo:latest",
                "embedding": "nomic-embed-text"
            },
            "server": {
                "api": {"host": "0.0.0.0", "port": 8000, "workers": 8},
                "mcp": {"host": "0.0.0.0", "port": 8001}
            },
            "database": {
                "type": "postgresql",
                "vector": {"backend": "milvus"}
            },
            "monitoring": {"enabled": True}
        }
    }
    return templates.get(name)


def deep_merge(base: Dict, custom: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = base.copy()
    for key, value in custom.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def find_differences(dict1: Dict, dict2: Dict, prefix: str = "") -> Dict:
    """Find differences between two dictionaries"""
    diffs = {}
    all_keys = set(dict1.keys()) | set(dict2.keys())

    for key in all_keys:
        full_key = f"{prefix}.{key}" if prefix else key
        val1 = dict1.get(key)
        val2 = dict2.get(key)

        if val1 != val2:
            if isinstance(val1, dict) and isinstance(val2, dict):
                nested_diffs = find_differences(val1, val2, full_key)
                diffs.update(nested_diffs)
            else:
                diffs[full_key] = (val1, val2)

    return diffs


def config_to_env(config: Dict, prefix: str = "NETINTEL") -> Dict[str, str]:
    """Convert configuration to environment variables"""
    env_vars = {}

    def flatten(obj, parent_key=''):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{parent_key}_{key.upper()}" if parent_key else f"{prefix}_{key.upper()}"
                flatten(value, new_key)
        elif isinstance(obj, list):
            env_vars[parent_key] = json.dumps(obj)
        else:
            env_vars[parent_key] = str(obj)

    flatten(config)
    return env_vars


@config.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--strict', is_flag=True, help='Strict validation mode')
def validate(config_file, strict):
    """Validate configuration file"""
    click.echo(f"🔍 Validating configuration: {config_file}")

    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)

        # Basic validation checks
        errors = []
        warnings = []

        # Check required fields
        required_fields = ['version', 'models']
        for field in required_fields:
            if field not in config_data:
                errors.append(f"Missing required field: {field}")

        # Check model configuration
        if 'models' in config_data:
            if 'ocr' not in config_data['models']:
                warnings.append("No OCR model configured")
            if 'network' not in config_data['models']:
                warnings.append("No network model configured")

        # Check paths exist
        if 'storage' in config_data:
            for key, path in config_data['storage'].items():
                if not Path(path).exists():
                    warnings.append(f"Path does not exist: {key}={path}")

        # Display results
        if errors:
            click.echo("\n❌ Validation failed:")
            for error in errors:
                click.echo(f"   • {error}")
            sys.exit(1)
        elif warnings and strict:
            click.echo("\n⚠️  Warnings found:")
            for warning in warnings:
                click.echo(f"   • {warning}")
            sys.exit(1)
        elif warnings:
            click.echo("\n⚠️  Warnings:")
            for warning in warnings:
                click.echo(f"   • {warning}")
            click.echo("\n✅ Configuration is valid (with warnings)")
        else:
            click.echo("✅ Configuration is valid")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}", err=True)
        sys.exit(1)


@config.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--fix', is_flag=True, help='Auto-fix issues')
@click.option('--output', '-o', type=click.Path(), help='Output file for fixed config')
def lint(config_file, fix, output):
    """Lint and format configuration file"""
    click.echo(f"🔧 Linting configuration: {config_file}")

    try:
        with open(config_file, 'r') as f:
            config_data = json.load(f)

        issues_found = False
        fixes_applied = []

        # Check and fix formatting
        original = json.dumps(config_data)
        formatted = json.dumps(config_data, indent=2, sort_keys=True)

        if original != formatted:
            issues_found = True
            if fix:
                fixes_applied.append("Formatted JSON with proper indentation")

        # Add default values for missing optional fields
        defaults = {
            'debug': False,
            'verbose': False,
            'parallel': 4,
            'timeout': 300
        }

        for key, value in defaults.items():
            if key not in config_data:
                issues_found = True
                if fix:
                    config_data[key] = value
                    fixes_applied.append(f"Added default value for '{key}'")

        # Save fixed config if requested
        if fix and issues_found:
            output_file = output or config_file
            with open(output_file, 'w') as f:
                json.dump(config_data, f, indent=2, sort_keys=True)

            click.echo("\n✅ Fixed issues:")
            for fix_msg in fixes_applied:
                click.echo(f"   • {fix_msg}")
            click.echo(f"\n💾 Saved to: {output_file}")
        elif issues_found:
            click.echo("\n⚠️  Issues found (use --fix to auto-fix):")
            click.echo("   • Formatting inconsistencies")
            click.echo("   • Missing optional fields")
        else:
            click.echo("✅ Configuration is properly formatted")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Lint failed: {e}", err=True)
        sys.exit(1)