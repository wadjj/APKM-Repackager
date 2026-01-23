# APKM-Repackager - Claude Development Guide

## Project Overview

APKM-Repackager is a **macOS GUI application** for converting APKM files (Android App Bundle split APKs) into single APK files that can be installed on Android-based TVs (like Xiaomi TVs).

## Project Purpose

This tool solves a specific compatibility issue:
- **Problem**: APKM files contain multiple APK slices (different architectures, screen densities, languages, etc.)
- **Challenge**: Many Android TVs don't support installing APKM files or split APK packages directly
- **Solution**: Extract only the necessary slices for the target device and repackage them into a single installable APK

### Use Case
Users with Android TVs (like Xiaomi) who want to install apps distributed as APKM files can use this tool to:
1. Extract the APKM file
2. Identify and select the required slices (correct architecture, density, etc.)
3. Merge them into a single APK
4. Install the resulting APK on their TV

## Project Structure

```
APKM-Repackager/
├── README.md              # Project documentation
├── CLAUDE.MD             # This file - Claude development guide
├── requirements.txt      # Python dependencies
├── main.py               # Main application entry point (GUI)
├── ui/                   # GUI components
│   ├── main_window.py    # Main application window
│   ├── config_dialog.py  # Configuration management dialog
│   └── progress_dialog.py # Progress/status dialog
├── lib/                  # Core logic modules
│   ├── apkm_parser.py    # APKM extraction and parsing
│   ├── apk_merger.py     # APK merging logic
│   ├── signer.py         # APK signing utilities
│   └── config_manager.py # Configuration management
├── configs/              # Device configuration profiles
│   ├── default.json      # Default configuration
│   └── xiaomi-tv.json    # Example: Xiaomi TV profile
├── resources/            # Application resources
│   ├── icons/            # App icons
│   └── images/           # UI images
└── .git/                 # Git repository
```

## How It Works

The tool follows this workflow:

1. **Extract APKM**: Unzip the APKM file to access individual APK slices
2. **Parse Manifests**: Read AndroidManifest.xml from each slice to understand their purpose
3. **Identify Slices**: Categorize slices by type (base, architecture, density, language, etc.)
4. **Select Required Slices**: Based on target device specs or user input, select necessary slices
5. **Merge APKs**: Combine selected slices into a single APK structure
6. **Sign APK**: Sign the merged APK to make it installable
7. **Output**: Produce a single APK file ready for installation on Android TV

## macOS GUI Design

### Main Window Layout
The application features a clean, simple macOS-style interface:

**Header Section:**
- App icon and title "APKM Repackager"

**Input Section:**
- Large drag-and-drop area with dashed border
- Text: "Drag APKM file here or click to browse"
- Selected file path displays below

**Configuration Section:**
- Label: "Device Configuration"
- Dropdown menu with saved configurations
- Display panel showing current config details
- Button: "Manage Configurations..."

**Preview Section:**
- Button: "Preview Selected Slices"
- Expandable/collapsible panel showing slice breakdown

**Action Section:**
- Primary button: "Convert to APK"
- Progress bar (hidden until conversion starts)
- Status text (e.g., "Ready", "Converting...", "Complete!")

### Menu Bar
- **File**
  - Open APKM... (Cmd+O)
  - Batch Convert...
  - Manage Configurations... (Cmd+,)
  - Close Window (Cmd+W)
  - Quit (Cmd+Q)
- **Edit**
  - (Standard macOS edit menu)
- **Window**
  - Minimize (Cmd+M)
  - Zoom
- **Help**
  - APKM Repackager Help
  - About

### Design Principles
- Native macOS look and feel (use system fonts, colors, spacing)
- Minimize clicks: most common operation should take 3 clicks or less
- Clear visual feedback for all actions
- Non-blocking UI: long operations use progress indicators
- Error messages in friendly, actionable language

## Configuration System

The tool supports saving multiple device configurations (profiles) to avoid specifying parameters repeatedly. This is especially useful for users with multiple TVs or for sharing configurations.

### Configuration Profile Structure

Each configuration profile contains:
- **Device Name**: Identifier for the TV/device (e.g., "Xiaomi Mi TV 4S")
- **Architecture**: Target CPU architecture (e.g., `arm64-v8a`, `armeabi-v7a`)
- **Max Screen Density**: Maximum screen density supported by the device
  - The tool will select the highest available density **up to and including** this value
  - Common values: `ldpi`, `mdpi`, `hdpi`, `xhdpi`, `xxhdpi`, `xxxhdpi`, `tvdpi`
  - Example: If max is `xhdpi`, tool won't include `xxhdpi` or `xxxhdpi` slices
