"""Core logic for repacking APKM archives into single APKs."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Iterable, List, Sequence

from .split_filters import filter_splits


class RepackagingError(RuntimeError):
    """Raised when repackaging fails."""


class SigningError(RuntimeError):
    """Raised when signing fails."""


class APKMRepackager:
    """Utilities to turn .apkm bundles into single APK files."""

    def __init__(
        self,
        allowed_abis: Sequence[str],
        allowed_languages: Sequence[str],
        max_dpi: str,
        apksigner_path: str | None = None,
        keystore_path: str | None = None,
        keystore_alias: str = "apkm_repackager",
        keystore_password: str = "apkm_repackager",
    ) -> None:
        self.allowed_abis = list(allowed_abis)
        self.allowed_languages = [lang.lower() for lang in allowed_languages]
        self.max_dpi = max_dpi
        self.apksigner_path = apksigner_path or "apksigner"
        self.keystore_path = (
            Path(keystore_path)
            if keystore_path is not None
            else Path.home() / ".apkm-repackager" / "debug.keystore"
        )
        self.keystore_alias = keystore_alias
        self.keystore_password = keystore_password

    def repackage(self, apkm_path: Path, output_dir: Path | None = None) -> Path:
        apkm_path = apkm_path.resolve()
        if not apkm_path.exists():
            raise RepackagingError(f"APKM file not found: {apkm_path}")
        output_dir = output_dir or apkm_path.parent

        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            extracted_dir = tmp_path / "extracted"
            extracted_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(apkm_path) as apkm_zip:
                apkm_zip.extractall(extracted_dir)

            base_apk = extracted_dir / "base.apk"
            if not base_apk.exists():
                raise RepackagingError("The APKM archive did not contain a base.apk file")

            split_paths = [p for p in extracted_dir.glob("config.*.apk") if p.is_file()]
            kept_splits = filter_splits(
                split_paths,
                allowed_abis=self.allowed_abis,
                allowed_languages=self.allowed_languages,
                max_dpi=self.max_dpi,
            )

            merged_apk = tmp_path / f"{apkm_path.stem}_merged.apk"
            self._merge_apks(base_apk, kept_splits, merged_apk)
            signed_apk = tmp_path / f"{apkm_path.stem}_signed.apk"
            self._ensure_keystore()
            self._sign_apk(merged_apk, signed_apk)

            final_apk = output_dir / f"{apkm_path.stem}_filtered.apk"
            shutil.copyfile(signed_apk, final_apk)
            return final_apk

    def _merge_apks(self, base_apk: Path, splits: Iterable[Path], output_apk: Path) -> None:
        entries = {}

        def add_entries(apk_path: Path) -> None:
            with zipfile.ZipFile(apk_path) as apk_zip:
                for info in apk_zip.infolist():
                    if info.filename.endswith("/"):
                        continue
                    entries[info.filename] = apk_zip.read(info.filename)

        add_entries(base_apk)
        for split in splits:
            add_entries(split)

        with zipfile.ZipFile(output_apk, "w", compression=zipfile.ZIP_DEFLATED) as out_zip:
            for filename, data in entries.items():
                out_zip.writestr(filename, data)

    def _ensure_keystore(self) -> None:
        if self.keystore_path.exists():
            return
        self.keystore_path.parent.mkdir(parents=True, exist_ok=True)
        command = [
            "keytool",
            "-genkeypair",
            "-alias",
            self.keystore_alias,
            "-keyalg",
            "RSA",
            "-keysize",
            "2048",
            "-validity",
            "9125",
            "-keystore",
            str(self.keystore_path),
            "-storepass",
            self.keystore_password,
            "-keypass",
            self.keystore_password,
            "-dname",
            "CN=APKM Repackager, OU=Dev, O=APKM, L=Internet, ST=NA, C=US",
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise SigningError(
                "keytool command not found. Install a JDK to enable APK signing."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise SigningError(
                f"Failed to generate keystore: {exc.stderr.decode('utf-8', 'ignore')}"
            ) from exc

    def _sign_apk(self, unsigned_apk: Path, output_apk: Path) -> None:
        command = [
            self.apksigner_path,
            "sign",
            "--ks",
            str(self.keystore_path),
            "--ks-key-alias",
            self.keystore_alias,
            "--ks-pass",
            f"pass:{self.keystore_password}",
            "--key-pass",
            f"pass:{self.keystore_password}",
            "--out",
            str(output_apk),
            str(unsigned_apk),
        ]
        try:
            subprocess.run(command, check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise SigningError(
                "apksigner command not found. Install Android build-tools to enable signing."
            ) from exc
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", "ignore")
            raise SigningError(f"Failed to sign APK: {stderr}") from exc


class APKInstaller:
    """Wrapper around adb to install APK files on a remote device."""

    def __init__(self, adb_path: str = "adb") -> None:
        self.adb_path = adb_path

    def install(self, apk_path: Path, target: str | None = None) -> subprocess.CompletedProcess:
        command: List[str] = [self.adb_path]
        if target:
            command.extend(["-s", target])
        command.extend(["install", "-r", str(apk_path)])
        try:
            result = subprocess.run(command, check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise RepackagingError("adb command not found. Install Android Platform Tools.") from exc
        except subprocess.CalledProcessError as exc:
            raise RepackagingError(
                f"adb install failed: {exc.stderr.decode('utf-8', 'ignore')}"
            ) from exc
        return result
