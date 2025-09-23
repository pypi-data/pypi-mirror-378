"""
Configuration management for MultiAgent Core
Handles environment variables and configuration loading
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

class Config:
    """Configuration manager for MultiAgent Core"""
    
    def __init__(self):
        self._config = {}
        self._load_env_file()
        self._load_env_vars()
    
    def _load_env_file(self):
        """Load .env file if it exists"""
        env_file = Path.cwd() / ".env"
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self._config[key.strip()] = self._parse_value(value.strip())
    
    def _load_env_vars(self):
        """Load environment variables, overriding .env file values"""
        env_vars = {
            'DEBUG': 'debug',
            'LOG_LEVEL': 'log_level',
            'GITHUB_TOKEN': 'github_token',
            'GITHUB_USERNAME': 'github_username',
            'DOCKER_HOST': 'docker_host',
            'FORCE_DOCKER': 'force_docker',
            'DOCKER_TIMEOUT': 'docker_timeout',
            'MULTIAGENT_AUTO_UPGRADE': 'auto_upgrade',
            'MULTIAGENT_INTERACTIVE': 'interactive',
            'MULTIAGENT_CONFIRM_DESTRUCTIVE': 'confirm_destructive',
            'DEFAULT_INSTALL_DEVOPS': 'default_install_devops',
            'DEFAULT_INSTALL_TESTING': 'default_install_testing',
            'DEFAULT_INSTALL_AGENTSWARM': 'default_install_agentswarm',
            'DEVELOPMENT_MODE': 'development_mode',
            'SKIP_VERSION_CHECK': 'skip_version_check',
            'CACHE_CLI_DETECTION': 'cache_cli_detection',
            'WSL_AUTO_CONVERT_PATHS': 'wsl_auto_convert_paths',
            'WINDOWS_GITHUB_CLI_PATH': 'windows_github_cli_path',
            'PYPI_API_BASE': 'pypi_api_base',
            'GITHUB_API_BASE': 'github_api_base',
            'ALLOW_SUDO_OPERATIONS': 'allow_sudo_operations',
            'TRUST_ROOT_CERTIFICATES': 'trust_root_certificates'
        }
        
        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value is not None:
                self._config[config_key] = self._parse_value(value)
    
    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type"""
        value = value.strip('"\'')  # Remove quotes
        
        # Boolean values
        if value.lower() in ('true', 'yes', '1', 'on'):
            return True
        elif value.lower() in ('false', 'no', '0', 'off'):
            return False
        
        # Integer values
        try:
            return int(value)
        except ValueError:
            pass
        
        # Float values
        try:
            return float(value)
        except ValueError:
            pass
        
        # String values
        return value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = self.get(key, default)
        return bool(value) if isinstance(value, bool) else default
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = self.get(key, default)
        return int(value) if isinstance(value, (int, float)) else default
    
    def get_str(self, key: str, default: str = "") -> str:
        """Get string configuration value"""
        value = self.get(key, default)
        return str(value) if value is not None else default
    
    @property
    def debug(self) -> bool:
        return self.get_bool('debug', False)
    
    @property
    def log_level(self) -> str:
        return self.get_str('log_level', 'info')
    
    @property
    def github_token(self) -> Optional[str]:
        token = self.get_str('github_token')
        return token if token and token != 'your-github-token-here' else None
    
    @property
    def github_username(self) -> Optional[str]:
        username = self.get_str('github_username')
        return username if username and username != 'your-github-username' else None
    
    @property
    def docker_host(self) -> str:
        return self.get_str('docker_host', 'unix:///var/run/docker.sock')
    
    @property
    def force_docker(self) -> bool:
        return self.get_bool('force_docker', False)
    
    @property
    def docker_timeout(self) -> int:
        return self.get_int('docker_timeout', 60)
    
    @property
    def auto_upgrade(self) -> bool:
        return self.get_bool('auto_upgrade', False)
    
    @property
    def interactive(self) -> bool:
        return self.get_bool('interactive', True)
    
    @property
    def confirm_destructive(self) -> bool:
        return self.get_bool('confirm_destructive', True)
    
    @property
    def development_mode(self) -> bool:
        return self.get_bool('development_mode', False)
    
    @property
    def skip_version_check(self) -> bool:
        return self.get_bool('skip_version_check', False)
    
    @property
    def wsl_auto_convert_paths(self) -> bool:
        return self.get_bool('wsl_auto_convert_paths', True)
    
    @property
    def pypi_api_base(self) -> str:
        return self.get_str('pypi_api_base', 'https://pypi.org/pypi')
    
    @property
    def github_api_base(self) -> str:
        return self.get_str('github_api_base', 'https://api.github.com')

# Global config instance
config = Config()