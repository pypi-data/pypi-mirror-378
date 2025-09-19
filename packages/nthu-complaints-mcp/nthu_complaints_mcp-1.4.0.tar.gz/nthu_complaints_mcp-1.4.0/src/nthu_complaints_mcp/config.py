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
        # Get the directory where this module is located
        module_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up to the project root (from src/nthu_complaints_mcp to project root)
        project_root = os.path.dirname(os.path.dirname(module_dir))

        possible_paths = [
            os.path.join(module_dir, "firebase_config.json"),  # Package directory (for built packages)
            os.path.join(module_dir, "firebase-service-account.json"),  # Package directory (original name)
            "firebase-service-account.json",  # Current working directory
            os.path.join(project_root, "firebase-service-account.json"),  # Project root
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