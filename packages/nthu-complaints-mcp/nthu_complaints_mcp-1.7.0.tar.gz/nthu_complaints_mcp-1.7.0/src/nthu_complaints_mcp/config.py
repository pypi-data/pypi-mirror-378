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
            config_path: Path to configuration file. If None, uses hardcoded config.
        """
        self.config_path = config_path or self._find_config_file()
        self._config: Dict[str, Any] = {}
        self.load_config()

    def _find_config_file(self) -> Optional[str]:
        """Find configuration file in standard locations."""
        # For simplicity, we'll just check the current working directory
        # All other configurations are hardcoded
        config_file = "firebase-service-account.json"
        if os.path.exists(config_file):
            return config_file
        return None

    def load_config(self) -> None:
        """Load configuration from file or use hardcoded config."""
        # Try to load from file first
        if self.config_path and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                    print(f"Loaded Firebase configuration from {self.config_path}")
                    return
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load config from {self.config_path}: {e}")

        # Fall back to hardcoded Firebase Web SDK configuration
        print("Using hardcoded Firebase Web SDK configuration")
        self._config = {
            "apiKey": "AIzaSyB9FzdMo9t3dIQ4KHn82YZXZfOyUXYYjEY",
            "authDomain": "nthu-student-association.firebaseapp.com",
            "projectId": "nthu-student-association",
            "storageBucket": "nthu-student-association.firebasestorage.app",
            "messagingSenderId": "1061254054944",
            "appId": "1:1061254054944:web:bf03a403e3810fdcb1e845",
            "measurementId": "G-EMEKTSBMGE"
        }

    def get_firebase_config(self) -> Dict[str, Any]:
        """Get Firebase configuration."""
        return self._config

    def has_firebase_config(self) -> bool:
        """Check if Firebase configuration is available."""
        return bool(self._config and (self._config.get('project_id') or self._config.get('projectId')))

    @property
    def project_id(self) -> Optional[str]:
        """Get Firebase project ID."""
        return self._config.get('project_id') or self._config.get('projectId')


# Global configuration instance
config = Config()