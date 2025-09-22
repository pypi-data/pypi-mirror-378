"""Multi-Agent Core CLI

Command-line interface for the multi-agent development framework.
"""

import click
import json
import os
import subprocess
import tempfile
import requests
import pkg_resources
import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
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
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
def init(dry_run):
    """Initialize multi-agent framework in current directory"""
    cwd = Path.cwd()
    
    if dry_run:
        console.print("[bold blue]Dry run mode - no changes will be made[/bold blue]")
    
    console.print(f"Initializing multi-agent framework in: {cwd}")
    
    # Interactive setup prompts
    if not dry_run:
        # Check if existing git repository
        git_exists = (cwd / ".git").exists()
        if git_exists:
            use_existing_git = click.confirm("Existing git repository detected. Use existing repository?", default=True)
        else:
            use_existing_git = False
            
        # GitHub repository creation
        create_github = click.confirm("Create GitHub repository?", default=False)
        
        # Git hooks installation  
        install_git_hooks = click.confirm("Install git hooks for multi-agent workflow?", default=True)
    else:
        use_existing_git = True
        create_github = False
        install_git_hooks = False
    
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
            current_version = pkg_resources.get_distribution(package).version
            latest_version = _get_latest_version(package)
            
            if latest_version and current_version != latest_version:
                updates_available.append((package, current_version, latest_version))
                console.print(f"[yellow]{package}: {current_version} -> {latest_version}[/yellow]")
            else:
                console.print(f"[green]{package}: {current_version} (up to date)[/green]")
        except pkg_resources.DistributionNotFound:
            console.print(f"[dim]{package}: not installed[/dim]")
    
    if updates_available:
        console.print(f"\n[bold yellow]{len(updates_available)} package(s) have updates available[/bold yellow]")
        
        if click.confirm("Install updates?"):
            for package, current, latest in updates_available:
                console.print(f"Upgrading {package}...")
                try:
                    result = subprocess.run([
                        'pip', 'install', '--upgrade', package, '--break-system-packages'
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        console.print(f"[green]{package} upgraded successfully[/green]")
                    else:
                        console.print(f"[red]Failed to upgrade {package}: {result.stderr}[/red]")
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
            current = pkg_resources.get_distribution(package).version
            latest = _get_latest_version(package)
            
            if latest and current != latest:
                status = "[red]Update Available[/red]"
            else:
                status = "[green]Up to Date[/green]"
                
            table.add_row(package, current, latest or "Unknown", status)
        except pkg_resources.DistributionNotFound:
            table.add_row(package, "[red]Not Installed[/red]", "Unknown", "[red]Missing[/red]")
    
    console.print(table)
    
    # Check Docker
    console.print("\n[bold]Docker Status:[/bold]")
    from .docker import check_docker
    docker_available, docker_status = check_docker()
    console.print(f"Docker: {docker_status}")
    
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
    """Detect available AI assistant CLIs with cross-platform support"""
    status = {}
    
    # CLI detection with multiple methods
    clis_to_check = ['gemini', 'qwen', 'codex']
    
    def try_cli_detection(cli_name):
        # Method 1: Direct which command (works in proper environment)
        try:
            result = subprocess.run(['which', cli_name], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Method 2: Try calling with --version (cross-platform)
        try:
            result = subprocess.run([cli_name, '--version'], capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Method 3: WSL detection if we detect Windows Python in WSL environment
        import sys
        if 'C:' in sys.executable:
            try:
                result = subprocess.run(['wsl', 'which', cli_name], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    return True
            except:
                pass
        
        return False
    
    for cli_name in clis_to_check:
        available = try_cli_detection(cli_name)
        status[f'{cli_name.title()} CLI'] = {'available': available, 'version': 'Available' if available else None}
    
    # GitHub CLI - just check if gh works
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            # Check for Copilot extension
            ext_result = subprocess.run(['gh', 'extension', 'list'], capture_output=True, text=True, timeout=3)
            if 'github/gh-copilot' in ext_result.stdout:
                status['GitHub Copilot'] = {'available': True, 'version': 'Available'}
            else:
                status['GitHub Copilot'] = {'available': False, 'version': None}
        else:
            status['GitHub Copilot'] = {'available': False, 'version': None}
    except:
        status['GitHub Copilot'] = {'available': False, 'version': None}
    
    # OpenAI CLI
    try:
        result = subprocess.run(['openai', '--version'], capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            version = result.stdout.strip().split()[-1] if result.stdout else "Available"
            status['OpenAI CLI'] = {'available': True, 'version': version}
        else:
            status['OpenAI CLI'] = {'available': False, 'version': None}
    except:
        status['OpenAI CLI'] = {'available': False, 'version': None}
    
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
    
    # Show available components based on CLI detection
    console.print(f"\n[bold]Available Components:[/bold]")
    console.print(f"  • [cyan]multiagent-devops[/cyan] - Advanced CI/CD and deployment automation")
    console.print(f"    Install: [dim]pip install multiagent-devops && python3 -m multiagent_devops.cli init[/dim]")
    console.print(f"  • [cyan]multiagent-testing[/cyan] - Comprehensive test automation")
    console.print(f"    Install: [dim]pip install multiagent-testing && python3 -m multiagent_testing.cli init[/dim]")
    
    if available_count > 1:
        console.print(f"  • [cyan]multiagent-agentswarm[/cyan] - Multi-agent coordination ({available_count} CLIs detected)")
        console.print(f"    Install: [dim]pip install multiagent-agentswarm[/dim]")
    
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

def _check_python_environment():
    """Check if we're using the right Python for the current environment"""
    import sys
    import os
    
    # Get current working directory and Python executable
    cwd = str(Path.cwd())
    python_exe = sys.executable
    
    # Check if we're in WSL filesystem but using Windows Python
    is_wsl_path = cwd.startswith('/') and ('wsl' in cwd.lower() or cwd.startswith('/home/') or cwd.startswith('/tmp/'))
    is_windows_python = 'C:' in python_exe or '\\' in python_exe
    
    if is_wsl_path and is_windows_python:
        console.print("[yellow]WARNING: You're in WSL but using Windows Python[/yellow]")
        console.print("[yellow]This may cause CLI detection issues. Consider using:[/yellow]")
        console.print("[yellow]  python3 -m multiagent_core.cli instead of python -m multiagent_core.cli[/yellow]")
        console.print()

def _check_for_updates_async():
    """Non-blocking check for updates - shows notification if available"""
    try:
        current_version = pkg_resources.get_distribution('multiagent-core').version
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

def _generate_project_structure(target_dir):
    """Simple, clean project structure setup"""
    console.print("🚀 Setting up MultiAgent framework...")
    
    try:
        target_dir = Path(target_dir)
        
        # 1. Create .multiagent directory
        multiagent_dir = target_dir / ".multiagent"
        multiagent_dir.mkdir(exist_ok=True)
        console.print("✅ Created .multiagent/ directory")
        
        # 2. Create basic structure inside .multiagent
        (multiagent_dir / "config").mkdir(exist_ok=True)
        (multiagent_dir / "core").mkdir(exist_ok=True) 
        (multiagent_dir / "templates").mkdir(exist_ok=True)
        console.print("✅ Created framework directories in .multiagent/")
        
        # 3. Create .claude directory and copy Claude templates
        claude_dir = target_dir / ".claude"
        claude_dir.mkdir(exist_ok=True)
        
        # Copy Claude templates from package
        package_claude_dir = Path(__file__).parent / ".claude"
        if package_claude_dir.exists():
            for item in package_claude_dir.rglob("*"):
                if item.is_file():
                    relative_path = item.relative_to(package_claude_dir)
                    dest_path = claude_dir / relative_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)
        
        console.print("✅ Created .claude/ directory with agent configurations")
        
        # 4. Create .vscode directory in project root
        vscode_dir = target_dir / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        # Basic VS Code settings
        vscode_settings = {
            "python.defaultInterpreterPath": "python3",
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True
            }
        }
        (vscode_dir / "settings.json").write_text(json.dumps(vscode_settings, indent=2))
        console.print("✅ Created VS Code settings")
        
        # 5. Create .github directory with workflows and Copilot instructions
        github_dir = target_dir / ".github"
        workflows_dir = github_dir / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Copilot instructions markdown in .github
        copilot_instructions = """# Copilot Instructions

## Project Overview
This project uses the MultiAgent framework for AI-assisted development.

## Development Guidelines
- Use the MultiAgent framework patterns found in `.multiagent/`
- Follow the component structure for consistent development
- Leverage git hooks for professional commit workflows

## Available Commands
```bash
multiagent status    # Check framework status
multiagent doctor    # Health check
multiagent upgrade   # Update components
```

## Framework Integration
- Framework files are organized under `.multiagent/`
- VS Code settings are optimized for Python development
- Git hooks provide commit guidance
"""
        (github_dir / "copilot-instructions.md").write_text(copilot_instructions)
        console.print("✅ Created .github/ directory with Copilot instructions")
        workflows_dir = github_dir / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Create version control workflow
        version_workflow = """name: Version Control Management

on:
  push:
    branches: [ main ]

jobs:
  version-management:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install semantic-release
      run: |
        npm install --no-save semantic-release
        npm install --no-save @semantic-release/changelog
        npm install --no-save @semantic-release/git
        
    - name: Update VERSION file and create release
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      run: npx semantic-release
"""
        (workflows_dir / "version-control.yml").write_text(version_workflow)
        console.print("✅ Created .github/workflows/ with version control")
        
        # 6. Create .gitmessage template in .multiagent
        gitmessage_content = """# [OPTIONAL STATE] type: brief description (50 chars max)

# [STABLE] feat: Add user authentication system
# [WORKING] fix: Resolve login validation issue  
# [WIP] refactor: Reorganize database models
# [HOTFIX] fix: Critical security patch

# Related to #123

# Commit Types:
# feat: New feature
# fix: Bug fix  
# docs: Documentation
# style: Formatting
# refactor: Code restructuring
# test: Adding tests
# chore: Maintenance

# States (optional):
# [STABLE] - Production-ready (create tag after)
# [WORKING] - Functional, needs testing
# [WIP] - Work in progress
# [HOTFIX] - Emergency fix

# Professional Commit Strategy:
# - Accumulate 3-6 focused commits locally
# - Push batches for rich release notes
# - Always reference issues: "Related to #123"
# - Use "Closes #123" only once per issue
"""
        (multiagent_dir / ".gitmessage").write_text(gitmessage_content)
        console.print("✅ Created git commit message template")
        
        # 7. Create README inside .multiagent
        readme_content = """# MultiAgent Framework

This directory contains the MultiAgent framework configuration.

## Structure
- `config/` - Framework configuration files
- `core/` - Core framework modules  
- `templates/` - Project templates

## Usage
- `.claude/` - Claude Code agent configurations (project root)
- `.vscode/` - VS Code settings (project root)
"""
        (multiagent_dir / "README.md").write_text(readme_content)
        console.print("✅ Created framework README")
        
        # 8. Create components.json
        components_data = {
            "framework_version": "2.1.7",
            "initialized": True,
            "structure": "correct"
        }
        (multiagent_dir / "components.json").write_text(json.dumps(components_data, indent=2))
        console.print("✅ Created components registry")
        
        console.print("🎉 MultiAgent framework setup complete!")
        return True
        
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        return False

def _create_github_repo(project_path):
    """Create GitHub repository using gh CLI"""
    # Check if gh CLI is available
    try:
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            console.print("[red]GitHub CLI not authenticated. Run: gh auth login[/red]")
            return False
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        console.print("[red]GitHub CLI (gh) not found. Install from: https://cli.github.com/[/red]")
        return False
    
    # Get project name from directory
    repo_name = project_path.name
    console.print(f"Creating GitHub repository: {repo_name}")
    
    # Make sure git repository exists and has files to commit
    git_dir = project_path / ".git"
    if not git_dir.exists():
        console.print("[red]Git repository not initialized. Cannot create GitHub repo.[/red]")
        return False
        
    # Add and commit all files for GitHub repo creation
    try:
        subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
        
        # Check if there are files to commit
        status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                     cwd=project_path, capture_output=True, text=True)
        
        if status_result.stdout.strip():  # There are files to commit
            subprocess.run(['git', 'commit', '-m', 'Initial commit from multiagent-core'], 
                         cwd=project_path, check=True, capture_output=True)
        else:
            console.print("[yellow]No files to commit. Creating empty repository.[/yellow]")
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to prepare files for commit: {e}[/red]")
        return False
    
    # Create GitHub repository using gh CLI
    try:
        subprocess.run(['gh', 'repo', 'create', repo_name, '--private', '--source', '.', '--push'], 
                      cwd=project_path, check=True, capture_output=True)
        console.print(f"[green]GitHub repository created successfully![/green]")
        
        # Get the repository URL
        result = subprocess.run(['gh', 'repo', 'view', '--web', '--json', 'url'], 
                              cwd=project_path, capture_output=True, text=True)
        if result.returncode == 0:
            repo_data = json.loads(result.stdout)
            console.print(f"Repository URL: {repo_data.get('url', '')}")
        
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to create GitHub repository: {e}[/red]")
        return False

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
    echo "🤖 Professional Commit Strategy Guidance"
    echo "📊 Commits to push: $commits_to_push"
    echo "💡 For richer release notes, consider accumulating 3-6 commits"
    echo "✅ Rich Release Pattern:"
    echo "   git commit -m 'fix(component): specific issue'"
    echo "   git commit -m 'feat(feature): new capability'"
    echo "   git commit -m 'docs: update guide'"
    echo "   git push  # ← Rich release (3+ bullets)"
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