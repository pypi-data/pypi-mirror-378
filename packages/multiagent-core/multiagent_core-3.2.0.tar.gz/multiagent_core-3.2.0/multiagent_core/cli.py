"""Multi-Agent Core CLI

Command-line interface for the multi-agent development framework.
"""

from __future__ import annotations

import click
import json
import os
import subprocess
import tempfile
import requests
import glob
try:
    from importlib import metadata
except ImportError:
    import importlib_metadata as metadata
import pkg_resources  # Still needed for resource files
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from shutil import which
from .config import config
# Docker imports removed - using simple file operations instead
from .detector import ProjectDetector
from .analyzer import TechStackAnalyzer
from .env_generator import EnvironmentGenerator
from .templates import TemplateManager
from . import __version__

console = Console()

@click.group()
@click.version_option(__version__)
def main():
    """Multi-Agent Development Framework CLI"""
    # Auto-detect WSL environment and warn if using wrong Python
    _check_python_environment()
    # Check for updates on every command (non-blocking)
    _check_for_updates_async()
    pass

@main.command()
@click.argument('path', type=click.Path(), required=False)
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--create-repo', is_flag=True, help='Create a GitHub repository')
@click.option('--interactive/--no-interactive', default=True, help='Use interactive prompts to configure initialization')
def init(path, dry_run, create_repo, interactive):
    """Initialize multi-agent framework in a new or existing directory."""
    if path:
        target_path = Path(path).resolve()
        try:
            target_path.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            console.print(f"[red]Error creating directory {target_path}: {e}[/red]")
            return
    else:
        target_path = Path.cwd()

    # Change current working directory to the target path
    os.chdir(target_path)
    cwd = target_path

    if dry_run:
        console.print("[bold blue]Dry run mode - no changes will be made[/bold blue]")

    console.print(f"Initializing multi-agent framework in: {cwd}")

    # Interactive setup prompts
    if not dry_run and interactive:
        # Check if existing git repository
        git_exists = (cwd / ".git").exists()
        if git_exists:
            use_existing_git = click.confirm("Existing git repository detected. Use existing repository?", default=True)
        else:
            use_existing_git = False

        # GitHub repository creation
        create_github = create_repo or click.confirm("Create GitHub repository?", default=False)

        # Git hooks installation
        install_git_hooks = click.confirm("Install git hooks for multi-agent workflow?", default=True)
    else:
        # Non-interactive defaults
        git_exists = (cwd / ".git").exists()
        use_existing_git = git_exists
        create_github = create_repo
        install_git_hooks = True

    # Copy framework structure from package
    if not dry_run:
        success = _generate_project_structure(cwd)
        if not success:
            console.print("[red]Framework initialization failed[/red]")
            return

        console.print("[green]Core framework initialized[/green]")

    # Handle git repository setup FIRST
    if not dry_run and not use_existing_git:
        console.print("Initializing git repository...")
        try:
            subprocess.run(['git', 'init'], cwd=str(cwd), check=True)
            # Handle git ownership issues in WSL/Windows
            try:
                subprocess.run(['git', 'config', '--global', '--add', 'safe.directory', str(cwd)],
                             capture_output=True, text=True)
            except:
                pass  # Non-critical if this fails
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Git initialization failed: {e}[/yellow]")

    # Handle git hooks installation (after git is initialized)
    if not dry_run and install_git_hooks:
        _install_git_hooks(cwd)

    # Create an initial commit before creating the repo
    if not dry_run and not use_existing_git:
        try:
            subprocess.run(['git', 'add', '.'], cwd=str(cwd), check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=str(cwd), check=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[yellow]Warning: Initial commit failed: {e}[/yellow]")

    # Handle GitHub repository creation
    if not dry_run and create_github:
        _create_github_repo(cwd)

    # Recommend additional components based on detected CLIs and project structure
    if not dry_run:
        _recommend_additional_components(cwd)

    # Auto-generate smart environment configuration
    if not dry_run:
        console.print("\n[bold blue]Smart Environment Detection[/bold blue]")
        try:
            detector = ProjectDetector(cwd)
            project_info = detector.detect()

            if project_info.project_type != 'unknown':
                console.print(f"Detected: [cyan]{project_info.project_type}[/cyan] project")

                if project_info.frameworks:
                    console.print(f"Frameworks: [cyan]{', '.join(list(project_info.frameworks)[:3])}[/cyan]")

            else:
                console.print("[dim]Unknown project type - skipping auto environment detection[/dim]")
        except Exception as e:
            console.print(f"[yellow]Warning: Environment detection failed: {e}[/yellow]")

    console.print("[green]Multi-agent framework initialization complete![/green]")

def _install_component(component, multiagent_dir, dry_run):
    """Install a specific component with intelligent directory merging"""
    console.print(f"Installing component: {component}")

    if not dry_run:
        # Create component-specific directories
        github_dir = Path.cwd() / ".github" / "workflows" / component
        github_dir.mkdir(parents=True, exist_ok=True)

        claude_dir = Path.cwd() / ".claude" / component
        claude_dir.mkdir(parents=True, exist_ok=True)

        # Update components registry
        components_file = multiagent_dir / "components.json"
        if components_file.exists():
            with open(components_file, 'r') as f:
                registry = json.load(f)

            registry[component] = {"version": "0.1.0", "installed": True}
            if component not in registry.get("installation_order", []):
                registry.setdefault("installation_order", []).append(component)

            with open(components_file, 'w') as f:
                json.dump(registry, f, indent=2)

    console.print(f"[green]Component {component} installed with intelligent directory merging[/green]")

@main.command()
def status():
    """Show installation status and component information"""
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if not multiagent_dir.exists():
        console.print("[red]Multi-agent framework not initialized in this directory[/red]")
        console.print("Run 'multiagent init' to get started")
        return

    # Read components registry
    components_file = multiagent_dir / "components.json"
    if components_file.exists():
        with open(components_file, 'r') as f:
            registry = json.load(f)

        table = Table(title="Multi-Agent Framework Status")
        table.add_column("Component", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Status", style="green")

        # Handle both old and new component.json formats
        components = registry.get("components", registry)

        for component, info in components.items():
            # Skip metadata keys
            if component in ["installation_order", "framework_version"]:
                continue

            # Ensure info is a dictionary before accessing
            if isinstance(info, dict):
                status = "[green]Installed[/green]" if info.get("installed", False) else "[red]Not installed[/red]"
                version = info.get("version", "unknown")
                table.add_row(component, version, status)
            elif isinstance(info, str):
                # Legacy format where info is just a version string
                table.add_row(component, info, "[yellow]Legacy format[/yellow]")
            else:
                # Fallback for any other format
                table.add_row(component, str(info), "[yellow]Unknown format[/yellow]")

        console.print(table)

        install_order = registry.get("installation_order", [])
        if install_order:
            console.print(f"\nInstallation order: {' -> '.join(install_order)}")
    else:
        console.print("[yellow]WARNING: No components registry found[/yellow]")

@main.command()
@click.argument('component')
def uninstall(component):
    """Remove a component from the framework"""
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if not multiagent_dir.exists():
        console.print("[red]ERROR: Multi-agent framework not initialized[/red]")
        return

    console.print(f"Removing component: {component}")

    # Update registry
    components_file = multiagent_dir / "components.json"
    if components_file.exists():
        with open(components_file, 'r') as f:
            registry = json.load(f)

        if component in registry:
            del registry[component]
            if component in registry.get("installation_order", []):
                registry["installation_order"].remove(component)

            with open(components_file, 'w') as f:
                json.dump(registry, f, indent=2)

            console.print(f"[green]Component {component} removed[/green]")
        else:
            console.print(f"[red]ERROR: Component {component} not found[/red]")

@main.command()
def upgrade():
    """Check for and install updates for all multiagent packages"""
    packages = [
        'multiagent-core',
        'multiagent-agentswarm',
        'multiagent-devops',
        'multiagent-testing'
    ]

    console.print("[bold blue]Checking for multiagent package updates...[/bold blue]")

    updates_available = []
    for package in packages:
        try:
            current_version = metadata.version(package)
            latest_version = _get_latest_version(package)

            if latest_version and current_version != latest_version:
                updates_available.append((package, current_version, latest_version))
                console.print(f"[yellow]{package}: {current_version} -> {latest_version}[/yellow]")
            else:
                console.print(f"[green]{package}: {current_version} (up to date)[/green]")
        except metadata.PackageNotFoundError:
            console.print(f"[dim]{package}: not installed[/dim]")

    if updates_available:
        console.print(f"\n[bold yellow]{len(updates_available)} package(s) have updates available[/bold yellow]")

        if click.confirm("Install updates?"):
            for package, current, latest in updates_available:
                console.print(f"Upgrading {package}...")
                try:
                    # Try pipx first, fall back to pip
                    pipx_result = subprocess.run(['pipx', 'upgrade', package],
                                               capture_output=True, text=True)

                    if pipx_result.returncode == 0:
                        console.print(f"[green]{package} upgraded successfully via pipx[/green]")
                        continue

                    # Fall back to pip with appropriate flags
                    pip_cmd = ['pip', 'install', '--upgrade', package]

                    # Try without --break-system-packages first
                    result = subprocess.run(pip_cmd, capture_output=True, text=True)

                    if result.returncode != 0 and "externally-managed-environment" in result.stderr:
                        # Ubuntu 24+ needs --break-system-packages
                        pip_cmd.append('--break-system-packages')
                        result = subprocess.run(pip_cmd, capture_output=True, text=True)

                    if result.returncode == 0:
                        console.print(f"[green]{package} upgraded successfully via pip[/green]")
                    else:
                        console.print(f"[red]Failed to upgrade {package}: {result.stderr}[/red]")
                        console.print(f"[yellow]Try: pipx upgrade {package}[/yellow]")
                except Exception as e:
                    console.print(f"[red]Error upgrading {package}: {e}[/red]")
    else:
        console.print("[green]All packages are up to date![/green]")

@main.command()
def config_show():
    """Show current configuration"""
    console.print("[bold blue]MultiAgent Core Configuration[/bold blue]\n")

    # Core settings
    console.print("[bold]Core Settings:[/bold]")
    console.print(f"Debug: {config.debug}")
    console.print(f"Log Level: {config.log_level}")
    console.print(f"Development Mode: {config.development_mode}")
    console.print(f"Interactive: {config.interactive}")

    # GitHub settings
    console.print("\n[bold]GitHub Settings:[/bold]")
    console.print(f"GitHub Token: {'[green]Set[/green]' if config.github_token else '[red]Not set[/red]'}")
    console.print(f"GitHub Username: {config.github_username or '[red]Not set[/red]'}")

    # Docker settings
    console.print("\n[bold]Docker Settings:[/bold]")
    console.print(f"Docker Host: {config.docker_host}")
    console.print(f"Force Docker: {config.force_docker}")
    console.print(f"Docker Timeout: {config.docker_timeout}s")

    # WSL/Windows settings
    console.print("\n[bold]WSL/Windows Settings:[/bold]")
    console.print(f"Auto Convert Paths: {config.wsl_auto_convert_paths}")

    # Component defaults
    console.print("\n[bold]Component Installation Defaults:[/bold]")
    console.print(f"DevOps: {config.get_bool('default_install_devops', True)}")
    console.print(f"Testing: {config.get_bool('default_install_testing', True)}")
    console.print(f"AgentSwarm: {config.get_bool('default_install_agentswarm', False)}")

    console.print(f"\n[dim]Configuration loaded from .env file and environment variables[/dim]")
    console.print(f"[dim]Copy .env.example to .env to customize settings[/dim]")

@main.command()
def detect():
    """Detect project structure and tech stack"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Analyzing project structure in: {cwd}[/bold blue]\n")

    # Run detection
    detector = ProjectDetector(cwd)
    project_info = detector.detect()

    # Display results
    console.print("[bold]Project Detection Results:[/bold]")
    console.print(f"Project Type: [cyan]{project_info.project_type}[/cyan]")
    console.print(f"Language: [cyan]{project_info.language}[/cyan]")
    console.print(f"Structure: [cyan]{project_info.structure}[/cyan]")

    if project_info.frameworks:
        console.print(f"Frameworks: [cyan]{', '.join(project_info.frameworks)}[/cyan]")

    console.print(f"\n[bold]Components:[/bold]")
    console.print(f"Backend: {'[green]Yes[/green]' if project_info.has_backend else '[red]No[/red]'}")
    console.print(f"Frontend: {'[green]Yes[/green]' if project_info.has_frontend else '[red]No[/red]'}")
    console.print(f"Database: {'[green]Yes[/green]' if project_info.has_database else '[red]No[/red]'}")

    if project_info.deployment_target:
        console.print(f"Deployment Target: [cyan]{project_info.deployment_target}[/cyan]")

    console.print(f"\n[dim]Found {len(project_info.config_files)} configuration files[/dim]")

@main.command()
def env_detect():
    """Analyze environment requirements for current project"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Analyzing environment requirements in: {cwd}[/bold blue]\n")

    # Run detection and analysis
    detector = ProjectDetector(cwd)
    analyzer = TechStackAnalyzer(detector)
    env_summary = analyzer.get_environment_summary()

    # Display summary
    console.print("[bold]Environment Requirements Summary:[/bold]")
    console.print(f"Total Services: [cyan]{env_summary['total_services']}[/cyan]")
    console.print(f"Required Environment Variables: [cyan]{env_summary['required_env_vars']}[/cyan]")
    console.print(f"Optional Environment Variables: [cyan]{env_summary['optional_env_vars']}[/cyan]")

    if env_summary['service_categories']:
        console.print(f"Service Categories: [cyan]{', '.join(env_summary['service_categories'])}[/cyan]")

    # Show services by category
    if env_summary['services_by_category']:
        console.print("\n[bold]Required Services:[/bold]")
        for category, services in env_summary['services_by_category'].items():
            console.print(f"  {category}: {', '.join(services)}")

    # Show requirements
    env_reqs = analyzer.analyze()
    if env_reqs.database_requirements:
        console.print("\n[bold]Database Setup Needed:[/bold]")
        for req in env_reqs.database_requirements:
            console.print(f"  • {req}")

    if env_reqs.deployment_requirements:
        console.print("\n[bold]Deployment Setup Needed:[/bold]")
        for req in env_reqs.deployment_requirements:
            console.print(f"  • {req}")

@main.command()
@click.option('--interactive/--no-interactive', default=True, help='Run interactive configuration')
@click.option('--template', help='Use specific template instead of auto-detection')
def env_init(interactive, template):
    """Generate smart environment configuration"""
    cwd = Path.cwd()
    console.print(f"[bold blue]Generating environment configuration for: {cwd}[/bold blue]\n")

    # Run detection and analysis
    detector = ProjectDetector(cwd)
    project_info = detector.detect()
    analyzer = TechStackAnalyzer(detector)
    generator = EnvironmentGenerator(analyzer)

    console.print(f"Detected: [cyan]{project_info.project_type}[/cyan] project with [cyan]{project_info.language}[/cyan]")

    if project_info.frameworks:
        console.print(f"Frameworks: [cyan]{', '.join(project_info.frameworks)}[/cyan]")

    # Check if template specified
    if template:
        template_manager = TemplateManager()
        project_template = template_manager.get_template(template)
        if not project_template:
            console.print(f"[red]Template '{template}' not found[/red]")
            console.print("Available templates:")
            for tmpl in template_manager.list_templates():
                console.print(f"  • {tmpl['name']}: {tmpl['description']}")
            return
        console.print(f"Using template: [cyan]{project_template.name}[/cyan]")
    else:
        console.print("Auto-detecting best configuration...")

    # Generate environment files
    try:
        env_example_path, env_template_path = generator.write_env_files(cwd)
        console.print(f"\n[green]Environment files generated:[/green]")
        console.print(f"  • {env_example_path.name} (for git repository)")
        console.print(f"  • {env_template_path.name} (with example values)")

        if interactive:
            console.print("\n[bold]Interactive Configuration:[/bold]")
            prompts = generator.generate_interactive_prompts()
            env_values = {}

            current_category = None
            for prompt in prompts:
                if prompt['type'] == 'category_header':
                    if current_category:
                        console.print()  # Add spacing between categories
                    current_category = prompt['category']
                    console.print(f"\n[bold cyan]{prompt['category']}[/bold cyan]")
                    console.print(f"[dim]{prompt['description']}[/dim]")
                elif prompt['type'] == 'input':
                    description = prompt['description']
                    if prompt.get('example'):
                        description += f" [dim](e.g., {prompt['example']})[/dim]"

                    if prompt['required']:
                        value = Prompt.ask(f"  {prompt['name']}", default="")
                        if value.strip():
                            env_values[prompt['name']] = value.strip()
                    else:
                        value = Prompt.ask(f"  {prompt['name']} [dim](optional)[/dim]", default="")
                        if value.strip():
                            env_values[prompt['name']] = value.strip()

            # Write .env file with user values
            if env_values:
                env_path = cwd / '.env'
                if env_path.exists():
                    if not Confirm.ask(f".env file already exists. Overwrite?"):
                        console.print("[yellow]Environment configuration cancelled[/yellow]")
                        return

                # Generate final .env content
                with open(env_template_path) as f:
                    env_content = f.read()

                # Replace values in template
                for var_name, var_value in env_values.items():
                    env_content = env_content.replace(f'{var_name}=', f'{var_name}={var_value}')

                with open(env_path, 'w') as f:
                    f.write(env_content)

                console.print(f"\n[green].env file created with your configuration![/green]")

                # Validate configuration
                errors = generator.validate_environment(env_values)
                if errors:
                    console.print("\n[yellow]Configuration warnings:[/yellow]")
                    for error in errors:
                        console.print(f"  • {error}")
                else:
                    console.print("[green]Environment configuration is valid[/green]")

        # Show setup instructions
        setup_instructions = generator.get_setup_instructions()
        if setup_instructions:
            console.print("\n[bold]Next Steps - Service Setup:[/bold]")
            for i, instruction in enumerate(setup_instructions, 1):
                console.print(f"  {i}. {instruction}")

    except Exception as e:
        console.print(f"[red]Error generating environment configuration: {e}[/red]")

@main.command()
def env_validate():
    """Validate current environment configuration"""
    cwd = Path.cwd()
    env_path = cwd / '.env'

    if not env_path.exists():
        console.print("[red].env file not found[/red]")
        console.print("Run 'multiagent env-init' to generate environment configuration")
        return

    console.print(f"[bold blue]Validating environment configuration in: {cwd}[/bold blue]\n")

    # Load current environment
    env_vars = {}
    try:
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except Exception as e:
        console.print(f"[red]Error reading .env file: {e}[/red]")
        return

    # Run validation
    detector = ProjectDetector(cwd)
    analyzer = TechStackAnalyzer(detector)
    generator = EnvironmentGenerator(analyzer)

    errors = generator.validate_environment(env_vars)

    if errors:
        console.print("[red]Environment validation failed:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        console.print(f"\nRun 'multiagent env-init --interactive' to fix configuration")
    else:
        console.print("[green]Environment configuration is valid![/green]")
        console.print(f"Found {len(env_vars)} configured variables")

@main.command()
def env_templates():
    """List available environment templates"""
    template_manager = TemplateManager()
    templates = template_manager.list_templates()

    console.print("[bold blue]Available Environment Templates:[/bold blue]\n")

    table = Table()
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Frameworks", style="dim")

    for template in templates:
        table.add_row(template['name'], template['description'], template['frameworks'])

    console.print(table)
    console.print("\nUse: [cyan]multiagent env-init --template <name>[/cyan] to use a specific template")

@main.command()
def version_info():
    """Show detailed version information"""
    console.print(f"[bold blue]MultiAgent Core Version Information[/bold blue]\n")
    
    # Read VERSION file for detailed info
    cwd = Path.cwd()
    version_files = [
        cwd / 'VERSION',
        Path.home() / '.multiagent' / 'VERSION',
        Path(__file__).parent / 'VERSION'
    ]
    
    version_data = None
    for version_file in version_files:
        if version_file.exists():
            try:
                with open(version_file) as f:
                    version_data = json.load(f)
                break
            except:
                continue
    
    if version_data:
        console.print(f"Version: [cyan]{version_data.get('version', 'unknown')}[/cyan]")
        console.print(f"Commit: [dim]{version_data.get('commit', 'unknown')}[/dim]")
        console.print(f"Build Date: [dim]{version_data.get('build_date', 'unknown')}[/dim]")
        console.print(f"Build Type: [dim]{version_data.get('build_type', 'unknown')}[/dim]")
    else:
        console.print(f"Version: [cyan]{__version__}[/cyan]")
        console.print("[dim]No detailed version information available[/dim]")
    
    console.print(f"\nInstallation: [cyan]pipx upgrade multiagent-core[/cyan] to update")

@main.command()
def doctor():
    """Comprehensive environment and package health check"""
    console.print("[bold blue]Multi-Agent Environment Health Check[/bold blue]\n")

    # Check Python version
    import sys
    console.print(f"Python: {sys.version.split()[0]}")

    # Check installed packages and versions
    packages = ['multiagent-core', 'multiagent-agentswarm', 'multiagent-devops', 'multiagent-testing']

    table = Table(title="Package Status")
    table.add_column("Package", style="cyan")
    table.add_column("Installed", style="green")
    table.add_column("Latest", style="yellow")
    table.add_column("Status", style="bold")

    for package in packages:
        try:
            current = metadata.version(package)
            latest = _get_latest_version(package)

            if latest and current != latest:
                status = "[red]Update Available[/red]"
            else:
                status = "[green]Up to Date[/green]"

            table.add_row(package, current, latest or "Unknown", status)
        except metadata.PackageNotFoundError:
            table.add_row(package, "[red]Not Installed[/red]", "Unknown", "[red]Missing[/red]")

    console.print(table)

    # Check available AI CLIs
    console.print("\n[bold]AI Assistant CLI Status:[/bold]")
    ai_status = _detect_available_clis()
    for cli, status in ai_status.items():
        if status['available']:
            console.print(f"{cli}: [green]{status['version']}[/green]")
        else:
            console.print(f"{cli}: [red]Not available[/red]")

    # Check GitHub CLI
    console.print("\n[bold]GitHub CLI Status:[/bold]")
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split()[2] if len(result.stdout.split()) > 2 else "unknown"
            console.print(f"GitHub CLI: [green]{version}[/green]")
        else:
            console.print("[red]GitHub CLI: Not found[/red]")
    except FileNotFoundError:
        console.print("[red]GitHub CLI: Not installed[/red]")

    # Check framework status
    console.print("\n[bold]Framework Status:[/bold]")
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"

    if multiagent_dir.exists():
        console.print("[green]Framework: Initialized[/green]")
        components_file = multiagent_dir / "components.json"
        if components_file.exists():
            with open(components_file, 'r') as f:
                registry = json.load(f)
            console.print(f"Components: {', '.join(registry.get('installation_order', []))}")
        else:
            console.print("[yellow]Components: No registry found[/yellow]")
    else:
        console.print("[red]Framework: Not initialized[/red]")
        console.print("Run 'multiagent init' to get started")

def _detect_available_clis():
    """Detect available AI assistant CLIs using non-interactive checks."""

    def _build_search_path() -> str:
        """Return a PATH string that includes common install prefixes."""
        current = os.environ.get("PATH", "")
        paths = [p for p in current.split(os.pathsep) if p]
        seen = set(paths)

        extra_templates = [
            os.path.expanduser("~/.npm-global/bin"),
            os.path.expanduser("~/.local/bin"),
            "/usr/local/bin",
        ]

        nvm_root = Path(os.path.expanduser("~/.nvm/versions/node"))
        if nvm_root.exists():
            for version_dir in nvm_root.iterdir():
                bin_dir = version_dir / "bin"
                if bin_dir.is_dir():
                    extra_templates.append(str(bin_dir))

        for template in extra_templates:
            for candidate in glob.glob(template):
                if candidate and candidate not in seen and Path(candidate).is_dir():
                    seen.add(candidate)
                    paths.append(candidate)

        return os.pathsep.join(paths)

    def _extract_version(raw: str) -> str | None:
        tokens = raw.strip().split()
        for token in tokens:
            if any(char.isdigit() for char in token) and any(ch == '.' for ch in token):
                return token.strip("()")
        return raw.strip() or None

    def _detect(commands: list[str]) -> tuple[bool, str | None]:
        search_path = _build_search_path()
        for cmd in commands:
            exe = which(cmd, path=search_path)
            if not exe:
                continue
            try:
                result = subprocess.run(
                    [exe, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                    env={**os.environ, "PATH": search_path},
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

            if result.returncode == 0:
                version = _extract_version(result.stdout or result.stderr)
                return True, version or "Available"

            # Non-zero return code but executable exists – treat as available
            return True, "Available"

        return False, None

    status = {}
    cli_checks = {
        "Gemini CLI": ["gemini", "gcloud"],
        "Qwen CLI": ["qwen", "qwen-cli"],
        "Codex CLI": ["codex", "openai-codex"],
        "GitHub Copilot": ["gh"],
        "Claude Code": ["claude", "claude-cli"],
    }

    for cli_name, commands in cli_checks.items():
        available, version = _detect(commands)
        status[cli_name] = {"available": available, "version": version}

    if status["GitHub Copilot"].get("available"):
        gh_path = which("gh", path=_build_search_path())
        if gh_path:
            try:
                result = subprocess.run(
                    [gh_path, "extension", "list"],
                    capture_output=True,
                    text=True,
                    timeout=3,
                )
                output = result.stdout.lower()
                if "github/gh-copilot" in output or "copilot" in output:
                    status["GitHub Copilot"] = {"available": True, "version": "Available (with Copilot)"}
                else:
                    status["GitHub Copilot"] = {"available": True, "version": "Available (no Copilot extension)"}
            except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
                status["GitHub Copilot"] = {"available": True, "version": "Available"}

    openai_available, openai_version = _detect(["openai", "openai-cli"])
    status["OpenAI CLI"] = {"available": openai_available, "version": openai_version}

    return status

def _recommend_additional_components(project_path):
    """Simple component recommendations based on CLI availability"""
    console.print("\n[bold]Checking for additional component recommendations...[/bold]")

    # Check available CLIs
    available_clis = _detect_available_clis()
    available_count = sum(1 for cli in available_clis.values() if cli['available'])

    # Show available CLIs
    for cli, status in available_clis.items():
        if status['available']:
            console.print(f"[green]FOUND[/green] {cli}: {status['version']}")
        else:
            console.print(f"[red]MISSING[/red] {cli}: Not available")

    # Check installed components
    console.print(f"\n[bold]MultiAgent Components Status:[/bold]")
    components = ['multiagent-devops', 'multiagent-testing', 'multiagent-agentswarm']
    
    for component in components:
        try:
            version = metadata.version(component)
            console.print(f"  • [cyan]{component}[/cyan]: [green]Installed (v{version})[/green]")
        except metadata.PackageNotFoundError:
            if component == 'multiagent-devops':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Advanced CI/CD and deployment automation")
                console.print(f"    Install: [dim]pipx install multiagent-devops[/dim]")
                console.print(f"    Initialize: [dim]{_get_python_command()} -m multiagent_devops.cli init[/dim]")
            elif component == 'multiagent-testing':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Comprehensive test automation")
                console.print(f"    Install: [dim]pipx install multiagent-testing[/dim]")
                console.print(f"    Initialize: [dim]{_get_python_command()} -m multiagent_testing.cli init[/dim]")
            elif component == 'multiagent-agentswarm':
                console.print(f"  • [cyan]{component}[/cyan]: [yellow]Not installed[/yellow]")
                console.print(f"    Multi-agent coordination and orchestration")
                console.print(f"    Install: [dim]pipx install multiagent-agentswarm[/dim]")

    if available_count > 0:
        console.print(f"    [dim]({available_count} AI assistant CLI(s) detected for enhanced coordination)[/dim]")

    console.print("\n[green]Core framework ready! Install components as needed.[/green]")

# Component installation removed - users install components manually when needed

def _get_latest_version(package_name):
    """Get latest version of package from PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data['info']['version']
    except Exception:
        pass
    return None

def _get_python_command():
    """Get the appropriate python command - simplified since pipx handles environment isolation"""
    return 'python'

def _check_python_environment():
    """Check Python environment - simplified since pipx handles isolation"""
    # pipx handles environment isolation automatically, so no complex checks needed
    pass

def _check_for_updates_async():
    """Non-blocking check for updates - shows notification if available"""
    try:
        current_version = metadata.version('multiagent-core')
        latest_version = _get_latest_version('multiagent-core')

        # Disable automatic upgrade notifications - user can run 'upgrade' command when needed
        # if latest_version and current_version != latest_version:
        #     console.print(f"[dim yellow]UPDATE AVAILABLE: multiagent-core {current_version} -> {latest_version}[/dim yellow]")
        #     console.print(f"[dim yellow]   Run 'multiagent upgrade' to update all packages[/dim yellow]")
    except Exception:
        # Silently fail - don't interrupt user workflow
        pass

def _convert_path_for_windows_tools(path):
    """Convert paths for Windows tools like gh CLI - handles all WSL scenarios"""
    path_str = str(path)

    # Handle different WSL path formats
    if '\\\\wsl.localhost\\' in path_str:
        # Format: \\wsl.localhost\Ubuntu\tmp\test -> C:\Users\user\AppData\Local\Temp\test
        # Extract the Linux path part
        linux_path = path_str.replace('\\\\wsl.localhost\\Ubuntu', '').replace('\\', '/')

        # Try to convert using wslpath
        try:
            result = subprocess.run(['wslpath', '-w', linux_path], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

        # Fallback: if in /tmp, map to Windows temp
        if linux_path.startswith('/tmp/'):
            import tempfile
            windows_temp = tempfile.gettempdir()
            relative_path = linux_path[5:]  # Remove /tmp/
            windows_path = os.path.join(windows_temp, relative_path).replace('/', '\\')

            # Create the directory in Windows if it doesn't exist
            try:
                os.makedirs(windows_path, exist_ok=True)
            except:
                pass

            return windows_path

    elif hasattr(os, 'uname') and 'Microsoft' in os.uname().release:
        # Running directly in WSL - convert to Windows path
        try:
            result = subprocess.run(['wslpath', '-w', path_str], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass

    # If all else fails, return original path
    return path_str

def _should_create_github_repo():
    """Interactive prompt to ask if user wants to create GitHub repository"""
    if not config.interactive:
        return False

    while True:
        response = input("Create GitHub repository? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            console.print("Please enter 'y' for yes or 'n' for no")

def _copy_non_destructive(src, dest, console):
    """
    Recursively copy files and directories.
    Does not overwrite existing files.
    """
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dest, item)
            _copy_non_destructive(s, d, console)
    else:
        if not os.path.exists(dest):
            shutil.copy2(src, dest)
        else:
            # This is noisy, let's keep it off for now.
            # console.print(f"[dim]Skipped existing file: {dest}[/dim]")
            pass


def _generate_project_structure(cwd):
    """Copy framework directories from package resources to the target directory."""
    console.print("🚀 Setting up MultiAgent framework...")

    # Use directories that actually ship with the package
    dirs_to_copy = {
        ".multiagent": ".multiagent",
        ".claude": ".claude",
        ".vscode": ".vscode",
        ".github": ".github",
        "docs": "docs",
    }

    for src_rel_path, dest_dir_name in dirs_to_copy.items():
        console.print(f"📁 Setting up {dest_dir_name}/ directory...")
        try:
            src_path = pkg_resources.resource_filename('multiagent_core', f'templates/{src_rel_path}')
            if os.path.exists(src_path):
                _copy_non_destructive(src_path, cwd / dest_dir_name, console)
                console.print(f"✅ Merged {dest_dir_name} from package resources")
            else:
                console.print(f"[yellow]Warning: Source directory not found for {dest_dir_name} at {src_path}[/yellow]")
        except Exception as e:
            console.print(f"[red]Error merging {dest_dir_name}: {e}[/red]")

    # Copy README template to .multiagent/ directory (not root)
    console.print("📄 Setting up .multiagent/README.md...")
    try:
        multiagent_path = pkg_resources.resource_filename('multiagent_core', '')
        site_packages = os.path.dirname(multiagent_path)
        readme_src_path = os.path.join(site_packages, '.multiagent/README.md')
        dest_readme_path = cwd / '.multiagent' / 'README.md'
        if os.path.exists(readme_src_path):
            # Ensure .multiagent directory exists
            (cwd / '.multiagent').mkdir(exist_ok=True)
            if not os.path.exists(dest_readme_path):
                shutil.copy(readme_src_path, dest_readme_path)
                console.print("✅ Copied .multiagent/README.md")
            else:
                console.print("[dim]Skipped existing .multiagent/README.md[/dim]")
        else:
            console.print(f"[yellow]Warning: README.md template not found at {readme_src_path}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not copy .multiagent/README.md: {e}[/yellow]")

    # Handle copilot-instructions.md - append instead of overwrite
    console.print("📄 Setting up copilot instructions...")
    try:
        # Get the correct path from package templates
        copilot_src_path = pkg_resources.resource_filename('multiagent_core', 'templates/.github/copilot-instructions.md')
        dest_copilot_path = cwd / '.github' / 'copilot-instructions.md'
        if os.path.exists(copilot_src_path):
            # Ensure .github directory exists
            (cwd / '.github').mkdir(exist_ok=True)
            
            if os.path.exists(dest_copilot_path):
                # Append our instructions to existing ones
                with open(dest_copilot_path, 'a', encoding='utf-8') as f:
                    f.write('\n\n# MultiAgent Framework Instructions\n\n')
                    with open(copilot_src_path, 'r', encoding='utf-8') as src_f:
                        f.write(src_f.read())
                console.print("✅ Appended MultiAgent instructions to existing copilot-instructions.md")
            else:
                # Copy if no existing file
                shutil.copy(copilot_src_path, dest_copilot_path)
                console.print("✅ Copied copilot-instructions.md")
        else:
            console.print(f"[yellow]Warning: copilot-instructions.md not found at {copilot_src_path}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]Warning: Could not handle copilot-instructions.md: {e}[/yellow]")

    console.print("🎉 MultiAgent framework setup complete!")
    return True


def _copy_resource_file(package, resource_path, dest_path):
    """Copy a single file from package resources"""
    import pkg_resources
    try:
        content = pkg_resources.resource_string(package, resource_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, 'wb') as f:
            f.write(content)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not copy {resource_path}: {e}[/yellow]")


def _copy_resource_directory(package, resource_dir, dest_dir):
    """Recursively copy a directory from package resources"""
    import pkg_resources
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)

        # List all items in the directory
        items = pkg_resources.resource_listdir(package, resource_dir)

        for item in items:
            item_path = f"{resource_dir}/{item}"
            dest_item_path = dest_dir / item

            if pkg_resources.resource_isdir(package, item_path):
                # Recursively copy subdirectory
                _copy_resource_directory(package, item_path, dest_item_path)
            else:
                # Copy file
                _copy_resource_file(package, item_path, dest_item_path)

    except Exception as e:
        console.print(f"[yellow]Warning: Could not copy directory {resource_dir}: {e}[/yellow]")

def _create_github_repo(cwd):
    """Create a GitHub repository using the gh CLI."""
    repo_name = cwd.name
    console.print(f"Creating GitHub repository: {repo_name}")

    try:
        # Ensure we are in the correct directory
        os.chdir(cwd)

        # Command to create a private repo from the current directory
        command = [
            'gh', 'repo', 'create', repo_name,
            '--private',
            '--source', '.',
            '--push'
        ]

        # The GITHUB_TOKEN is read automatically by 'gh' from env variables
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            cwd=str(cwd)
        )
        console.print(f"[green]Successfully created and pushed to GitHub repository: {repo_name}[/green]")
        console.print(result.stdout)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to create GitHub repository: {e}[/red]")
        console.print(f"[red]stdout: {e.stdout}[/red]")
        console.print(f"[red]stderr: {e.stderr}[/red]")
    except FileNotFoundError:
        console.print("[red]Failed to create GitHub repository: 'gh' command not found.[/red]")
        console.print("[red]Please ensure the GitHub CLI is installed and in your PATH.[/red]")


def _should_install_git_hooks():
    """Interactive prompt to ask if user wants to install git hooks"""
    if not config.interactive:
        return True  # Default to installing git hooks in non-interactive mode

    while True:
        response = input("Install git hooks for multi-agent workflow? [y/N]: ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            return False
        else:
            console.print("Please enter 'y' for yes or 'n' for no")

def _install_git_hooks(project_path):
    """Install git hooks for multi-agent development workflow"""
    console.print("Installing git hooks...")

    try:
        # Get package directory for hooks
        import multiagent_core
        package_location = multiagent_core.__file__

        # Handle WSL/Windows path conversion
        if '\\\\wsl.localhost\\Ubuntu\\' in str(package_location):
            package_path_str = str(package_location).replace('\\\\wsl.localhost\\Ubuntu\\', '/').replace('\\', '/')
            package_path = Path(package_path_str).parent
        else:
            package_path = Path(package_location).parent

        # Generate actual git hooks (not Claude hooks)
        git_hooks_dir = project_path / '.git' / 'hooks'

        if not (project_path / '.git').exists():
            console.print("[yellow]No .git directory found - not a git repository?[/yellow]")
            return False

        if not git_hooks_dir.exists():
            console.print("[yellow].git/hooks directory not found - creating it[/yellow]")
            git_hooks_dir.mkdir(parents=True, exist_ok=True)

        # Generate pre-push hook for professional commit strategy
        pre_push_hook = git_hooks_dir / 'pre-push'
        pre_push_content = '''#!/bin/bash
# MultiAgent framework pre-push hook
# Provides guidance for professional commit accumulation

# Only guide on main branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
if [[ "$current_branch" != "main" ]]; then
    exit 0
fi

# Count commits to push
commits_to_push=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")

# Only guide if 1 or fewer commits
if [[ "$commits_to_push" -le 1 ]]; then
    echo "Professional Commit Strategy Guidance"
    echo "Commits to push: $commits_to_push"
    echo "For richer release notes, consider accumulating 3-6 commits"
    echo "Rich Release Pattern:"
    echo "   git commit -m 'fix(component): specific issue'"
    echo "   git commit -m 'feat(feature): new capability'"
    echo "   git commit -m 'docs: update guide'"
    echo "   git push  # <- Rich release (3+ bullets)"
    echo ""
    echo "🚀 Continue anyway? Proceeding in 3 seconds..."
    echo "   Press Ctrl+C to cancel, or wait to continue"

    # 3 second countdown
    for i in {3..1}; do
        echo -n "$i "
        sleep 1
    done
    echo ""
fi

exit 0
'''

        with open(pre_push_hook, 'w') as f:
            f.write(pre_push_content)
        pre_push_hook.chmod(0o755)

        console.print("[green]Git hooks installed successfully![/green]")
        console.print("[dim]- pre-push: Professional commit strategy guidance[/dim]")
        return True

    except Exception as e:
        console.print(f"[red]Failed to install git hooks: {e}[/red]")
        return False

if __name__ == "__main__":
    main()
