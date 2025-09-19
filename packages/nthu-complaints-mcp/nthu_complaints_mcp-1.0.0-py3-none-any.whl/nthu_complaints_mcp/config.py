"""Configuration management for NTHU Complaints MCP server."""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for the MCP server."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration.

        Args:
            config_path: Path to configuration file. If None, uses default locations.
        """
        self.config_path = config_path or self._find_config_file()
        self._config: Dict[str, Any] = {}
        self.load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        possible_paths = [
            "firebase-service-account.json",
            os.path.expanduser("~/.nthu-complaints/firebase-service-account.json"),
            "/etc/nthu-complaints/firebase-service-account.json"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def load_config(self) -> None:
        """Load configuration from file."""
        if not self.config_path or not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Failed to load config from {self.config_path}: {e}")

    def get_firebase_config(self) -> Dict[str, Any]:
        """Get Firebase configuration."""
        return self._config

    def has_firebase_config(self) -> bool:
        """Check if Firebase configuration is available."""
        return bool(self._config and self._config.get('project_id'))

    @property
    def project_id(self) -> Optional[str]:
        """Get Firebase project ID."""
        return self._config.get('project_id')


# Global configuration instance
config = Config()