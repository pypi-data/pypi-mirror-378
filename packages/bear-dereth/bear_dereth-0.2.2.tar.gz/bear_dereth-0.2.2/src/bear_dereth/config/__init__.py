"""Config and settings management utilities for Bear Utils."""

from ._settings_manager import Query, Table, where
from ._settings_manager._base_settings import BaseSettingHandler
from .config_manager import ConfigManager
from .dir_manager import (
    DirectoryManager,
    clear_temp_directory,
    get_cache_path,
    get_config_path,
    get_local_config_path,
    get_settings_path,
    get_temp_path,
)
from .settings_manager import SettingsManager

__all__ = [
    "BaseSettingHandler",
    "ConfigManager",
    "DirectoryManager",
    "Query",
    "SettingsManager",
    "Table",
    "clear_temp_directory",
    "get_cache_path",
    "get_config_path",
    "get_local_config_path",
    "get_settings_path",
    "get_temp_path",
    "where",
]
