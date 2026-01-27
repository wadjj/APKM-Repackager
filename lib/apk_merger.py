"""
APK Merger
Handles merging multiple APK slices into a single APK
"""

import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import List


class APKMerger:
    """Merges multiple APK slices into a single APK file"""

    def __init__(self):
        """Initialize the APK merger"""
        self.temp_dir = None

    def merge(self, apk_files: List[Path], output_path: str) -> bool:
        """
        Merge multiple APK files into a single APK

        Args:
            apk_files: List of APK file paths to merge
            output_path: Path for the output merged APK

        Returns:
            True if merge succeeded, False otherwise
        """
        if not apk_files:
            print("No APK files to merge")
            return False

        try:
            # Create temporary directory for merging
            self.temp_dir = Path(tempfile.mkdtemp(prefix='apk_merge_'))
            merged_dir = self.temp_dir / 'merged'
            merged_dir.mkdir()

            # Extract all APKs and merge their contents
            for apk_file in apk_files:
                if not apk_file.exists():
                    print(f"APK file not found: {apk_file}")
                    continue

                with zipfile.ZipFile(apk_file, 'r') as zip_ref:
                    # Extract all files from this APK
                    for member in zip_ref.namelist():
                        # Skip META-INF directory (signatures will be invalid anyway)
                        if member.startswith('META-INF/'):
                            continue

                        # Extract file to merged directory
                        source = zip_ref.open(member)
                        target_path = merged_dir / member
                        target_path.parent.mkdir(parents=True, exist_ok=True)

                        # For files that exist in multiple APKs, keep the one from base
                        # or overwrite with split configs
                        if not target_path.exists() or 'split_' in apk_file.name:
                            with open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)

            # Create the merged APK
            output_path = Path(output_path)
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
                # Add all files from merged directory
                for file_path in merged_dir.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(merged_dir))
                        zip_out.write(file_path, arcname)

            print(f"Merged APK created: {output_path}")
            return True

        except (zipfile.BadZipFile, OSError) as e:
            print(f"Error merging APKs: {e}")
            return False
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except OSError as e:
                print(f"Error cleaning up temp directory: {e}")

    def estimate_size(self, apk_files: List[Path]) -> int:
        """
        Estimate the size of the merged APK

        Args:
            apk_files: List of APK file paths

        Returns:
            Estimated size in bytes
        """
        total_size = 0
        for apk_file in apk_files:
            if apk_file.exists():
                total_size += apk_file.stat().st_size
        # Estimate is roughly 80% of combined size (accounting for overlap)
        return int(total_size * 0.8)
