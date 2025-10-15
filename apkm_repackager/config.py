"""Configuration management for APKM Repackager."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Set


APP_NAME = "APKM Repackager"
DEFAULT_ABIS = ["arm64_v8a", "armeabi_v7a", "x86_64", "x86"]
DEFAULT_LANGUAGES = ["en", "zh"]
DEFAULT_MAX_DPI = "xxhdpi"
CONFIG_FILENAME = "config.json"
ADB_HISTORY_FILENAME = "adb_history.json"


@dataclass
class Preferences:
    """Persisted user preferences."""

    selected_abis: List[str]
    allowed_languages: List[str]
    max_dpi: str
    apksigner_path: str | None = None
    keystore_path: str | None = None
    keystore_alias: str = "apkm_repackager"
    keystore_password: str = "apkm_repackager"
    adb_target: str | None = None

    @classmethod
    def default(cls) -> "Preferences":
        return cls(
            selected_abis=list(DEFAULT_ABIS),
            allowed_languages=list(DEFAULT_LANGUAGES),
            max_dpi=DEFAULT_MAX_DPI,
        )


class ConfigManager:
    """Handles loading and saving preferences in the user's config directory."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self.config_dir = config_dir or Path(
            os.environ.get("APKM_REPACKAGER_CONFIG", self._default_config_dir())
        )
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = self.config_dir / CONFIG_FILENAME
        self.adb_history_path = self.config_dir / ADB_HISTORY_FILENAME

    @staticmethod
    def _default_config_dir() -> str:
        base = Path.home() / "Library" / "Application Support" / APP_NAME
        return str(base)

    def load_preferences(self) -> Preferences:
        if not self.config_path.exists():
            return Preferences.default()
        try:
            data = json.loads(self.config_path.read_text())
            return Preferences(
                selected_abis=data.get("selected_abis", DEFAULT_ABIS),
                allowed_languages=data.get("allowed_languages", DEFAULT_LANGUAGES),
                max_dpi=data.get("max_dpi", DEFAULT_MAX_DPI),
                apksigner_path=data.get("apksigner_path"),
                keystore_path=data.get("keystore_path"),
                keystore_alias=data.get("keystore_alias", "apkm_repackager"),
                keystore_password=data.get("keystore_password", "apkm_repackager"),
                adb_target=data.get("adb_target"),
            )
        except json.JSONDecodeError:
            return Preferences.default()

    def save_preferences(self, preferences: Preferences) -> None:
        self.config_path.write_text(json.dumps(asdict(preferences), indent=2))

    def load_recent_adb_targets(self) -> List[str]:
        if not self.adb_history_path.exists():
            return []
        try:
            data = json.loads(self.adb_history_path.read_text())
            if isinstance(data, list):
                return [str(item) for item in data]
        except json.JSONDecodeError:
            pass
        return []

    def save_recent_adb_targets(self, targets: List[str]) -> None:
        unique_targets: List[str] = []
        seen: Set[str] = set()
        for target in targets:
            if target and target not in seen:
                unique_targets.append(target)
                seen.add(target)
        self.adb_history_path.write_text(json.dumps(unique_targets, indent=2))
