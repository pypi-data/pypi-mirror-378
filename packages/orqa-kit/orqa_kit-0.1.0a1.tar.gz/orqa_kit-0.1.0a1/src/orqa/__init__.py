from ._version import __version__

# Public API (optionally expose)
from .config import load_user_config, DatasetConfig
from .main import main  # convenient import

__all__ = ["__version__", "load_user_config", "DatasetConfig", "main"]