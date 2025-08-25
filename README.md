# Pre-commit Check Hooks

A collection of lightweight pre-commit hooks focused on checking code quality without making modifications. These hooks identify issues and require manual fixes, promoting awareness and consistency in code formatting.

## Overview

This repository provides pre-commit hooks that perform **check-only** operations. Unlike hooks that automatically fix issues, these hooks will:
- ✅ Pass silently when no issues are found
- ❌ Fail and report issues when problems are detected
- 🚫 Never modify your files automatically

This approach ensures developers are aware of formatting issues and can address them consciously.

## Available Hooks

### `check-trailing-whitespace`
Detects trailing whitespace at the end of lines.
- **Purpose**: Prevents unnecessary whitespace that can cause diff noise
- **Action**: Reports lines with trailing spaces or tabs
- **Fix**: Manually remove trailing whitespace from reported lines

### `check-end-of-file`
Ensures files end with a newline character.
- **Purpose**: Maintains POSIX compliance and prevents tool issues
- **Action**: Reports files missing final newline
- **Fix**: Add a newline at the end of reported files

### `check-mixed-line-ending`
Detects mixed line endings (CRLF/LF) within files.
- **Purpose**: Prevents line ending inconsistencies across platforms
- **Action**: Reports files with mixed line endings
- **Fix**: Standardize line endings throughout the file

### `check-byte-order-marker`
Identifies files containing Byte Order Markers (BOM).
- **Purpose**: Prevents BOM-related issues in various tools and systems
- **Action**: Reports files with BOM characters
- **Fix**: Remove BOM from the beginning of reported files

## Installation

### Option 1: Use in your .pre-commit-config.yaml

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Hernan-V/pre-commit-check-hooks
    rev: v1.0.0  # Use the latest version
    hooks:
      - id: check-trailing-whitespace
      - id: check-end-of-file
      - id: check-mixed-line-ending
      - id: check-byte-order-marker
```

### Option 2: Selective Usage

Choose only the hooks you need:

```yaml
repos:
  - repo: https://github.com/Hernan-V/pre-commit-check-hooks
    rev: v1.0.0
    hooks:
      - id: check-trailing-whitespace
      - id: check-end-of-file
```

## Usage

1. Install pre-commit if you haven't already:
   ```bash
   pip install pre-commit
   ```

2. Add the hooks to your `.pre-commit-config.yaml` file (see installation section above)

3. Install the hooks:
   ```bash
   pre-commit install
   ```

4. Run the hooks manually (optional):
   ```bash
   pre-commit run --all-files
   ```

5. The hooks will now run automatically on every commit

## Example Output

When issues are found, you'll see output like:

```
Check for trailing whitespace (check only)........................Failed
- hook id: check-trailing-whitespace
- exit code: 1

src/example.py:15:    def function():     
src/example.py:23:        return True    
Trailing whitespace found!

Check for end-of-file newline (check only)..........................Failed
- hook id: check-end-of-file
- exit code: 1

Missing EOF newline!
```

## Philosophy

These hooks follow a "check-only" philosophy:

- **Educational**: Developers see exactly what needs to be fixed
- **Non-intrusive**: No automatic modifications to your code
- **Transparent**: Clear reporting of issues with line numbers
- **Consistent**: Same behavior across all environments

## Requirements

- **System**: Unix-like systems (Linux, macOS)
- **Dependencies**: Standard Unix tools (`grep`, `tail`, `file`)
- **Pre-commit**: Version 0.15.0 or higher

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new hooks
4. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

**Hernan Valenzuela** - [@Hernan-V](https://github.com/Hernan-V)

---

*Part of the effort to maintain high-quality, consistent codebases across development teams.*
