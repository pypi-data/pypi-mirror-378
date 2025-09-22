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
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from .config import config
from .docker import init_with_docker, create_docker_setup, run_github_operation_in_docker
from .detector import ProjectDetector
from .analyzer import TechStackAnalyzer
from .env_generator import EnvironmentGenerator
from .templates import TemplateManager

console = Console()

@click.group()
@click.version_option()
def main():
    """Multi-Agent Development Framework CLI"""
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
    
    # Handle Docker initialization
    use_docker, docker_status = init_with_docker(
        dry_run=dry_run, 
        force_docker=False, 
        no_docker=False
    )
    
    
    # Create framework structure using existing sophisticated system
    if not dry_run:
        success = create_docker_setup(use_docker=use_docker)
        if not success:
            console.print("[red]Framework initialization failed[/red]")
            return
        
        # The create_docker_setup already handles template injection via _inject_core_templates
        # which detects existing CLI templates and injects our comprehensive content
        installation_method = "Docker-based" if use_docker else "Direct"
        console.print(f"[green]Core framework initialized ({installation_method})[/green]")
    
    # Handle git repository setup
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

    # Handle GitHub repository creation
    if not dry_run and create_github:
        _create_github_repo(cwd)
    
    # Handle git hooks installation
    if not dry_run and install_git_hooks:
        _install_git_hooks(cwd)
    
    # Recommend additional components based on detected CLIs and project structure
    if not dry_run:
        _recommend_additional_components(cwd)
    
    # Auto-generate smart environment configuration
    if not dry_run:
        console.print("\n[bold blue]🔧 Smart Environment Detection[/bold blue]")
        try:
            detector = ProjectDetector(cwd)
            project_info = detector.detect()
            
            if project_info.project_type != 'unknown':
                console.print(f"Detected: [cyan]{project_info.project_type}[/cyan] project")
                
                if project_info.frameworks:
                    console.print(f"Frameworks: [cyan]{', '.join(list(project_info.frameworks)[:3])}[/cyan]")
                
                # Ask if user wants smart environment setup
                if Confirm.ask("Generate smart environment configuration?", default=True):
                    analyzer = TechStackAnalyzer(detector)
                    generator = EnvironmentGenerator(analyzer)
                    
                    env_example_path, env_template_path = generator.write_env_files(cwd)
                    console.print(f"[green]Generated {env_example_path.name} and {env_template_path.name}[/green]")
                    
                    # Show quick setup summary
                    env_summary = analyzer.get_environment_summary()
                    if env_summary['total_services'] > 0:
                        console.print(f"[dim]Found {env_summary['total_services']} services requiring configuration[/dim]")
                        console.print("[dim]Run 'python -m multiagent_core.cli env-init --interactive' to configure[/dim]")
            else:
                console.print("[dim]Unknown project type - skipping auto environment detection[/dim]")
        except Exception as e:
            console.print(f"[yellow]Warning: Environment detection failed: {e}[/yellow]")
    
    console.print("[green]Multi-agent framework initialization complete![/green]")

