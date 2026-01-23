# APKM-Repackager - Claude Development Guide

## Project Overview

APKM-Repackager is a tool for repackaging Android APK files. This project enables modification, analysis, and repackaging of Android application packages.

## Project Purpose

This tool is designed for:
- Legitimate APK modification and customization
- Security research and analysis
- Authorized penetration testing
- Educational purposes
- CTF challenges
- Development and testing workflows

**Important**: This tool should only be used with proper authorization and for legitimate purposes.

## Project Structure

```
APKM-Repackager/
├── README.md           # Project documentation
├── CLAUDE.MD          # This file - Claude development guide
└── .git/              # Git repository
```

## Technology Stack

To be determined based on project development. Likely technologies:
- Python for scripting and automation
- Java/Kotlin for Android-specific operations
- Bash scripts for system operations
- APKTool or similar for APK decompilation/recompilation
- Android SDK tools

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
- Test with various APK types and sizes
- Verify repackaged APKs function correctly
- Test error handling and edge cases
- Document test cases and results

## Key Features (Planned)

- [ ] APK decompilation
- [ ] Resource modification
- [ ] Code modification support
- [ ] APK recompilation
- [ ] Signing repackaged APKs
- [ ] Batch processing support
- [ ] Configuration management

## Dependencies

Document dependencies as they are added:
- APKTool or similar decompilation tools
- Java/Android SDK
- Python packages (if applicable)
- System utilities

## Usage Patterns

### For Claude

When working on this project:
1. Always validate that operations are for authorized purposes
2. Check file paths and permissions before operations
3. Test changes with sample APK files
4. Document any new features or modifications
5. Update this CLAUDE.MD file as the project evolves

### Command Patterns

Document common command patterns here as the project develops:
```bash
# Example patterns (to be updated)
# ./repackage.py input.apk output.apk
# ./analyze.py input.apk
```

## Important Notes

- This is a security-sensitive tool - always prioritize safe operations
- Maintain clear documentation of capabilities and limitations
- Keep track of Android version compatibility
- Document any third-party tool dependencies

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

- [Android Developer Documentation](https://developer.android.com/)
- [APKTool Documentation](https://ibotpeaches.github.io/Apktool/)
- [Android Security Guidelines](https://source.android.com/security)

---

**Last Updated**: 2026-01-23
**Project Status**: Initial Setup

Keep this file updated as the project evolves to help Claude understand the codebase and development practices.
