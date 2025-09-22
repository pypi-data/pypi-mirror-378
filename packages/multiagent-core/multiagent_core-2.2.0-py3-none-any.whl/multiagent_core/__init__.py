"""Multi-Agent Core Framework

Foundation framework with intelligent directory management for multi-agent development.
"""

try:
    from importlib.metadata import version
    __version__ = version("multiagent-core")
except ImportError:
    # For Python < 3.8
    from importlib_metadata import version
    __version__ = version("multiagent-core")
except Exception:
    __version__ = "unknown"

__author__ = "Multi-Agent Template Framework"

from .cli import main
from .detector import ProjectDetector
from .analyzer import TechStackAnalyzer
from .env_generator import EnvironmentGenerator
from .templates import TemplateManager
from .config import config

__all__ = [
    "main",
    "ProjectDetector", 
    "TechStackAnalyzer",
    "EnvironmentGenerator",
    "TemplateManager",
    "config"
]