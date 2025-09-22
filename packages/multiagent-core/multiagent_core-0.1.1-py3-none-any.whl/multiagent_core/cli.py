"""Multi-Agent Core CLI

Command-line interface for the multi-agent development framework.
"""

import click
import json
import subprocess
import requests
import pkg_resources
from pathlib import Path
from rich.console import Console
from rich.table import Table
from .docker import init_with_docker, create_docker_setup

console = Console()

@click.group()
@click.version_option()
def main():
    """Multi-Agent Development Framework CLI"""
    # Check for updates on every command (non-blocking)
    _check_for_updates_async()
    pass

@main.command()
@click.option('--with', 'components', help='Components to install (comma-separated)')
@click.option('--dry-run', is_flag=True, help='Show what would be done without making changes')
@click.option('--no-docker', is_flag=True, help='Skip Docker and install directly')
@click.option('--force-docker', is_flag=True, help='Require Docker, fail if not available')
@click.option('--github', is_flag=True, help='Create GitHub repository automatically')
@click.option('--no-github', is_flag=True, help='Skip GitHub repository creation')
def init(components, dry_run, no_docker, force_docker, github, no_github):
    """Initialize multi-agent framework in current directory"""
    cwd = Path.cwd()
    
    if dry_run:
        console.print("[bold blue]Dry run mode - no changes will be made[/bold blue]")
    
    console.print(f"Initializing multi-agent framework in: {cwd}")
    
    # Handle Docker initialization
    use_docker, docker_status = init_with_docker(
        dry_run=dry_run, 
        force_docker=force_docker, 
        no_docker=no_docker
    )
    
    if force_docker and not use_docker:
        console.print("[red]Docker required but not available. Exiting.[/red]")
        return
    
    # Create framework structure
    if not dry_run:
        success = create_docker_setup(use_docker=use_docker)
        if not success:
            console.print("[red]Framework initialization failed[/red]")
            return
    
    installation_method = "Docker-based" if use_docker else "Direct"
    console.print(f"[green]Core framework initialized ({installation_method})[/green]")
    
    # Handle GitHub repository creation
    if not dry_run and not no_github:
        if github:
            _create_github_repo(cwd)
        elif not github and not no_github:
            # Interactive prompt for GitHub creation
            if _should_create_github_repo():
                _create_github_repo(cwd)
    
    # Handle component installation
    if components:
        component_list = [c.strip() for c in components.split(',')]
        multiagent_dir = cwd / ".multiagent"
        for component in component_list:
            _install_component(component, multiagent_dir, dry_run)

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
        console.print("⚠️ No components registry found")

@main.command()
@click.argument('component')
def uninstall(component):
    """Remove a component from the framework"""
    cwd = Path.cwd()
    multiagent_dir = cwd / ".multiagent"
    
    if not multiagent_dir.exists():
        console.print("❌ Multi-agent framework not initialized")
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
            console.print(f"❌ Component {component} not found")

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
    
    # Check GitHub CLI
    console.print("\n[bold]GitHub CLI Status:[/bold]")
    try:
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split()[2] if len(result.stdout.split()) > 2 else "unknown"
            console.print(f"GitHub CLI: {version}")
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

def _should_create_github_repo():
    """Interactive prompt to ask if user wants to create GitHub repository"""
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
    try:
        # Check if gh CLI is available
        result = subprocess.run(['gh', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            console.print("[red]GitHub CLI (gh) not found. Please install it first.[/red]")
            console.print("Visit: https://cli.github.com/")
            return False
        
        # Check if already a git repo
        git_dir = project_path / ".git"
        if not git_dir.exists():
            console.print("Initializing git repository...")
            subprocess.run(['git', 'init'], cwd=project_path, check=True)
        
        # Get project name from directory
        repo_name = project_path.name
        
        # Create GitHub repository
        console.print(f"Creating GitHub repository: {repo_name}")
        result = subprocess.run([
            'gh', 'repo', 'create', repo_name,
            '--public',
            '--source', str(project_path),
            '--push'
        ], capture_output=True, text=True, cwd=project_path)
        
        if result.returncode == 0:
            console.print(f"[green]GitHub repository created successfully![/green]")
            console.print(f"Repository URL: https://github.com/$(gh api user --jq .login)/{repo_name}")
            return True
        else:
            console.print(f"[red]Failed to create GitHub repository: {result.stderr}[/red]")
            return False
            
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error creating GitHub repository: {e}[/red]")
        return False
    except FileNotFoundError:
        console.print("[red]Git not found. Please install Git first.[/red]")
        return False

if __name__ == "__main__":
    main()