#!/usr/bin/env python3
"""
APKM Repackager
Main entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application metadata
    app.setApplicationName("APKM Repackager")
    app.setOrganizationName("APKM Repackager")
    app.setApplicationVersion("1.0.0")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
