"""
Configuration Management Dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QLabel, QLineEdit, QComboBox, QTextEdit, QMessageBox,
    QWidget, QGroupBox, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt


class ConfigDialog(QDialog):
    """Dialog for managing device configurations"""

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.init_ui()
        self.load_config_list()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Manage Configurations")
        self.setMinimumSize(700, 500)

        layout = QHBoxLayout(self)

        # Left side: List of configurations
        left_layout = QVBoxLayout()

        left_layout.addWidget(QLabel("Configurations:"))

        self.config_list = QListWidget()
        self.config_list.currentTextChanged.connect(self.on_config_selected)
        left_layout.addWidget(self.config_list)

        # Buttons for list management
        list_buttons = QHBoxLayout()
        btn_new = QPushButton("New")
        btn_new.clicked.connect(self.new_config)
        list_buttons.addWidget(btn_new)

        btn_delete = QPushButton("Delete")
        btn_delete.clicked.connect(self.delete_config)
        list_buttons.addWidget(btn_delete)

        left_layout.addLayout(list_buttons)

        # Right side: Configuration editor
        right_layout = QVBoxLayout()

        # Name field
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.edit_name = QLineEdit()
        name_layout.addWidget(self.edit_name)
        right_layout.addLayout(name_layout)

        # Architecture field
        arch_layout = QHBoxLayout()
        arch_layout.addWidget(QLabel("Architecture:"))
        self.combo_arch = QComboBox()
        self.combo_arch.addItems([
            'arm64-v8a',
            'armeabi-v7a',
            'x86',
            'x86_64'
        ])
        arch_layout.addWidget(self.combo_arch)
        right_layout.addLayout(arch_layout)

        # Max density field
        density_layout = QHBoxLayout()
        density_layout.addWidget(QLabel("Max Density:"))
        self.combo_density = QComboBox()
        self.combo_density.addItems([
            'ldpi',
            'mdpi',
            'hdpi',
            'tvdpi',
            'xhdpi',
            'xxhdpi',
            'xxxhdpi'
        ])
        self.combo_density.setCurrentText('xhdpi')
        density_layout.addWidget(self.combo_density)
        right_layout.addLayout(density_layout)

        # Languages field
        right_layout.addWidget(QLabel("Languages (check preferred):"))

        # Create scrollable area for language checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)

        lang_widget = QWidget()
        lang_layout = QVBoxLayout(lang_widget)

        self.lang_checkboxes = {}
        common_languages = [
            ('en', 'English'),
            ('zh-CN', 'Chinese (Simplified)'),
            ('zh-TW', 'Chinese (Traditional)'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('ar', 'Arabic'),
            ('hi', 'Hindi'),
            ('th', 'Thai'),
            ('vi', 'Vietnamese'),
            ('id', 'Indonesian'),
        ]

        for code, name in common_languages:
            checkbox = QCheckBox(f"{name} ({code})")
            checkbox.setProperty('lang_code', code)
            self.lang_checkboxes[code] = checkbox
            lang_layout.addWidget(checkbox)

        scroll_area.setWidget(lang_widget)
        right_layout.addWidget(scroll_area)

        # Description field
        right_layout.addWidget(QLabel("Description:"))
        self.edit_description = QTextEdit()
        self.edit_description.setMaximumHeight(80)
        right_layout.addWidget(self.edit_description)

        # Save button
        btn_save = QPushButton("Save Configuration")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        btn_save.clicked.connect(self.save_config)
        right_layout.addWidget(btn_save)

        right_layout.addStretch()

        # Add layouts to main layout
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)

        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        btn_close = QPushButton("Close")
        btn_close.clicked.connect(self.accept)
        button_layout.addWidget(btn_close)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def load_config_list(self):
        """Load the list of configurations"""
        self.config_list.clear()
        configs = self.config_manager.list_configs()
        self.config_list.addItems(configs)

    def on_config_selected(self, config_name):
        """Handle configuration selection"""
        if not config_name:
            return

        config = self.config_manager.load_config(config_name)
        if not config:
            QMessageBox.warning(self, "Error", "Failed to load configuration")
            return

        # Populate form fields
        self.edit_name.setText(config.get('name', ''))
        self.combo_arch.setCurrentText(config.get('architecture', 'arm64-v8a'))
        self.combo_density.setCurrentText(config.get('max_density', 'xhdpi'))
        self.edit_description.setText(config.get('description', ''))

        # Clear all language checkboxes
        for checkbox in self.lang_checkboxes.values():
            checkbox.setChecked(False)

        # Check selected languages
        languages = config.get('languages', [])
        for lang in languages:
            # Handle both 'zh-CN' and 'zh' format
            if lang in self.lang_checkboxes:
                self.lang_checkboxes[lang].setChecked(True)
            else:
                # Try base language code
                lang_base = lang.split('-')[0]
                if lang_base in self.lang_checkboxes:
                    self.lang_checkboxes[lang_base].setChecked(True)

    def new_config(self):
        """Create a new configuration"""
        # Clear form
        self.edit_name.setText("New Configuration")
        self.combo_arch.setCurrentIndex(0)
        self.combo_density.setCurrentText('xhdpi')
        self.edit_description.clear()

        # Uncheck all languages
        for checkbox in self.lang_checkboxes.values():
            checkbox.setChecked(False)

        # Check English by default
        if 'en' in self.lang_checkboxes:
            self.lang_checkboxes['en'].setChecked(True)

        self.edit_name.setFocus()
        self.edit_name.selectAll()

    def save_config(self):
        """Save the current configuration"""
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Please enter a configuration name")
            return

        # Collect selected languages
        languages = []
        for code, checkbox in self.lang_checkboxes.items():
            if checkbox.isChecked():
                languages.append(code)

        if not languages:
            QMessageBox.warning(self, "Invalid Input",
                              "Please select at least one language")
            return

        # Create configuration dictionary
        config = {
            'name': name,
            'architecture': self.combo_arch.currentText(),
            'max_density': self.combo_density.currentText(),
            'languages': languages,
            'description': self.edit_description.toPlainText().strip()
        }

        # Generate config file name (sanitize)
        config_filename = name.lower().replace(' ', '-')
        config_filename = ''.join(c for c in config_filename if c.isalnum() or c == '-')

        # Save configuration
        if self.config_manager.save_config(config_filename, config):
            QMessageBox.information(self, "Success",
                                  f"Configuration '{name}' saved successfully")
            self.load_config_list()
            # Select the saved configuration
            items = self.config_list.findItems(config_filename, Qt.MatchFlag.MatchExactly)
            if items:
                self.config_list.setCurrentItem(items[0])
        else:
            QMessageBox.critical(self, "Error", "Failed to save configuration")

    def delete_config(self):
        """Delete the selected configuration"""
        current_item = self.config_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a configuration to delete")
            return

        config_name = current_item.text()

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the configuration '{config_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.config_manager.delete_config(config_name):
                QMessageBox.information(self, "Success",
                                      f"Configuration '{config_name}' deleted")
                self.load_config_list()
                # Clear form
                self.edit_name.clear()
                self.edit_description.clear()
                for checkbox in self.lang_checkboxes.values():
                    checkbox.setChecked(False)
            else:
                QMessageBox.critical(self, "Error", "Failed to delete configuration")
