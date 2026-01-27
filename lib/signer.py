"""
APK Signer
Handles signing APK files for installation
"""

import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional


class APKSigner:
    """Signs APK files using apksigner or jarsigner"""

    def __init__(self):
        """Initialize the APK signer"""
        self.debug_keystore = None

    def sign_apk(self, apk_path: str, keystore_path: Optional[str] = None,
                 keystore_password: Optional[str] = None,
                 key_alias: Optional[str] = None,
                 key_password: Optional[str] = None) -> bool:
        """
        Sign an APK file

        Args:
            apk_path: Path to the APK file to sign
            keystore_path: Path to keystore (uses debug keystore if None)
            keystore_password: Keystore password
            key_alias: Key alias
            key_password: Key password

        Returns:
            True if signing succeeded, False otherwise
        """
        apk_path = Path(apk_path)
        if not apk_path.exists():
            print(f"APK file not found: {apk_path}")
            return False

        # If no keystore provided, create/use debug keystore
        if keystore_path is None:
            keystore_path = self._get_debug_keystore()
            keystore_password = "android"
            key_alias = "androiddebugkey"
            key_password = "android"

        # Try to use apksigner first (from Android SDK Build Tools)
        if self._sign_with_apksigner(apk_path, keystore_path, keystore_password,
                                      key_alias, key_password):
            return True

        # Fallback to jarsigner (requires Java)
        if self._sign_with_jarsigner(apk_path, keystore_path, keystore_password,
                                      key_alias, key_password):
            return True

        print("Failed to sign APK: apksigner and jarsigner not available")
        return False

    def _sign_with_apksigner(self, apk_path: Path, keystore_path: str,
                            keystore_password: str, key_alias: str,
                            key_password: str) -> bool:
        """
        Sign APK using apksigner from Android SDK Build Tools

        Returns:
            True if signing succeeded, False otherwise
        """
        try:
            # Try to find apksigner in PATH or common locations
            apksigner_cmd = self._find_apksigner()
            if not apksigner_cmd:
                return False

            cmd = [
                apksigner_cmd,
                'sign',
                '--ks', keystore_path,
                '--ks-pass', f'pass:{keystore_password}',
                '--ks-key-alias', key_alias,
                '--key-pass', f'pass:{key_password}',
                str(apk_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"APK signed successfully with apksigner")
                return True
            else:
                print(f"apksigner error: {result.stderr}")
                return False

        except (subprocess.SubprocessError, OSError) as e:
            print(f"Error running apksigner: {e}")
            return False

    def _sign_with_jarsigner(self, apk_path: Path, keystore_path: str,
                            keystore_password: str, key_alias: str,
                            key_password: str) -> bool:
        """
        Sign APK using jarsigner (Java tool)

        Returns:
            True if signing succeeded, False otherwise
        """
        try:
            cmd = [
                'jarsigner',
                '-sigalg', 'SHA256withRSA',
                '-digestalg', 'SHA-256',
                '-keystore', keystore_path,
                '-storepass', keystore_password,
                '-keypass', key_password,
                str(apk_path),
                key_alias
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"APK signed successfully with jarsigner")
                # Run zipalign if available
                self._zipalign_apk(apk_path)
                return True
            else:
                print(f"jarsigner error: {result.stderr}")
                return False

        except (subprocess.SubprocessError, OSError) as e:
            print(f"Error running jarsigner: {e}")
            return False

    def _get_debug_keystore(self) -> str:
        """
        Get or create a debug keystore

        Returns:
            Path to debug keystore
        """
        if self.debug_keystore and Path(self.debug_keystore).exists():
            return self.debug_keystore

        # Check for Android debug keystore in default location
        debug_keystore = Path.home() / '.android' / 'debug.keystore'
        if debug_keystore.exists():
            self.debug_keystore = str(debug_keystore)
            return self.debug_keystore

        # Create a new debug keystore
        keystore_dir = Path.home() / '.apkm_repackager'
        keystore_dir.mkdir(exist_ok=True)
        keystore_path = keystore_dir / 'debug.keystore'

        if not keystore_path.exists():
            self._create_debug_keystore(str(keystore_path))

        self.debug_keystore = str(keystore_path)
        return self.debug_keystore

    def _create_debug_keystore(self, keystore_path: str) -> bool:
        """
        Create a debug keystore using keytool

        Args:
            keystore_path: Path where keystore will be created

        Returns:
            True if creation succeeded, False otherwise
        """
        try:
            cmd = [
                'keytool',
                '-genkeypair',
                '-keystore', keystore_path,
                '-alias', 'androiddebugkey',
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '10000',
                '-storepass', 'android',
                '-keypass', 'android',
                '-dname', 'CN=Android Debug,O=Android,C=US'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Debug keystore created: {keystore_path}")
                return True
            else:
                print(f"keytool error: {result.stderr}")
                return False

        except (subprocess.SubprocessError, OSError) as e:
            print(f"Error creating debug keystore: {e}")
            return False

    def _find_apksigner(self) -> Optional[str]:
        """
        Try to find apksigner executable

        Returns:
            Path to apksigner or None if not found
        """
        # Try to find in PATH
        try:
            result = subprocess.run(['which', 'apksigner'],
                                   capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except OSError:
            pass

        # Try common Android SDK locations
        android_home = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if android_home:
            build_tools = Path(android_home) / 'build-tools'
            if build_tools.exists():
                # Find latest version
                versions = sorted([d for d in build_tools.iterdir() if d.is_dir()],
                                reverse=True)
                for version in versions:
                    apksigner = version / 'apksigner'
                    if apksigner.exists():
                        return str(apksigner)

        return None

    def _zipalign_apk(self, apk_path: Path) -> bool:
        """
        Align APK using zipalign (optimization)

        Args:
            apk_path: Path to APK file

        Returns:
            True if alignment succeeded, False otherwise
        """
        try:
            # Create temporary aligned APK
            aligned_path = apk_path.with_suffix('.aligned.apk')

            cmd = ['zipalign', '-f', '4', str(apk_path), str(aligned_path)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                # Replace original with aligned version
                aligned_path.replace(apk_path)
                print(f"APK aligned successfully")
                return True
            else:
                return False

        except (subprocess.SubprocessError, OSError):
            # zipalign is optional, don't fail if not available
            return False
