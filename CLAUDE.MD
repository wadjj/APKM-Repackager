# APKM-Repackager - Claude Development Guide

## Project Overview

APKM-Repackager is a tool for converting APKM files (Android App Bundle split APKs) into single APK files that can be installed on Android-based TVs (like Xiaomi TVs).

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
├── apkm_repackager.py   # Main script (planned)
├── lib/                 # Helper modules (planned)
│   ├── apkm_parser.py   # APKM extraction and parsing
│   ├── apk_merger.py    # APK merging logic
│   ├── signer.py        # APK signing utilities
│   └── config_manager.py # Configuration management
├── configs/             # Device configuration profiles
│   ├── default.json     # Default configuration
│   └── xiaomi-tv.json   # Example: Xiaomi TV profile
└── .git/                # Git repository
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

Technologies for APKM processing:
- **Python** - Main scripting language for automation and logic
- **ZIP/Unzip utilities** - APKM files are essentially ZIP archives
- **APK Parser libraries** - To read AndroidManifest.xml and analyze APK contents
- **APK signing tools** - For signing the merged APK (apksigner from Android SDK)
- **Android SDK Build Tools** - For various APK operations
- Possible libraries:
  - `zipfile` (Python built-in) for APKM extraction
  - `androguard` or similar for APK analysis
  - `apksigner` for signing

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

### Interface & Usability
- [ ] CLI interface for easy usage
- [ ] List available slices in APKM
- [ ] Dry-run mode to preview selected slices
- [ ] Verbose output for debugging
- [ ] Batch processing support

## Dependencies

Required dependencies:
- **Python 3.7+** - Main runtime environment
- **Android SDK Build Tools** - For apksigner and other tools
- **Java/JDK** - Required by Android SDK tools

Python packages (to be added to requirements.txt):
- `androguard` or `pyaxmlparser` - For parsing AndroidManifest.xml from APK files
- Standard library modules: `zipfile`, `argparse`, `pathlib`, `json`, `shutil`

Optional:
- `pyyaml` - If YAML configuration format is preferred over JSON
- `apktool` - For deeper APK analysis if needed

## Usage Patterns

### For Claude

When working on this project:
1. Validate configuration files for correct format and valid values
2. Check file paths and permissions before operations
3. Test with various APKM files and different configurations
4. Ensure density hierarchy is correctly implemented
5. Verify language preference ordering works as expected
6. Test edge cases (missing slices, unavailable languages, etc.)
7. Document any new features or modifications
8. Update this CLAUDE.MD file as the project evolves

### Command Patterns

Expected usage patterns:
```bash
# Using saved configuration (recommended)
python apkm_repackager.py input.apkm -o output.apk --config xiaomi-tv

# Using default configuration
python apkm_repackager.py input.apkm -o output.apk

# Manual parameters (without configuration)
python apkm_repackager.py input.apkm -o output.apk --arch arm64-v8a --max-density xhdpi --languages zh-CN,en

# List available slices in APKM
python apkm_repackager.py input.apkm --list

# Dry run to preview selected slices (before actual conversion)
python apkm_repackager.py input.apkm --config xiaomi-tv --dry-run

# Configuration management commands
python apkm_repackager.py --create-config xiaomi-tv
python apkm_repackager.py --list-configs
python apkm_repackager.py --show-config xiaomi-tv
python apkm_repackager.py --delete-config xiaomi-tv
python apkm_repackager.py --set-default xiaomi-tv

# Batch processing with same configuration
python apkm_repackager.py *.apkm --config xiaomi-tv --batch
```

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

## Example Configuration Workflow

### Creating a Configuration

1. **Create new configuration interactively**:
   ```bash
   python apkm_repackager.py --create-config my-xiaomi-tv
   # Prompts for: architecture, max_density, languages, description
   ```

2. **Or create from template**:
   ```json
   # configs/my-xiaomi-tv.json
   {
     "name": "My Xiaomi Mi TV",
     "architecture": "arm64-v8a",
     "max_density": "xhdpi",
     "languages": ["zh-CN", "en"],
     "description": "Living room Xiaomi TV with 1080p display"
   }
   ```

### Using the Configuration

```bash
# Convert APKM using saved configuration
python apkm_repackager.py netflix.apkm -o netflix.apk --config my-xiaomi-tv

# The tool will:
# 1. Extract netflix.apkm
# 2. Find all APK slices inside
# 3. Select arm64-v8a architecture slice
# 4. Select highest density ≤ xhdpi (e.g., if xxhdpi exists, use xhdpi instead)
# 5. Select zh-CN language if available, otherwise en
# 6. Merge selected slices + base APK
# 7. Sign the merged APK
# 8. Output to netflix.apk
```

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

- Platform support (Linux, macOS, Windows)
- GUI interface (web-based or desktop)
- Cloud configuration sharing (public repository of TV profiles)
- Auto-detection from connected Android device via ADB
- Logging and reporting capabilities
- Performance optimization for large APKs
- Support for XAPK format (similar to APKM)
- Integration with package managers or app stores

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
