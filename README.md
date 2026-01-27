# APKM Repackager

A macOS GUI application for converting APKM files (Android App Bundle split APKs) into single APK files that can be installed on Android-based TVs (like Xiaomi TVs).

## Features

- 🖱️ Drag-and-drop APKM file support
- ⚙️ Save multiple device configuration profiles
- 📱 Support for different architectures (ARM, x86)
- 🎨 Intelligent screen density selection
- 🌍 Multi-language preference support
- ✨ Clean, native macOS interface
- 🔐 Automatic APK signing

## Requirements

- macOS 10.14 or later
- Python 3.9 or later
- Java/JDK (for APK signing)
- Android SDK Build Tools (optional, for apksigner)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/wadjj/APKM-Repackager.git
cd APKM-Repackager
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Install Java (if not already installed):
```bash
brew install openjdk
```

## Usage

### Running the Application

Simply run the main script:
```bash
python3 main.py
```

Or make it executable and run directly:
```bash
chmod +x main.py
./main.py
```

### Using the App

1. **Drag and drop** an APKM file into the window (or click Browse)
2. **Select a device configuration** from the dropdown
3. Click **Convert to APK**
4. Choose where to save the output APK file
5. Wait for the conversion to complete

### Managing Configurations

Click **File > Manage Configurations** to:
- Create new device profiles
- Edit existing configurations
- Delete unwanted profiles

Each configuration includes:
- Device name
- Architecture (arm64-v8a, armeabi-v7a, x86, x86_64)
- Maximum screen density
- Preferred languages (in priority order)

## Building macOS App

To create a standalone macOS application:

```bash
python3 setup.py py2app
```

The app will be created in the `dist/` directory.

## Configuration Examples

### Xiaomi TV (included)
- Architecture: arm64-v8a
- Max Density: xhdpi
- Languages: Chinese (Simplified), English

### Default Android TV (included)
- Architecture: arm64-v8a
- Max Density: xhdpi
- Languages: English

## Project Structure

```
APKM-Repackager/
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── setup.py            # py2app configuration
├── ui/                 # GUI components
│   ├── main_window.py
│   └── config_dialog.py
├── lib/                # Core logic
│   ├── config_manager.py
│   ├── apkm_parser.py
│   ├── apk_merger.py
│   └── signer.py
├── configs/            # Device configurations
│   ├── default.json
│   └── xiaomi-tv.json
└── resources/          # App resources
```

## How It Works

1. **Extract**: Unzips the APKM file to access individual APK slices
2. **Analyze**: Identifies base APK, architecture, density, and language slices
3. **Select**: Chooses appropriate slices based on configuration
4. **Merge**: Combines selected slices into a single APK
5. **Sign**: Signs the merged APK for installation
6. **Output**: Produces installable APK file

## Troubleshooting

### "Failed to sign APK"
- Make sure Java/JDK is installed: `java -version`
- The app will create a debug keystore automatically

### "No slices selected for merging"
- The APKM may not contain slices matching your configuration
- Try a different architecture or density setting

### "Failed to extract APKM"
- Make sure the file is a valid APKM file
- The file may be corrupted - try downloading again

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Credits

Built with:
- PyQt6 for the GUI
- pyaxmlparser for APK analysis
- py2app for macOS packaging