- **Language Preferences**: Ordered list of preferred languages (e.g., `["zh-CN", "en"]`)
  - Languages are prioritized in order
  - If first preference (e.g., Simplified Chinese) is available, it will be included
  - Falls back to next preference if first isn't available

### Example Configuration (JSON format)

```json
{
  "name": "Xiaomi Mi TV 4S",
  "architecture": "arm64-v8a",
  "max_density": "xhdpi",
  "languages": ["zh-CN", "en"],
  "description": "Xiaomi Android TV with ARM64 processor"
}
```

### Configuration Usage Benefits

1. **Convenience**: Save settings once, reuse for all APKM conversions
2. **Consistency**: Ensure all APKs are optimized the same way for a device
3. **Sharing**: Share configurations with others who have the same TV model
4. **Multiple Devices**: Maintain different profiles for different TVs in your household

## Technology Stack

### GUI Framework (macOS)
- **PyQt6** or **PySide6** - Modern Qt-based GUI framework with native macOS look and feel
  - Alternative: **tkinter** - Built-in Python GUI (simpler but less native-looking)
  - Alternative: **rumps** - For macOS menu bar app (if minimal UI desired)
- **py2app** - For packaging Python app as macOS `.app` bundle

### Core Technologies
- **Python 3.9+** - Main programming language
- **zipfile** (Python built-in) - For APKM extraction (ZIP archives)
- **androguard** or **pyaxmlparser** - For parsing AndroidManifest.xml from APK files
- **apksigner** (Android SDK Build Tools) - For signing merged APK
- **Java/JDK** - Required by Android SDK tools

### Development Tools
- **macOS 10.14+** - Target platform
- **Xcode Command Line Tools** - For macOS development

## Development Guidelines

### Code Style
- Write clean, readable, and maintainable code
- Include comments for complex logic
- Follow language-specific best practices
- Keep security considerations in mind

### Security Considerations
- Validate all input files
- Handle file operations safely
- Avoid command injection vulnerabilities
- Implement proper error handling
- Log operations for audit trails

### Testing
- Test with various APKM files from different sources
- Verify merged APKs install correctly on Android TVs
- Test with different architecture combinations
- Validate APK signatures after merging
- Test error handling for corrupted APKM files
- Ensure all necessary slices are included in merged APK
- Document test cases and results

## Key Features (Planned)

### Core Functionality
- [ ] APKM file extraction (unzip/decompress)
- [ ] Parse and analyze APK slices within APKM
- [ ] Identify and categorize slices (base, arch, density, language)
- [ ] Select appropriate slices based on configuration
- [ ] Merge selected APK slices into single APK
- [ ] Sign the merged APK for installation
- [ ] Validate merged APK integrity

### Configuration Management
- [ ] Save and load device configuration profiles (JSON format)
- [ ] Support multiple configurations for different devices
- [ ] Create, edit, list, and delete configuration profiles
- [ ] Set default configuration
- [ ] Configuration validation

### Architecture & Density Support
- [ ] Support for multiple architectures (armeabi-v7a, arm64-v8a, x86, x86_64)
- [ ] Support for screen densities (ldpi, mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi, tvdpi)
- [ ] Intelligent density selection (max density threshold)
- [ ] Fallback to lower density if exact match not available

### Language Support
- [ ] Multi-language preference ordering
- [ ] Prioritized language selection (e.g., zh-CN preferred, fallback to en)
- [ ] Include only preferred languages to reduce APK size

### Interface & Usability (macOS GUI)
- [ ] Drag-and-drop APKM file support
- [ ] Visual configuration selector (dropdown for saved configs)
- [ ] Interactive slice preview (show what will be included)
- [ ] Real-time progress bar during conversion
- [ ] Configuration manager UI (create, edit, delete profiles)
- [ ] File picker for input/output
- [ ] Visual feedback and error messages
- [ ] Batch processing with queue management
- [ ] macOS native look and feel
- [ ] Menu bar integration
- [ ] Keyboard shortcuts (Cmd+O for open, etc.)

## Dependencies

### System Requirements
- **macOS 10.14+** - Target operating system
- **Python 3.9+** - Main runtime environment
- **Android SDK Build Tools** - For apksigner and other tools
- **Java/JDK** - Required by Android SDK tools
- **Xcode Command Line Tools** - For building macOS app

### Python Packages (requirements.txt)
**GUI Framework:**
- `PyQt6` or `PySide6` - Qt-based GUI framework for macOS
- `py2app` - For creating standalone macOS application bundle

