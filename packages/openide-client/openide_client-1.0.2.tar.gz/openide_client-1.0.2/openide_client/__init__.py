"""
OpenIDE Client Library
Python библиотека для взаимодействия с OpenIDE API
"""

from .client import OpenIDEClient, OpenIDEConfig, OpenIDEAPIClient

__version__ = "1.0.2"
__author__ = "OpenIDE Team"
__email__ = "openide@example.com"

__all__ = [
    "OpenIDEClient",
    "OpenIDEConfig", 
    "OpenIDEAPIClient",
    "create_client",
    "create_api_client",
]

def create_client(openide_directory=None, timeout=30, api_key=None):
    """
    Создать OpenIDE клиент
    
    Args:
        openide_directory: Путь к директории OpenIDE
        timeout: Таймаут операций в секундах
        api_key: API ключ для аутентификации
    
    Returns:
        OpenIDEClient: Настроенный клиент
    """
    config = OpenIDEConfig(
        openide_directory=openide_directory,
        timeout=timeout,
        api_key=api_key
    )
    return OpenIDEClient(config)

def create_api_client(api_key, openide_directory=None, timeout=30):
    """
    Создать OpenIDE API клиент
    
    Args:
        api_key: API ключ для аутентификации
        openide_directory: Путь к директории OpenIDE
        timeout: Таймаут операций в секундах
    
    Returns:
        OpenIDEAPIClient: Настроенный API клиент
    """
    config = OpenIDEConfig(
        api_key=api_key,
        openide_directory=openide_directory,
        timeout=timeout
    )
    return OpenIDEAPIClient(config)
