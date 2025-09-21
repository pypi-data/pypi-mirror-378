"""
OpenIDE Client Library
Python библиотека для взаимодействия с OpenIDE API
"""

from .client import (
    OpenIDEClient,
    OpenIDEAPIClient,
    OpenIDEConfig,
    create_client,
    create_api_client
)
from .cli import cli

__version__ = "1.1.2"
__author__ = "ArtemJS"
__email__ = "artemjson@gmail.com"
__description__ = "Python client library for OpenIDE container system"

__all__ = [
    "OpenIDEClient",
    "OpenIDEAPIClient", 
    "OpenIDEConfig",
    "create_client",
    "create_api_client",
    "cli",
    "__version__",
    "__author__",
    "__email__",
    "__description__"
]
