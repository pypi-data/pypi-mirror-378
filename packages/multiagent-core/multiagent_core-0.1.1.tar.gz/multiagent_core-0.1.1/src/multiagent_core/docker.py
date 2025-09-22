"""Docker utilities for multi-agent development framework.

This module provides Docker detection, installation, and container management
utilities that are used across all multiagent components.
"""

import os
import subprocess
import shutil
from pathlib import Path
from rich.console import Console

console = Console()

def check_docker():
    """Check if Docker is installed and running
    
    Returns:
        tuple: (bool, str) - (is_available, status_message)
    """
    try:
        # Handle WSL/Windows cross-platform Docker detection
        docker_commands = ['docker']
        
        # If running from Windows Python but in WSL path, try wsl docker
        if '\\\\wsl.localhost\\' in str(Path.cwd()) or (hasattr(os, 'uname') and 'Microsoft' in os.uname().release):
            docker_commands = ['wsl', 'docker']
        
        # Try Docker version check
        result = subprocess.run(docker_commands + ['--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "Docker command not found"
        
        # Check if Docker daemon is running
        result = subprocess.run(docker_commands + ['info'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "Docker daemon not running"
        
        return True, f"Docker available via {' '.join(docker_commands)}"
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, AttributeError):
        return False, "Docker check failed"

def install_docker():
    """Install Docker if not present
    
    Returns:
        bool: True if installation successful, False otherwise
    """
    console.print("[yellow]Docker not found. Installing Docker...[/yellow]")
    
    # Detect OS - check for WSL specifically
    try:
        is_wsl = os.path.exists('/proc/version') and 'Microsoft' in open('/proc/version').read()
    except:
        is_wsl = False
    
    if os.name == 'nt' and not is_wsl:  # Pure Windows
        console.print("[red]Please install Docker Desktop from https://docker.com/products/docker-desktop[/red]")
        return False
    
    if is_wsl:
        console.print("[yellow]WSL detected. Checking for Docker Desktop integration...[/yellow]")
        # In WSL, Docker Desktop should be used instead of installing Docker directly
        console.print("[red]Please install Docker Desktop on Windows and enable WSL integration[/red]")
        console.print("[yellow]1. Install Docker Desktop from https://docker.com/products/docker-desktop[/yellow]")
        console.print("[yellow]2. Enable WSL integration in Docker Desktop settings[/yellow]")
        return False
    
    # Linux
    try:
        # Install Docker using official script
        console.print("Installing Docker via official script...")
        subprocess.run(['curl', '-fsSL', 'https://get.docker.com', '-o', 'get-docker.sh'], check=True)
        subprocess.run(['sh', 'get-docker.sh'], check=True)
        subprocess.run(['rm', 'get-docker.sh'], check=True)
        
        # Add user to docker group (requires logout/login)
        username = os.getenv('USER')
        if username:
            subprocess.run(['sudo', 'usermod', '-aG', 'docker', username], check=True)
            console.print(f"[yellow]Added {username} to docker group. Please logout and login again.[/yellow]")
        
        console.print("[green]Docker installed successfully![/green]")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to install Docker: {e}[/red]")
        return False

def run_in_docker(command, work_dir="/workspace", image="python:3.12-slim"):
    """Run command in Docker container
    
    Args:
        command (str): Command to run in container
        work_dir (str): Working directory in container
        image (str): Docker image to use
        
    Returns:
        subprocess.CompletedProcess: Result of docker run command
    """
    # Mount current directory as workspace
    cwd = Path.cwd()
    
    # Use appropriate Docker command and fix paths for WSL
    docker_commands = ['docker']
    mount_path = str(cwd)
    
    if '\\\\wsl.localhost\\' in str(cwd):
        docker_commands = ['wsl', 'docker']
        # Convert Windows WSL path to Linux path for Docker
        # \\wsl.localhost\Ubuntu\home\user\path -> /home/user/path
        mount_path = str(cwd).replace('\\\\wsl.localhost\\Ubuntu', '').replace('\\', '/')
    elif hasattr(os, 'uname') and 'Microsoft' in os.uname().release:
        # Running in WSL directly
        mount_path = str(cwd)
    
    docker_cmd = docker_commands + [
        'run', '--rm',
        '-v', f'{mount_path}:{work_dir}',
        '-w', work_dir,
        image,
        'bash', '-c', command
    ]
    
    return subprocess.run(docker_cmd, capture_output=True, text=True)

def init_with_docker(dry_run=False, force_docker=False, no_docker=False):
    """Initialize framework with Docker support
    
    Args:
        dry_run (bool): Show what would be done without making changes
        force_docker (bool): Require Docker, fail if not available
        no_docker (bool): Skip Docker entirely
        
    Returns:
        tuple: (bool, str) - (docker_used, status_message)
    """
    if no_docker:
        return False, "Docker skipped by user request"
    
    # Check Docker availability
    docker_available, docker_msg = check_docker()
    console.print(f"Docker status: {docker_msg}")
    
    if not docker_available and not dry_run:
        console.print("[yellow]Attempting to install Docker for consistent environment...[/yellow]")
        if install_docker():
            docker_available, _ = check_docker()
    
    use_docker = docker_available and not dry_run
    
    if force_docker and not docker_available:
        return False, "Docker required but not available"
    
    if use_docker:
        console.print("[green]Using Docker for consistent installation environment[/green]")
        return True, "Docker enabled"
    else:
        console.print("[yellow]Proceeding with direct installation[/yellow]")
        return False, "Direct installation"

def create_docker_setup(use_docker=False):
    """Create framework directories using Docker or direct method
    
    Args:
        use_docker (bool): Whether to use Docker for setup
        
    Returns:
        bool: True if successful, False otherwise
    """
    if use_docker:
        # Create directories using Docker for consistent permissions
        docker_setup = """
        mkdir -p .multiagent/core .multiagent/config .multiagent/environments .multiagent/templates .claude .github/workflows
        
        # Create comprehensive agent templates in .claude directory
        cat > .claude/claude-agents.md << 'EOF'
# Claude Code Subagents

## @claude/general-purpose
Complex multi-step tasks requiring coordination across multiple files and systems.

## @claude/code-refactorer  
Large-scale refactoring across multiple files with pattern recognition.

## @claude/pr-reviewer
Code review with security, performance, and standards analysis.

## @claude/backend-tester
API testing, integration tests, and backend validation.

## @claude/integration-architect
Multi-service integrations, webhooks, and API orchestration.

## @claude/system-architect
Database schemas, API architecture, and system design.

## @claude/security-auth-compliance
Authentication systems, security audits, and compliance validation.

## @claude/frontend-playwright-tester
End-to-end testing, UI validation, and cross-browser testing.
EOF

        # Create Copilot integration templates in .github
        cat > .github/workflows/copilot-integration.yml << 'EOF'
name: GitHub Copilot Integration

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, ready_for_review]

jobs:
  copilot-auto-assign:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'copilot') || (github.event.issue.body && contains(github.event.issue.body, 'Complexity: 1-2') && contains(github.event.issue.body, 'Size: XS-S'))
    steps:
      - name: Assign to Copilot
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '@copilot Please handle this task'
            });
EOF

        # Create base agent coordination templates
        cat > .claude/agent-coordination.md << 'EOF'
# Multi-Agent Coordination

## Task Assignment Rules
- **@copilot**: Complexity ≤2 AND Size XS-S (both required)
- **@claude**: Complexity >2 OR Size >S (either condition)
- **@gemini**: Large document analysis (2M context)
- **@qwen**: Local CLI for everyday coding (FREE)

## Symbol Routing
- @claude/[subagent] - Specific Claude Code subagent
- @copilot - GitHub Copilot for simple tasks
- @gemini - Large context analysis
- @qwen - Local development

<!-- AGENTSWARM_INJECTION_POINT -->
<!-- DEVOPS_INJECTION_POINT -->
<!-- TESTING_INJECTION_POINT -->
EOF
        
        # Create components registry
        cat > .multiagent/components.json << 'EOF'
{
  "framework_version": "0.1.0",
  "components": {
    "core": {"version": "0.1.0", "installed": true, "docker_enabled": true}
  },
  "installation_order": ["core"]
}
EOF
        
        echo "Docker-based initialization complete with comprehensive templates"
        """
        
        result = run_in_docker(docker_setup)
        if result.returncode != 0:
            console.print(f"[red]Docker setup failed: {result.stderr}[/red]")
            return False
        else:
            console.print("[green]Docker environment created successfully[/green]")
            return True
    else:
        # Direct installation fallback
        try:
            from pathlib import Path
            import json
            
            cwd = Path.cwd()
            multiagent_dir = cwd / ".multiagent"
            
            # Create directories
            multiagent_dir.mkdir(exist_ok=True)
            (multiagent_dir / "core").mkdir(exist_ok=True)
            (multiagent_dir / "config").mkdir(exist_ok=True)
            (multiagent_dir / "environments").mkdir(exist_ok=True)
            (multiagent_dir / "templates").mkdir(exist_ok=True)
            
            # Create comprehensive agent directories
            claude_dir = cwd / ".claude"
            claude_dir.mkdir(exist_ok=True)
            
            github_dir = cwd / ".github" / "workflows"
            github_dir.mkdir(parents=True, exist_ok=True)
            
            # Detect existing CLI templates and inject core content
            _inject_core_templates(claude_dir, github_dir)
            
            # Create components registry
            components_file = multiagent_dir / "components.json"
            if not components_file.exists():
                with open(components_file, 'w') as f:
                    json.dump({
                        "framework_version": "0.1.0",
                        "components": {
                            "core": {"version": "0.1.0", "installed": True, "docker_enabled": False}
                        },
                        "installation_order": ["core"]
                    }, f, indent=2)
            
            return True
        except Exception as e:
            console.print(f"[red]Direct setup failed: {e}[/red]")
            return False

def _inject_core_templates(claude_dir, github_dir):
    """Detect existing CLI templates and inject core content"""
    
    # Always create Copilot integration workflow (GitHub templates are always from core)
    copilot_workflow_file = github_dir / "copilot-integration.yml"
    copilot_content = """name: GitHub Copilot Integration

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, ready_for_review]

jobs:
  copilot-auto-assign:
    runs-on: ubuntu-latest
    if: contains(github.event.issue.labels.*.name, 'copilot') || (github.event.issue.body && contains(github.event.issue.body, 'Complexity: 1-2') && contains(github.event.issue.body, 'Size: XS-S'))
    steps:
      - name: Assign to Copilot
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: '@copilot Please handle this task'
            });
"""
    
    with open(copilot_workflow_file, 'w') as f:
        f.write(copilot_content)
    
    # Detect existing CLI templates and inject core content
    existing_templates = []
    
    # Check for CLI-created templates
    agentswarm_file = claude_dir / "agentswarm-agents.md"
    devops_file = claude_dir / "devops-agents.md"  
    testing_file = claude_dir / "testing-agents.md"
    
    if agentswarm_file.exists():
        existing_templates.append("agentswarm")
    if devops_file.exists():
        existing_templates.append("devops")
    if testing_file.exists():
        existing_templates.append("testing")
    
    if existing_templates:
        # CLI templates exist - inject core content into them
        _inject_into_existing_templates(claude_dir, existing_templates)
    else:
        # No CLI templates - create comprehensive core template
        _create_comprehensive_core_template(claude_dir)

def _inject_into_existing_templates(claude_dir, existing_templates):
    """Inject core content at the top of existing CLI templates"""
    
    core_content = """# Multi-Agent Framework - Core Integration

## Claude Code Subagents
- **@claude/general-purpose**: Complex multi-step tasks requiring coordination
- **@claude/code-refactorer**: Large-scale refactoring across multiple files  
- **@claude/pr-reviewer**: Code review with security and standards analysis
- **@claude/backend-tester**: API testing, integration tests, backend validation
- **@claude/integration-architect**: Multi-service integrations, webhooks, API orchestration
- **@claude/system-architect**: Database schemas, API architecture, system design
- **@claude/security-auth-compliance**: Authentication systems, security audits, compliance
- **@claude/frontend-playwright-tester**: E2E testing, UI validation, cross-browser testing

## Task Assignment Rules
- **@copilot**: Complexity ≤2 AND Size XS-S (both required)
- **@claude**: Complexity >2 OR Size >S (either condition)

---

"""
    
    for template_type in existing_templates:
        template_file = claude_dir / f"{template_type}-agents.md"
        if template_file.exists():
            existing_content = template_file.read_text()
            
            # Check if core content already injected
            if "Multi-Agent Framework - Core Integration" not in existing_content:
                # Inject core content at the top
                updated_content = core_content + existing_content
                template_file.write_text(updated_content)

def _create_comprehensive_core_template(claude_dir):
    """Create comprehensive core template when no CLI templates exist"""
    
    claude_agents_file = claude_dir / "claude-agents.md"
    claude_agents_content = """# Claude Code Subagents

## @claude/general-purpose
Complex multi-step tasks requiring coordination across multiple files and systems.

## @claude/code-refactorer  
Large-scale refactoring across multiple files with pattern recognition.

## @claude/pr-reviewer
Code review with security, performance, and standards analysis.

## @claude/backend-tester
API testing, integration tests, and backend validation.

## @claude/integration-architect
Multi-service integrations, webhooks, and API orchestration.

## @claude/system-architect
Database schemas, API architecture, and system design.

## @claude/security-auth-compliance
Authentication systems, security audits, and compliance validation.

## @claude/frontend-playwright-tester
End-to-end testing, UI validation, and cross-browser testing.

## Task Assignment Rules
- **@copilot**: Complexity ≤2 AND Size XS-S (both required)
- **@claude**: Complexity >2 OR Size >S (either condition)
- **@gemini**: Large document analysis (2M context)
- **@qwen**: Local CLI for everyday coding (FREE)

## Symbol Routing
- @claude/[subagent] - Specific Claude Code subagent
- @copilot - GitHub Copilot for simple tasks
- @gemini - Large context analysis
- @qwen - Local development
"""
    
    with open(claude_agents_file, 'w') as f:
        f.write(claude_agents_content)