def _install_component(component, multiagent_dir, dry_run):
    """Install a specific component with intelligent directory merging"""
    console.print(f"📦 Installing component: {component}")
    
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
        
        for component, info in registry.items():
            if component != "installation_order":
                status = "[green]Installed[/green]" if info.get("installed") else "[red]Not installed[/red]"
                table.add_row(component, info.get("version", "unknown"), status)
        
        console.print(table)
        
        install_order = registry.get("installation_order", [])
        if install_order:
            console.print(f"\n📋 Installation order: {' → '.join(install_order)}")
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
    
    console.print(f"🗑️ Removing component: {component}")
    
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
                console.print(f"[yellow]{package}: {current_version} → {latest_version}[/yellow]")
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
                        'pip', 'install', '--upgrade', package
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
    """Detect available AI assistant CLIs"""
    clis = {
        'Gemini CLI': {'cmd': ['gemini', '--version'], 'version_idx': -1},
        'Qwen CLI': {'cmd': ['qwen', '--version'], 'version_idx': -1},
        'GitHub Copilot': {'cmd': ['gh', 'copilot', '--help'], 'version_idx': None},
        'OpenAI CLI': {'cmd': ['openai', '--version'], 'version_idx': -1},
    }
    
    status = {}
    for name, config in clis.items():
        try:
            result = subprocess.run(config['cmd'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                if config['version_idx'] is not None and result.stdout:
                    try:
                        version = result.stdout.strip().split()[config['version_idx']]
                    except (IndexError, AttributeError):
                        version = "Available"
                else:
                    version = "Available"
                status[name] = {'available': True, 'version': version}
            else:
                status[name] = {'available': False, 'version': None}
        except (FileNotFoundError, subprocess.TimeoutExpired):
            status[name] = {'available': False, 'version': None}
    
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
    
    # Quick recommendations
    components_to_install = []
    
    # Check for spec-kit or GitHub structure for DevOps
    if (project_path / 'tasks.md').exists() or (project_path / '.github').exists():
        if click.confirm("Install DevOps component for advanced CI/CD and deployment automation?", default=True):
            components_to_install.append('devops')
    
    # Check for existing tests for Testing enhancement
    test_dirs = ['tests/', 'test/', '__tests__/', 'spec/']
    has_tests = any((project_path / test_dir).exists() for test_dir in test_dirs)
    
    if has_tests:
        if click.confirm("Install Testing component to enhance existing test suite?", default=True):
            components_to_install.append('testing')
    elif click.confirm("Install Testing component for comprehensive test automation?", default=True):
        components_to_install.append('testing')
    
    # AgentSwarm for multi-CLI coordination
    if available_count > 1:
        if click.confirm(f"Install AgentSwarm component for multi-agent coordination? ({available_count} CLIs detected)", default=True):
            components_to_install.append('agentswarm')
    
    # Install selected components
    if components_to_install:
        console.print(f"\n[bold]Installing components: {', '.join(components_to_install)}[/bold]")
        for component in components_to_install:
            _install_multiagent_component(component, project_path)
    else:
        console.print("\n[yellow]No additional components selected[/yellow]")

def _install_multiagent_component(component, project_path):
    """Install a multiagent component using pip"""
    try:
        console.print(f"Installing multiagent-{component}...")
        result = subprocess.run([
            'pip', 'install', f'multiagent-{component}'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            console.print(f"[green]SUCCESS: multiagent-{component} installed successfully[/green]")
            
            # Run component initialization if available
            try:
                init_result = subprocess.run([
                    'python', '-m', f'multiagent_{component}.cli', 'init'
                ], cwd=str(project_path), capture_output=True, text=True)
                
                if init_result.returncode == 0:
                    console.print(f"[green]SUCCESS: {component} component initialized[/green]")
                else:
                    console.print(f"[yellow]WARNING: {component} installed but initialization had issues[/yellow]")
            except Exception:
                console.print(f"[yellow]WARNING: {component} installed but no initialization command found[/yellow]")
        else:
            console.print(f"[red]ERROR: Failed to install multiagent-{component}: {result.stderr}[/red]")
    except Exception as e:
        console.print(f"[red]ERROR: Error installing {component}: {e}[/red]")

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

def _check_for_updates_async():
    """Non-blocking check for updates - shows notification if available"""
    try:
        current_version = pkg_resources.get_distribution('multiagent-core').version
        latest_version = _get_latest_version('multiagent-core')
        
        if latest_version and current_version != latest_version:
            console.print(f"[dim yellow]💡 Update available: multiagent-core {current_version} → {latest_version}[/dim yellow]")
            console.print(f"[dim yellow]   Run 'multiagent upgrade' to update all packages[/dim yellow]")
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
    
    # Initialize git if needed
    git_dir = project_path / ".git"
    if not git_dir.exists():
        console.print("Initializing git repository...")
        try:
            subprocess.run(['git', 'init'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(['git', 'add', '.'], cwd=project_path, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit from multiagent-core'], 
                         cwd=project_path, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to initialize git: {e}[/red]")
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
    """Install git hooks for multi-agent development workflow using Docker"""
    console.print("Installing git hooks...")
    
    success = run_github_operation_in_docker(
        'install_hooks',
        work_dir=project_path,
        github_token=config.github_token
    )
    
    if success:
        console.print("[green]Git hooks installed successfully![/green]")
        console.print("Hooks installed: pre-commit")
        return True
    else:
        console.print("[red]Failed to install git hooks[/red]")
        return False

if __name__ == "__main__":
    main()