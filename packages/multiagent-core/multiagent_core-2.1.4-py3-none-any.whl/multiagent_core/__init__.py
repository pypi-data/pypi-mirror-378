"""Multi-Agent Core Framework

Foundation framework with intelligent directory management for multi-agent development.
"""

__version__ = "0.1.0"
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