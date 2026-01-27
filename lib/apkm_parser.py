"""
APKM Parser
Handles extraction and analysis of APKM files
"""

import zipfile
import tempfile
import shutil
import re
from pathlib import Path
from typing import List, Dict, Optional
from pyaxmlparser import APK


class APKMParser:
    """Parser for APKM files (Android App Bundle split APKs)"""

    def __init__(self, apkm_path: str):
        """
        Initialize the APKM parser

        Args:
            apkm_path: Path to the APKM file
        """
        self.apkm_path = Path(apkm_path)
        self.temp_dir = None
        self.apk_files = []
        self.slices = {}

    def extract(self) -> bool:
        """
        Extract the APKM file to a temporary directory

        Returns:
            True if extraction succeeded, False otherwise
        """
        if not self.apkm_path.exists():
            print(f"APKM file not found: {self.apkm_path}")
            return False

        try:
            # Create temporary directory
            self.temp_dir = Path(tempfile.mkdtemp(prefix='apkm_'))

            # Extract APKM (it's just a ZIP file)
            with zipfile.ZipFile(self.apkm_path, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)

            # Find all APK files in the extracted directory
            self.apk_files = list(self.temp_dir.rglob('*.apk'))

            if not self.apk_files:
                print("No APK files found in APKM")
                return False

            return True
        except (zipfile.BadZipFile, OSError) as e:
            print(f"Error extracting APKM: {e}")
            return False

    def analyze_slices(self) -> Dict:
        """
        Analyze the APK slices to categorize them

        Returns:
            Dictionary with categorized slices
        """
        self.slices = {
            'base': None,
            'architecture': {},
            'density': {},
            'language': {},
            'other': []
        }

        for apk_file in self.apk_files:
            filename = apk_file.name

            # Identify base APK
            if filename == 'base.apk' or not filename.startswith('split_'):
                self.slices['base'] = apk_file
                continue

            # Parse split APK naming convention
            # Common patterns:
            # - split_config.arm64_v8a.apk (architecture)
            # - split_config.armeabi_v7a.apk (architecture)
            # - split_config.xhdpi.apk (density)
            # - split_config.en.apk (language)
            # - split_config.zh.apk (language)

            # Check for architecture
            if 'arm64' in filename or 'arm64_v8a' in filename:
                self.slices['architecture']['arm64-v8a'] = apk_file
            elif 'armeabi' in filename or 'armeabi_v7a' in filename:
                self.slices['architecture']['armeabi-v7a'] = apk_file
            elif 'x86_64' in filename:
                self.slices['architecture']['x86_64'] = apk_file
            elif 'x86' in filename and 'x86_64' not in filename:
                self.slices['architecture']['x86'] = apk_file
            # Check for density
            elif any(density in filename for density in ['ldpi', 'mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi', 'tvdpi']):
                for density in ['ldpi', 'mdpi', 'hdpi', 'tvdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']:
                    if density in filename:
                        self.slices['density'][density] = apk_file
                        break
            # Check for language codes (2-letter or locale codes)
            elif re.search(r'split_config\.(en|zh|ja|ko|fr|de|es|it|pt|ru|ar|hi|th|vi|id|ms|tr|nl|pl|uk|cs|da|fi|nb|sv|el|he|ro|hu|sk|bg|hr|sr|sl|lt|lv|et|ca|eu|gl|af|sq|am|hy|az|be|bn|bs|my|km|ka|gu|kn|ky|lo|mk|ml|mn|mr|ne|or|pa|si|ta|te|tg|ur|uz|zu)', filename):
                # Extract language code
                match = re.search(r'split_config\.([a-z]{2}(_[A-Z]{2})?)', filename)
                if match:
                    lang_code = match.group(1)
                    self.slices['language'][lang_code] = apk_file
            else:
                self.slices['other'].append(apk_file)

        return self.slices

    def get_slice_info(self) -> Dict:
        """
        Get detailed information about available slices

        Returns:
            Dictionary with slice information
        """
        info = {
            'base': self.slices['base'].name if self.slices['base'] else None,
            'architectures': list(self.slices['architecture'].keys()),
            'densities': list(self.slices['density'].keys()),
            'languages': list(self.slices['language'].keys()),
            'other': [f.name for f in self.slices['other']]
        }
        return info

    def select_slices(self, architecture: str, max_density: str, languages: List[str]) -> List[Path]:
        """
        Select appropriate slices based on configuration

        Args:
            architecture: Target architecture (e.g., 'arm64-v8a')
            max_density: Maximum screen density
            languages: Preferred languages in order

        Returns:
            List of APK file paths to include
        """
        selected = []

        # Always include base APK
        if self.slices['base']:
            selected.append(self.slices['base'])

        # Select architecture
        if architecture in self.slices['architecture']:
            selected.append(self.slices['architecture'][architecture])

        # Select density (highest available up to max_density)
        density_order = ['ldpi', 'mdpi', 'hdpi', 'tvdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi']
        max_density_rank = density_order.index(max_density) if max_density in density_order else -1

        best_density = None
        best_rank = -1
        for density in self.slices['density'].keys():
            if density in density_order:
                rank = density_order.index(density)
                if rank <= max_density_rank and rank > best_rank:
                    best_density = density
                    best_rank = rank

        if best_density:
            selected.append(self.slices['density'][best_density])

        # Select language (first available from preferences)
        for lang in languages:
            # Try exact match first
            if lang in self.slices['language']:
                selected.append(self.slices['language'][lang])
                break
            # Try language without region (e.g., 'zh' for 'zh-CN')
            lang_base = lang.split('-')[0]
            if lang_base in self.slices['language']:
                selected.append(self.slices['language'][lang_base])
                break

        return selected

    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and self.temp_dir.exists():
            try:
                shutil.rmtree(self.temp_dir)
            except OSError as e:
                print(f"Error cleaning up temp directory: {e}")

    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
