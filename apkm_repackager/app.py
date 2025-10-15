"""PySide6-based macOS application for repackaging APKM bundles."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import ConfigManager, DEFAULT_ABIS, DEFAULT_LANGUAGES, Preferences
from .repackager import APKInstaller, APKMRepackager, RepackagingError, SigningError
from .split_filters import DPI_ORDER


class DropArea(QLabel):
    """Widget that accepts .apkm files via drag and drop."""

    fileDropped = Signal(str)

    def __init__(self) -> None:
        super().__init__("将 .apkm 文件拖拽到此处")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            """
            QLabel {
                border: 2px dashed #888;
                padding: 32px;
                font-size: 16px;
                color: #444;
                border-radius: 12px;
            }
            """
        )

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and urls[0].toLocalFile().lower().endswith(".apkm"):
                event.acceptProposedAction()
                return
        event.ignore()

    def dropEvent(self, event: QDropEvent) -> None:
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            local_file = url.toLocalFile()
            if local_file.lower().endswith(".apkm"):
                self.fileDropped.emit(local_file)
                self.setText(Path(local_file).name)
                return
        event.ignore()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("APKM Repackager")
        self.config_manager = ConfigManager()
        self.preferences = self.config_manager.load_preferences()
        self.recent_targets = self.config_manager.load_recent_adb_targets()

        self.repackager: APKMRepackager | None = None
        self.installer = APKInstaller()
        self.current_apkm: Path | None = None
        self.last_output_apk: Path | None = None

        central = QWidget()
        layout = QVBoxLayout(central)

        self.drop_area = DropArea()
        self.drop_area.fileDropped.connect(self._on_file_dropped)
        layout.addWidget(self.drop_area)

        layout.addWidget(self._create_preferences_group())
        layout.addWidget(self._create_adb_group())

        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view, stretch=1)

        action_layout = QHBoxLayout()
        self.repackage_button = QPushButton("重新打包")
        self.repackage_button.clicked.connect(self._handle_repackage)
        action_layout.addWidget(self.repackage_button)

        self.repackage_install_button = QPushButton("打包并安装")
        self.repackage_install_button.clicked.connect(self._handle_repackage_and_install)
        action_layout.addWidget(self.repackage_install_button)

        self.install_button = QPushButton("仅安装上次生成的 APK")
        self.install_button.clicked.connect(self._handle_install_last)
        action_layout.addWidget(self.install_button)

        layout.addLayout(action_layout)
        self.setCentralWidget(central)
        self._refresh_repackager()

    def _create_preferences_group(self) -> QGroupBox:
        group = QGroupBox("打包配置")
        layout = QGridLayout(group)

        self.abi_checkboxes: Dict[str, QCheckBox] = {}
        abi_layout = QVBoxLayout()
        for abi in DEFAULT_ABIS:
            checkbox = QCheckBox(abi)
            checkbox.setChecked(abi in self.preferences.selected_abis)
            self.abi_checkboxes[abi] = checkbox
            abi_layout.addWidget(checkbox)
        layout.addWidget(QLabel("ABI 切片"), 0, 0)
        layout.addLayout(abi_layout, 0, 1)

        self.language_checkboxes: Dict[str, QCheckBox] = {}
        lang_layout = QVBoxLayout()
        for lang in DEFAULT_LANGUAGES:
            checkbox = QCheckBox(lang)
            checkbox.setChecked(lang in self.preferences.allowed_languages)
            self.language_checkboxes[lang] = checkbox
            lang_layout.addWidget(checkbox)
        layout.addWidget(QLabel("语言"), 1, 0)
        layout.addLayout(lang_layout, 1, 1)

        self.dpi_combo = QComboBox()
        for dpi in DPI_ORDER:
            self.dpi_combo.addItem(dpi)
        index = max(0, DPI_ORDER.index(self.preferences.max_dpi)) if self.preferences.max_dpi in DPI_ORDER else 0
        self.dpi_combo.setCurrentIndex(index)
        layout.addWidget(QLabel("最大 DPI"), 2, 0)
        layout.addWidget(self.dpi_combo, 2, 1)

        self.apksigner_edit = QLineEdit(self.preferences.apksigner_path or "")
        layout.addWidget(QLabel("apksigner 路径 (可选)"), 3, 0)
        layout.addWidget(self.apksigner_edit, 3, 1)

        self.keystore_edit = QLineEdit(self.preferences.keystore_path or "")
        layout.addWidget(QLabel("自定义 keystore (可选)"), 4, 0)
        layout.addWidget(self.keystore_edit, 4, 1)

        self.save_pref_button = QPushButton("保存配置")
        self.save_pref_button.clicked.connect(self._save_preferences)
        layout.addWidget(self.save_pref_button, 5, 1)
        return group

    def _create_adb_group(self) -> QGroupBox:
        group = QGroupBox("ADB 安装")
        form = QFormLayout(group)

        self.adb_target_combo = QComboBox()
        self.adb_target_combo.setEditable(True)
        self.adb_target_combo.addItem("")
        for target in self.recent_targets:
            self.adb_target_combo.addItem(target)
        if self.preferences.adb_target:
            self.adb_target_combo.setCurrentText(self.preferences.adb_target)
        form.addRow("IP:端口", self.adb_target_combo)
        return group

    def _refresh_repackager(self) -> None:
        self.repackager = APKMRepackager(
            allowed_abis=self.preferences.selected_abis,
            allowed_languages=self.preferences.allowed_languages,
            max_dpi=self.preferences.max_dpi,
            apksigner_path=self.preferences.apksigner_path,
            keystore_path=self.preferences.keystore_path,
            keystore_alias=self.preferences.keystore_alias,
            keystore_password=self.preferences.keystore_password,
        )

    def _log(self, message: str) -> None:
        self.log_view.appendPlainText(message)

    def _on_file_dropped(self, file_path: str) -> None:
        self.current_apkm = Path(file_path)
        self._log(f"已载入: {self.current_apkm}")

    def _save_preferences(self) -> None:
        selected_abis = [abi for abi, box in self.abi_checkboxes.items() if box.isChecked()]
        languages = [lang for lang, box in self.language_checkboxes.items() if box.isChecked()]
        if not selected_abis:
            QMessageBox.warning(self, "配置错误", "请至少选择一个 ABI。")
            return
        if not languages:
            QMessageBox.warning(self, "配置错误", "请至少选择一种语言。")
            return
        self.preferences.selected_abis = selected_abis
        self.preferences.allowed_languages = languages
        self.preferences.max_dpi = self.dpi_combo.currentText()
        self.preferences.apksigner_path = self.apksigner_edit.text().strip() or None
        self.preferences.keystore_path = self.keystore_edit.text().strip() or None
        self.preferences.adb_target = self.adb_target_combo.currentText().strip() or None
        self.config_manager.save_preferences(self.preferences)
        targets: List[str] = [self.adb_target_combo.itemText(i) for i in range(self.adb_target_combo.count()) if self.adb_target_combo.itemText(i)]
        current_target = self.preferences.adb_target
        if current_target and current_target not in targets:
            targets.insert(0, current_target)
            self.adb_target_combo.insertItem(0, current_target)
        self.config_manager.save_recent_adb_targets(targets)
        self._refresh_repackager()
        self._log("配置已保存。")

    def _handle_repackage(self) -> None:
        if not self.current_apkm:
            QMessageBox.information(self, "未选择文件", "请先拖入一个 .apkm 文件。")
            return
        assert self.repackager is not None
        try:
            self._log("开始重新打包...")
            output = self.repackager.repackage(self.current_apkm)
            self.last_output_apk = output
            self._log(f"生成 APK: {output}")
            QMessageBox.information(self, "完成", f"APK 已生成:\n{output}")
        except SigningError as exc:
            QMessageBox.critical(self, "签名失败", str(exc))
            self._log(f"签名失败: {exc}")
        except RepackagingError as exc:
            QMessageBox.critical(self, "打包失败", str(exc))
            self._log(f"打包失败: {exc}")

    def _handle_repackage_and_install(self) -> None:
        self._handle_repackage()
        if self.last_output_apk:
            self._handle_install(self.last_output_apk)

    def _handle_install_last(self) -> None:
        if not self.last_output_apk:
            QMessageBox.information(self, "无可安装的 APK", "请先生成一个 APK。")
            return
        self._handle_install(self.last_output_apk)

    def _handle_install(self, apk_path: Path) -> None:
        target = self.adb_target_combo.currentText().strip()
        try:
            self._log(f"通过 adb 安装 {apk_path}...")
            result = self.installer.install(apk_path, target if target else None)
            stdout = result.stdout.decode("utf-8", "ignore") if result.stdout else ""
            stderr = result.stderr.decode("utf-8", "ignore") if result.stderr else ""
            if stdout:
                self._log(stdout)
            if stderr:
                self._log(stderr)
            QMessageBox.information(self, "安装完成", "应用已通过 adb 安装。")
            if target:
                existing = [self.adb_target_combo.itemText(i) for i in range(self.adb_target_combo.count())]
                if target not in existing:
                    self.adb_target_combo.insertItem(0, target)
                self.preferences.adb_target = target
                self.config_manager.save_preferences(self.preferences)
        except RepackagingError as exc:
            QMessageBox.critical(self, "安装失败", str(exc))
            self._log(f"安装失败: {exc}")


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 720)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