**Core Functionality:**
- `androguard` or `pyaxmlparser` - For parsing AndroidManifest.xml from APK files
- Standard library modules: `zipfile`, `pathlib`, `json`, `shutil`

**Optional:**
- `apktool` - For deeper APK analysis if needed

## Usage Patterns

### For Claude

When working on this project:
1. **GUI Development**: Focus on native macOS look and feel using PyQt6/PySide6
2. **Configuration Validation**: Validate configuration files for correct format and valid values
3. **File Operations**: Check file paths and permissions before operations; use macOS file dialogs
4. **Testing**: Test with various APKM files and different configurations
5. **Density Logic**: Ensure density hierarchy is correctly implemented
6. **Language Logic**: Verify language preference ordering works as expected
7. **Error Handling**: Test edge cases (missing slices, unavailable languages, corrupted files, etc.)
8. **UI Responsiveness**: Keep UI responsive during long operations (use threading/async)
9. **macOS Guidelines**: Follow Apple Human Interface Guidelines for macOS apps
10. **Documentation**: Document any new features or modifications
11. **Updates**: Update this CLAUDE.MD file as the project evolves

### macOS-Specific Considerations
- Use native file dialogs (`QFileDialog` with native mode)
- Support drag-and-drop for APKM files
- Handle macOS file permissions and app sandboxing
- Support dark mode (system appearance)
- Use macOS keyboard shortcuts (Cmd instead of Ctrl)
- Package as `.app` bundle using `py2app`
- Consider code signing for distribution

### GUI Workflow

Expected user workflow in the macOS app:

**Main Window:**
1. **Select APKM File**
   - Drag and drop APKM file onto window, OR
   - Click "Select APKM" button to open file picker
   - File path displays in the UI

2. **Choose Configuration**
   - Dropdown menu shows saved device configurations
   - Select desired configuration (e.g., "Xiaomi Mi TV 4S")
   - Configuration details display below (arch, density, languages)

3. **Preview Slices** (Optional)
   - Click "Preview" button to see which slices will be included
   - Shows: base APK, selected architecture, density, languages
   - Estimated output APK size

4. **Convert**
   - Click "Convert" button
   - Progress bar shows conversion status
   - Notification when complete
   - Converted APK saved to selected location

**Configuration Manager:**
- Access via menu: `File > Manage Configurations`
- Visual list of saved configurations
- Buttons: New, Edit, Delete, Duplicate
- Form to create/edit: Name, Architecture dropdown, Max Density dropdown, Language checkboxes

**Batch Processing:**
- Access via menu: `File > Batch Convert`
- Select multiple APKM files
- Choose configuration
- Queue shows all files with progress
- Convert all at once

## Important Notes

### APKM File Structure
- APKM files are ZIP archives containing multiple APK files
- Typically includes: base APK + split APKs (architecture, density, language, etc.)
- Each slice has a specific naming convention indicating its purpose
- AndroidManifest.xml in each APK contains configuration details

### Android TV Compatibility
- Most Android TVs use ARM architecture (arm64-v8a or armeabi-v7a)
- Common TV screen densities: hdpi, xhdpi, or tvdpi
- TVs typically don't need all language packs
- The merged APK must maintain proper manifest merging

### Screen Density Selection
- **Max Density Threshold**: When `max_density` is set (e.g., `xhdpi`), the tool includes the highest available density up to that limit
- **Example**: If max is `xhdpi` and APKM contains `mdpi`, `hdpi`, `xhdpi`, `xxhdpi`:
  - Tool will select `xhdpi` (highest available ≤ max)
  - Will NOT include `xxhdpi` slices (exceeds max)
- **Rationale**: Including higher density resources wastes space and may cause compatibility issues on lower-spec TVs
- **Density hierarchy**: `ldpi` < `mdpi` < `hdpi` < `tvdpi` < `xhdpi` < `xxhdpi` < `xxxhdpi`

### Language Preferences
- **Priority Order**: Languages are specified in preference order (e.g., `["zh-CN", "en"]`)
- **First Available Wins**: Tool includes the first available language from the preference list
- **Fallback**: If primary language (zh-CN) unavailable, falls back to next (en)
- **APK Size Optimization**: Only includes preferred languages, excluding unnecessary language packs
- **Common Language Codes**:
  - `zh-CN` - Simplified Chinese
  - `zh-TW` - Traditional Chinese
  - `en` - English
  - `ja` - Japanese
  - `ko` - Korean
  - And many others following ISO 639-1 / BCP 47 standards

