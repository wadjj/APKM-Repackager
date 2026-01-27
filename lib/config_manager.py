"""
Configuration Manager for APKM Repackager
Handles loading, saving, and managing device configuration profiles
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional


class ConfigManager:
    """Manages device configuration profiles for APKM conversion"""

    VALID_ARCHITECTURES = ['armeabi-v7a', 'arm64-v8a', 'x86', 'x86_64']
    VALID_DENSITIES = ['ldpi', 'mdpi', 'hdpi', 'tvdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']
    DENSITY_ORDER = ['ldpi', 'mdpi', 'hdpi', 'tvdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']

    def __init__(self, config_dir: str = None):
        """
        Initialize the configuration manager

        Args:
            config_dir: Directory to store configuration files (default: ./configs)
        """
        if config_dir is None:
            # Use configs directory relative to project root
            project_root = Path(__file__).parent.parent
            config_dir = project_root / 'configs'

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def list_configs(self) -> List[str]:
        """
        List all available configuration names

        Returns:
            List of configuration names (without .json extension)
        """
        configs = []
        for file in self.config_dir.glob('*.json'):
            configs.append(file.stem)
        return sorted(configs)

    def load_config(self, name: str) -> Optional[Dict]:
        """
        Load a configuration by name

        Args:
            name: Configuration name (without .json extension)

        Returns:
            Configuration dictionary or None if not found
        """
        config_path = self.config_dir / f"{name}.json"
        if not config_path.exists():
            return None

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading config {name}: {e}")
            return None

    def save_config(self, name: str, config: Dict) -> bool:
        """
        Save a configuration

        Args:
            name: Configuration name (without .json extension)
            config: Configuration dictionary

        Returns:
            True if saved successfully, False otherwise
        """
        # Validate configuration
        validation_error = self.validate_config(config)
        if validation_error:
            print(f"Invalid configuration: {validation_error}")
            return False

        config_path = self.config_dir / f"{name}.json"
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config {name}: {e}")
            return False

    def delete_config(self, name: str) -> bool:
        """
        Delete a configuration

        Args:
            name: Configuration name (without .json extension)

        Returns:
            True if deleted successfully, False otherwise
        """
        config_path = self.config_dir / f"{name}.json"
        if not config_path.exists():
            return False

        try:
            config_path.unlink()
            return True
        except OSError as e:
            print(f"Error deleting config {name}: {e}")
            return False

    def validate_config(self, config: Dict) -> Optional[str]:
        """
        Validate a configuration dictionary

        Args:
            config: Configuration dictionary

        Returns:
            Error message if invalid, None if valid
        """
        # Check required fields
        required_fields = ['name', 'architecture', 'max_density', 'languages']
        for field in required_fields:
            if field not in config:
                return f"Missing required field: {field}"

        # Validate architecture
        if config['architecture'] not in self.VALID_ARCHITECTURES:
            return f"Invalid architecture: {config['architecture']}"

        # Validate max_density
        if config['max_density'] not in self.VALID_DENSITIES:
            return f"Invalid max_density: {config['max_density']}"

        # Validate languages (must be a list)
        if not isinstance(config['languages'], list) or len(config['languages']) == 0:
            return "Languages must be a non-empty list"

        return None

    def get_density_rank(self, density: str) -> int:
        """
        Get the rank of a density in the hierarchy

        Args:
            density: Density string (e.g., 'xhdpi')

        Returns:
            Rank (0-6), or -1 if invalid
        """
        try:
            return self.DENSITY_ORDER.index(density)
        except ValueError:
            return -1

    def is_density_allowed(self, density: str, max_density: str) -> bool:
        """
        Check if a density is allowed given a maximum density

        Args:
            density: Density to check
            max_density: Maximum allowed density

        Returns:
            True if density <= max_density in the hierarchy
        """
        density_rank = self.get_density_rank(density)
        max_rank = self.get_density_rank(max_density)

        if density_rank == -1 or max_rank == -1:
            return False

        return density_rank <= max_rank

    def create_default_config(self):
        """Create a default configuration if it doesn't exist"""
        default_config = {
            "name": "Default Android TV",
            "architecture": "arm64-v8a",
            "max_density": "xhdpi",
            "languages": ["en"],
            "description": "Default configuration for most Android TVs"
        }

        if not (self.config_dir / "default.json").exists():
            self.save_config("default", default_config)
