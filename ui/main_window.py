"""
Main Window for APKM Repackager
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTextEdit, QProgressBar, QFileDialog,
    QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from lib.config_manager import ConfigManager
from lib.apkm_parser import APKMParser
from lib.apk_merger import APKMerger
from lib.signer import APKSigner


class ConversionWorker(QThread):
    """Worker thread for APKM conversion"""
    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(bool, str)  # Success, message

    def __init__(self, apkm_path, output_path, config):
        super().__init__()
        self.apkm_path = apkm_path
        self.output_path = output_path
        self.config = config

    def run(self):
        """Run the conversion process"""
        try:
            # Parse APKM
            self.progress.emit("Extracting APKM file...")
            parser = APKMParser(self.apkm_path)
            if not parser.extract():
                self.finished.emit(False, "Failed to extract APKM file")
                return

            # Analyze slices
            self.progress.emit("Analyzing APK slices...")
            parser.analyze_slices()
            slice_info = parser.get_slice_info()

            # Select slices
            self.progress.emit("Selecting appropriate slices...")
            selected_slices = parser.select_slices(
                self.config['architecture'],
                self.config['max_density'],
                self.config['languages']
            )

            if not selected_slices:
                self.finished.emit(False, "No slices selected for merging")
                return

            # Merge APKs
            self.progress.emit("Merging APK slices...")
            merger = APKMerger()
            if not merger.merge(selected_slices, self.output_path):
                self.finished.emit(False, "Failed to merge APK slices")
                return

            # Sign APK
            self.progress.emit("Signing APK...")
            signer = APKSigner()
            if not signer.sign_apk(self.output_path):
                self.finished.emit(False, "Failed to sign APK")
                return

            # Cleanup
            parser.cleanup()

            self.finished.emit(True, f"APK created successfully!\n\nSaved to: {self.output_path}")

        except Exception as e:
            self.finished.emit(False, f"Error during conversion: {str(e)}")


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.selected_apkm = None
        self.conversion_worker = None

        # Create default config if it doesn't exist
        self.config_manager.create_default_config()

        self.init_ui()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("APKM Repackager")
        self.setMinimumSize(600, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)

        # Header
        header = QLabel("APKM Repackager")
        header.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # File input section
        input_group = QGroupBox("1. Select APKM File")
        input_layout = QVBoxLayout()

        self.drop_area = DropArea()
        self.drop_area.file_dropped.connect(self.on_file_selected)
        input_layout.addWidget(self.drop_area)

        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self.browse_file)
        input_layout.addWidget(btn_browse)

        self.label_selected_file = QLabel("No file selected")
        self.label_selected_file.setStyleSheet("color: #666; font-style: italic;")
        input_layout.addWidget(self.label_selected_file)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Configuration section
        config_group = QGroupBox("2. Device Configuration")
        config_layout = QVBoxLayout()

        config_select_layout = QHBoxLayout()
        config_select_layout.addWidget(QLabel("Configuration:"))
        self.combo_config = QComboBox()
        self.load_configurations()
        self.combo_config.currentTextChanged.connect(self.on_config_changed)
        config_select_layout.addWidget(self.combo_config, 1)

        btn_manage_config = QPushButton("Manage...")
        btn_manage_config.clicked.connect(self.manage_configurations)
        config_select_layout.addWidget(btn_manage_config)
        config_layout.addLayout(config_select_layout)

        self.config_info = QTextEdit()
        self.config_info.setReadOnly(True)
        self.config_info.setMaximumHeight(80)
        self.update_config_display()
        config_layout.addWidget(self.config_info)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Conversion section
        convert_group = QGroupBox("3. Convert")
        convert_layout = QVBoxLayout()

        self.btn_convert = QPushButton("Convert to APK")
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
        """)
        self.btn_convert.clicked.connect(self.convert_apkm)
        self.btn_convert.setEnabled(False)
        convert_layout.addWidget(self.btn_convert)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)
        convert_layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        convert_layout.addWidget(self.status_label)

        convert_group.setLayout(convert_layout)
        layout.addWidget(convert_group)

        layout.addStretch()

        # Set up menu bar
        self.create_menu_bar()

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = file_menu.addAction("Open APKM...")
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_file)

        file_menu.addSeparator()

        manage_config_action = file_menu.addAction("Manage Configurations...")
        manage_config_action.setShortcut("Ctrl+,")
        manage_config_action.triggered.connect(self.manage_configurations)

        file_menu.addSeparator()

        quit_action = file_menu.addAction("Quit")
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)

        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = help_menu.addAction("About")
        about_action.triggered.connect(self.show_about)

    def load_configurations(self):
        """Load available configurations into combo box"""
        self.combo_config.clear()
        configs = self.config_manager.list_configs()
        self.combo_config.addItems(configs)

        # Select default if available
        if 'default' in configs:
            self.combo_config.setCurrentText('default')

    def on_config_changed(self):
        """Handle configuration selection change"""
        self.update_config_display()

    def update_config_display(self):
        """Update the configuration info display"""
        config_name = self.combo_config.currentText()
        if not config_name:
            self.config_info.setText("No configuration selected")
            return

        config = self.config_manager.load_config(config_name)
        if not config:
            self.config_info.setText("Error loading configuration")
            return

        info_text = f"<b>Name:</b> {config['name']}<br>"
        info_text += f"<b>Architecture:</b> {config['architecture']}<br>"
        info_text += f"<b>Max Density:</b> {config['max_density']}<br>"
        info_text += f"<b>Languages:</b> {', '.join(config['languages'])}"
        if 'description' in config:
            info_text += f"<br><b>Description:</b> {config['description']}"

        self.config_info.setHtml(info_text)

    def browse_file(self):
        """Open file browser to select APKM file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select APKM File",
            str(Path.home()),
            "APKM Files (*.apkm);;All Files (*)"
        )
        if file_path:
            self.on_file_selected(file_path)

    def on_file_selected(self, file_path):
        """Handle file selection"""
        self.selected_apkm = file_path
        self.label_selected_file.setText(f"Selected: {Path(file_path).name}")
        self.label_selected_file.setStyleSheet("color: #000;")
        self.btn_convert.setEnabled(True)
        self.status_label.setText("Ready to convert")

    def convert_apkm(self):
        """Start APKM conversion"""
        if not self.selected_apkm:
            QMessageBox.warning(self, "No File", "Please select an APKM file first")
            return

        config_name = self.combo_config.currentText()
        config = self.config_manager.load_config(config_name)
        if not config:
            QMessageBox.critical(self, "Configuration Error",
                               "Failed to load configuration")
            return

        # Ask for output location
        default_name = Path(self.selected_apkm).stem + ".apk"
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save APK As",
            str(Path.home() / default_name),
            "APK Files (*.apk)"
        )

        if not output_path:
            return

        # Disable UI during conversion
        self.btn_convert.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Start conversion in worker thread
        self.conversion_worker = ConversionWorker(
            self.selected_apkm, output_path, config
        )
        self.conversion_worker.progress.connect(self.on_conversion_progress)
        self.conversion_worker.finished.connect(self.on_conversion_finished)
        self.conversion_worker.start()

    def on_conversion_progress(self, message):
        """Handle conversion progress update"""
        self.status_label.setText(message)

    def on_conversion_finished(self, success, message):
        """Handle conversion completion"""
        self.progress_bar.setVisible(False)
        self.btn_convert.setEnabled(True)

        if success:
            self.status_label.setText("Conversion completed!")
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("Conversion failed")
            QMessageBox.critical(self, "Error", message)

    def manage_configurations(self):
        """Open configuration management dialog"""
        from ui.config_dialog import ConfigDialog
        dialog = ConfigDialog(self.config_manager, self)
        if dialog.exec():
            # Reload configurations
            self.load_configurations()

    def show_about(self):
        """Show about dialog"""
        about_text = """<h2>APKM Repackager</h2>
        <p>Version 1.0</p>
        <p>A tool for converting APKM files to APK files for Android TV installation.</p>
        <p>© 2026 APKM Repackager Project</p>
        """
        QMessageBox.about(self, "About APKM Repackager", about_text)


class DropArea(QLabel):
    """Drag-and-drop area for APKM files"""
    file_dropped = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("Drag APKM file here\nor click Browse button")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #CCCCCC;
                border-radius: 5px;
                padding: 40px;
                background-color: #F9F9F9;
                color: #666;
            }
        """)
        self.setAcceptDrops(True)
        self.setMinimumHeight(100)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #007AFF;
                    border-radius: 5px;
                    padding: 40px;
                    background-color: #E8F4FF;
                    color: #007AFF;
                }
            """)

    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #CCCCCC;
                border-radius: 5px;
                padding: 40px;
                background-color: #F9F9F9;
                color: #666;
            }
        """)

    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #CCCCCC;
                border-radius: 5px;
                padding: 40px;
                background-color: #F9F9F9;
                color: #666;
            }
        """)

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.apkm'):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "Invalid File",
                                  "Please drop an APKM file")
