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
│   └── signer.py        # APK signing utilities
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

- [ ] APKM file extraction (unzip/decompress)
- [ ] Parse and analyze APK slices within APKM
- [ ] Detect device architecture and requirements
- [ ] Select appropriate slices (architecture, density, language)
- [ ] Merge selected APK slices into single APK
- [ ] Sign the merged APK for installation
- [ ] Validate merged APK integrity
- [ ] Support for multiple architectures (arm, arm64, x86, x86_64)
- [ ] Support for different screen densities (hdpi, xhdpi, xxhdpi, etc.)
- [ ] CLI interface for easy usage
- [ ] Batch processing support

## Dependencies

Required dependencies:
- **Python 3.7+** - Main runtime environment
- **Android SDK Build Tools** - For apksigner and other tools
- **Java/JDK** - Required by Android SDK tools

Python packages (to be added to requirements.txt):
- `androguard` or `pyaxmlparser` - For parsing AndroidManifest.xml from APK files
- Standard library modules: `zipfile`, `argparse`, `pathlib`, `json`

Optional:
- `apktool` - For deeper APK analysis if needed

## Usage Patterns

### For Claude

When working on this project:
1. Always validate that operations are for authorized purposes
2. Check file paths and permissions before operations
3. Test changes with sample APK files
4. Document any new features or modifications
5. Update this CLAUDE.MD file as the project evolves

### Command Patterns

Expected usage patterns:
```bash
# Basic usage - convert APKM to APK
python apkm_repackager.py input.apkm -o output.apk

# Specify target architecture
python apkm_repackager.py input.apkm -o output.apk --arch arm64-v8a

# Specify screen density
python apkm_repackager.py input.apkm -o output.apk --density xhdpi

# List available slices in APKM
python apkm_repackager.py input.apkm --list

# Auto-detect from device (future feature)
python apkm_repackager.py input.apkm -o output.apk --auto-detect
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

### Key Challenges
- Correctly identifying which slices are mandatory vs optional
- Properly merging manifests from multiple APKs
- Maintaining valid APK signature after merging
- Handling different APKM formats from various sources

## Git Workflow

- Default branch: main
- Feature branches: Use descriptive names
- Commit messages: Clear and descriptive
- Always test before committing changes

## Future Considerations

- Platform support (Linux, macOS, Windows)
- GUI vs CLI interface
- Configuration file format
- Logging and reporting capabilities
- Performance optimization for large APKs

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
