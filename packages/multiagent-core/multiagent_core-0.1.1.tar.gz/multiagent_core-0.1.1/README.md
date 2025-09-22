# MultiAgent Core

Foundation framework with intelligent directory management for multi-agent development.

## Installation

```bash
pip install multiagent-core
```

## Usage

```bash
# Initialize base framework
multiagent init

# Initialize and skip the git prompt (useful for automation)
multiagent init --auto-init-git

# Add components with intelligent merging
multiagent init --with agentswarm,devops

# Check installation status
multiagent status

# Remove a component
multiagent uninstall agentswarm
```

## Features

- **Intelligent Directory Merging**: Preserves existing `.github/`, `.claude/`, `.vscode/` content
- **Component Organization**: Each component gets organized subdirectories  
- **Installation Order Tracking**: Components installed in proper dependency order
- **Non-Destructive**: Never overwrites existing files
- **Spec-Kit Inspired**: Follows `.specify/` model for intelligent directory detection

## Architecture

```
your-project/
├── .multiagent/
│   ├── core/           # Core framework files
│   ├── config/         # Framework configuration  
│   ├── environments/   # Docker/dev environments
│   ├── templates/      # Project templates
│   └── components.json # Installation registry
├── .github/workflows/
│   ├── core/          # Core framework workflows
│   ├── agentswarm/    # Agent orchestration workflows  
│   └── devops/        # DevOps automation workflows
└── .claude/
    ├── settings.json  # Preserved existing settings
    └── hooks/         # Component hooks organized
```
