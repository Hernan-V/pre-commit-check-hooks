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

### `validate-schema`
Validates database schema files for compliance with RDBMS dialects (BigQuery, etc.).
- **Purpose**: Ensures schema files meet dialect requirements and naming conventions
- **Action**: Validates JSON schema files against BigQuery standards
- **Features**:
  - Multi-dialect support (BigQuery with extensibility for PostgreSQL, Hive, SQL Server)
  - 9 naming conventions (snake_case, camelCase, PascalCase, UPPER_CASE, kebab-case, Train-Case, flatcase, COBOL-CASE, Title Case)
  - Lint mode (check only) and fix mode (auto-correct naming)
  - File discovery with regex patterns
  - Nested RECORD type validation
- **Fix**: Manually correct reported schema violations or use `--mode=fix` for naming corrections

### `setup-configs`
Downloads shared configuration files from remote repositories to a local cache directory.
- **Purpose**: Provides centralized configuration management for tools like SQLFluff and isort
- **Action**: Downloads configuration files to cache directory
- **Configuration**: Uses environment variables from `.envrc` file
- **Benefits**: Keeps project workspace clean by storing files in cache directory

## Installation

### Option 1: Use in your .pre-commit-config.yaml

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Hernan-V/pre-commit-check-hooks
    rev: v1.0.11  # Use the latest version
    hooks:
      - id: setup-configs  # Download shared config files first
      - id: check-trailing-whitespace
      - id: check-end-of-file
      - id: check-mixed-line-ending
      - id: check-byte-order-marker
      - id: validate-schema
        args:
          - --file-type=json
          - --path-regex=(schema|bq)/.*
          - --dialect=bigquery
          - --case=snake
          - --mode=lint
```

### Option 2: Selective Usage

Choose only the hooks you need:

```yaml
repos:
  - repo: https://github.com/Hernan-V/pre-commit-check-hooks
    rev: v1.0.11
    hooks:
      - id: setup-configs  # If you need shared config files
      - id: check-trailing-whitespace
      - id: check-end-of-file
      # Schema validation for BigQuery projects
      - id: validate-schema
        files: '\.json$'
        args: ['--dialect', 'bigquery', '--case', 'snake']
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
   
   # Run specific hook
   pre-commit run validate-schema --all-files
   
   # Test schema validation directly
   python hooks/validate_schema.py --dialect bigquery --case snake schema/*.json
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

Validate Database Schema (BigQuery)................................Failed
- hook id: validate-schema
- exit code: 1

schema/customer_table.json: Field customer_table.json.CustomerID: Field name 'CustomerID' does not follow snake_case. Expected: customer_id
schema/orders.json: Field orders.json.emailAddress: Field name 'emailAddress' does not follow snake_case. Expected: email_address
schema/orders.json: Field orders.json.orderDate: Missing required attribute 'mode'
```

## Philosophy

These hooks follow a "check-only" philosophy:

- **Educational**: Developers see exactly what needs to be fixed
- **Non-intrusive**: No automatic modifications to your code
- **Transparent**: Clear reporting of issues with line numbers
- **Consistent**: Same behavior across all environments

## Schema Validation Details

### Supported Dialects
- **BigQuery** (current): Validates against BigQuery table schema standards
- **PostgreSQL** (planned): Coming in future versions
- **Hive** (planned): Coming in future versions
- **SQL Server** (planned): Coming in future versions

### Naming Conventions
Choose from 9 different naming styles using the `--case` argument:
- `snake` (default): `customer_id`
- `camel`: `customerId`
- `pascal`: `CustomerId`
- `upper`: `CUSTOMER_ID`
- `kebab`: `customer-id`
- `train`: `Customer-Id`
- `flat`: `customerid`
- `cobol`: `CUSTOMER-ID`
- `title`: `Customer Id`

### CLI Usage
```bash
# Basic validation
python hooks/validate_schema.py schema/*.json

# With specific options
python hooks/validate_schema.py \
  --dialect bigquery \
  --case snake \
  --mode lint \
  --file-type json \
  --path-regex "schema/.*" \
  schema/*.json

# Auto-fix naming conventions
python hooks/validate_schema.py --mode fix --case snake schema/*.json
```

## Configuration

### Environment Variables (Optional)

The hooks use default configuration values and work out-of-the-box. You can optionally customize behavior by setting environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `PRE_COMMIT_HOOK_CACHE_DIRECTORY` | `.git/.pre-commit-config-cache` | Directory where downloaded configuration files are cached |
| `PRE_COMMIT_HOOK_DOWNLOAD_BASE_URL` | `https://raw.githubusercontent.com/Hernan-V/pre-commit-check-hooks/main` | Base URL for downloading shared configuration files |

#### Customization Examples

**Shell Environment:**
```bash
export PRE_COMMIT_HOOK_CACHE_DIRECTORY=".git/.my-custom-cache"
export PRE_COMMIT_HOOK_DOWNLOAD_BASE_URL="https://raw.githubusercontent.com/your-org/configs/main"
```

**CI/CD Systems:**
Set these as environment variables in your CI/CD pipeline configuration.

## Version Management

The package version is managed through a `VERSION` file in the repository root. This approach provides:
- **Single source of truth**: Version is defined in one place (`VERSION` file)
- **Easy automation**: Scripts and CI/CD can easily read and update the version
- **Python integration**: The version is accessible via `hooks.__version__`

```bash
# Check current version
cat VERSION

# Update version (for maintainers)
echo "1.0.12" > VERSION
```

## Requirements

- **System**: Unix-like systems (Linux, macOS)
- **Dependencies**: Standard Unix tools (`grep`, `tail`, `file`) + Python 3.7+
- **Python Packages**: `case-converter` (for schema validation)
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