### Key Challenges
- Correctly identifying which slices are mandatory vs optional
- Properly merging manifests from multiple APKs
- Maintaining valid APK signature after merging
- Handling different APKM formats from various sources
- Accurate density comparison and selection
- Language code matching across different naming conventions

## Example GUI Workflow

### Creating a Configuration

1. **Open Configuration Manager**:
   - Click menu: `File > Manage Configurations`
   - Click "New Configuration" button

2. **Fill in Configuration Form**:
   - **Name**: "My Xiaomi Mi TV"
   - **Architecture**: Select "arm64-v8a" from dropdown
   - **Max Density**: Select "xhdpi" from dropdown
   - **Languages**: Check boxes for "Simplified Chinese (zh-CN)" and "English (en)"
   - **Description**: "Living room Xiaomi TV with 1080p display"
   - Click "Save"

3. **Configuration is now saved** to `configs/my-xiaomi-tv.json`

### Converting APKM with GUI

1. **Launch the app** (double-click APKM Repackager.app)

2. **Load APKM file**:
   - Drag `netflix.apkm` onto the main window, OR
   - Click "Select APKM" and choose `netflix.apkm`

3. **Select Configuration**:
   - Click configuration dropdown
   - Select "My Xiaomi Mi TV" from list
   - UI shows: Architecture: arm64-v8a, Max Density: xhdpi, Languages: zh-CN, en

4. **Preview** (optional):
   - Click "Preview Slices" button
   - Dialog shows which slices will be included:
     - ✓ base.apk
     - ✓ split_config.arm64_v8a.apk
     - ✓ split_config.xhdpi.apk
     - ✓ split_config.zh.apk
     - ✓ split_config.en.apk
   - Shows estimated output size

5. **Convert**:
   - Click "Convert" button
   - Choose save location for output APK
   - Progress bar shows: "Extracting APKM... Merging slices... Signing APK..."
   - Success notification: "Netflix.apk created successfully!"

**The app automatically**:
- Extracts netflix.apkm
- Finds all APK slices inside
- Selects arm64-v8a architecture slice
- Selects highest density ≤ xhdpi
- Selects zh-CN language if available, otherwise en
- Merges selected slices + base APK
- Signs the merged APK
- Saves to chosen location

### Configuration for Different Scenarios

**High-end TV** (4K, powerful processor):
```json
{
  "name": "Samsung 4K TV",
  "architecture": "arm64-v8a",
  "max_density": "xxxhdpi",
  "languages": ["en"]
}
```

**Older TV** (720p, lower specs):
```json
{
  "name": "Old Android TV Box",
  "architecture": "armeabi-v7a",
  "max_density": "hdpi",
  "languages": ["en", "zh-CN"]
}
```

**Chinese Market TV** (prefer Chinese UI):
```json
{
  "name": "Xiaomi TV China",
  "architecture": "arm64-v8a",
  "max_density": "xhdpi",
  "languages": ["zh-CN", "zh-TW", "en"]
}
```

## Git Workflow

- Default branch: main
- Feature branches: Use descriptive names
- Commit messages: Clear and descriptive
- Always test before committing changes

## Future Considerations

### Application Features
- Auto-detection from connected Android device via ADB
- Cloud configuration sharing (public repository of TV profiles)
- Support for XAPK format (similar to APKM)
- Dark mode support for macOS
- Preferences/Settings panel
- Recent files menu
- Automatic updates mechanism

### Technical Improvements
- Performance optimization for large APKs
- Logging and error reporting
- Crash reporting and diagnostics
- Code signing and notarization for macOS distribution
- Multi-threaded conversion for better performance

### Distribution
- macOS App Store distribution (requires Apple Developer account)
- Direct download DMG distribution
- Homebrew cask formula
- Auto-updater (Sparkle framework)

### Platform Expansion
- Windows version (if demand exists)
- Linux version (if demand exists)

## Resources

- [Android App Bundles Documentation](https://developer.android.com/guide/app-bundle)
- [Split APKs Overview](https://developer.android.com/guide/app-bundle/configure-base)
- [APK Splits and Configuration](https://developer.android.com/studio/build/configure-apk-splits)
- [Android SDK Build Tools](https://developer.android.com/studio/releases/build-tools)
- [apksigner Documentation](https://developer.android.com/studio/command-line/apksigner)
- [Androguard - Python APK Analysis](https://github.com/androguard/androguard)

---

**Last Updated**: 2026-01-23
**Project Status**: Initial Setup

Keep this file updated as the project evolves to help Claude understand the codebase and development practices.
