# AtaData CLI

A comprehensive command-line interface for managing your AtaData Job Scheduler Backend API.

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PyPI](https://img.shields.io/pypi/v/atadata-cli.svg)](https://pypi.org/project/atadata-cli/)

## Features

This CLI tool provides full access to all backend operations including:

- **Job Management**: CRUD operations, enable/disable, manual triggering
- **Settings Management**: Data source configuration, migrations
- **Secret Management**: Validation, generation, encryption status
- **System Health Monitoring**: Health checks and status monitoring
- **Authentication Management**: API key management and authentication

## Installation

### From PyPI (Recommended)

```bash
pip install atadata-cli
```

### From Source

```bash
git clone https://github.com/atadata/atadata-cli.git
cd atadata-cli
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/atadata/atadata-cli.git
cd atadata-cli
pip install -e ".[dev]"
```

## Quick Start

### 1. Authentication

First, authenticate with your AtaData backend:

```bash
# Option 1: Use .env file (recommended)
cp env.example .env
# Edit .env file and add your API key:
# ATADATA_API_KEY=your-api-key-here
# ATADATA_BASE_URL=http://localhost:8000

# Option 2: Login interactively
atadata auth login

# Option 3: Set environment variable directly
export ATADATA_API_KEY="your-api-key-here"

# Check authentication status
atadata auth status
```

### 2. Basic Usage

```bash
# Check backend health
atadata health

# List all jobs
atadata jobs list

# Create a new job
atadata jobs create --id "backup-job" --title "Daily Backup" --cron "0 2 * * *"

# Trigger a job manually
atadata jobs trigger backup-job

# Disable a job
atadata jobs disable backup-job
```

## Commands Reference

### Authentication Commands

```bash
# Login to the backend
atadata auth login

# Logout from the backend
atadata auth logout

# Show authentication status
atadata auth status

# Create a new API key
atadata auth create-key --name "my-key" --expires-days 30

# List all API keys
atadata auth list-keys

# Revoke an API key
atadata auth revoke-key <api-key-id>
```

### Job Management Commands

```bash
# List all jobs
atadata jobs list [--json]

# Get a specific job
atadata jobs get <job-id>

# Create a new job
atadata jobs create --id <job-id> --title <title> --cron <cron-expression> [--description <desc>] [--secrets <secrets>]

# Update an existing job
atadata jobs update <job-id> [--title <title>] [--description <desc>] [--cron <cron>] [--secrets <secrets>] [--enable] [--disable]

# Delete a job
atadata jobs delete <job-id>

# Enable a job
atadata jobs enable <job-id>

# Disable a job
atadata jobs disable <job-id>

# Manually trigger a job
atadata jobs trigger <job-id>
```

### Settings Management Commands

```bash
# Get current settings
atadata settings get

# Update data source configuration
atadata settings data-source --type <json|firebase> [--json-file <path>] [--collection <name>]

# Test data source connection
atadata settings test-connection --type <json|firebase> [--collection <name>]

# Migrate data between sources
atadata settings migrate --from <source> --to <target>
```

### Secret Management Commands

```bash
# Validate secret strength
atadata secrets validate --secret <secret>

# Generate a secure secret
atadata secrets generate [--length <length>] [--json]

# Check encryption status
atadata secrets encryption-status
```

### System Commands

```bash
# Check backend health
atadata health

# Get system status
atadata status

# Configuration management
atadata config get <key>
atadata config set <key> <value>
```

## Configuration

The CLI supports multiple configuration methods (in order of priority):

### 1. Environment Variables (Recommended)
Create a `.env` file in your project directory:

```bash
# Copy the example file
cp env.example .env

# Edit .env with your values
ATADATA_API_KEY=your-api-key-here
ATADATA_BASE_URL=http://localhost:8000
```

### 2. System Environment Variables
```bash
export ATADATA_API_KEY="your-api-key-here"
export ATADATA_BASE_URL="http://localhost:8000"
```

### 3. Config File
The CLI also stores configuration in `~/.atadata_cli_config.json` for interactive login sessions.

### Environment Variables
- `ATADATA_API_KEY`: Your API key for authentication (primary)
- `API_KEY_ATADATA`: Alternative API key variable name (backward compatibility)
- `ATADATA_BASE_URL`: Base URL for the backend API (default: http://localhost:8000)

## Examples

### Complete Workflow Example

```bash
# 1. Set up environment
cp env.example .env
# Edit .env with your API key and base URL

# 2. Authenticate (or use .env file)
atadata auth status

# 3. Check system health
atadata health

# 4. Create a backup job
atadata jobs create \
  --id "daily-backup" \
  --title "Daily Database Backup" \
  --description "Automated daily backup of the database" \
  --cron "0 2 * * *" \
  --secrets "BACKUP_PASSWORD=secret123"

# 5. List jobs to verify
atadata jobs list

# 6. Test the job manually
atadata jobs trigger daily-backup

# 7. Update job settings
atadata jobs update daily-backup --cron "0 3 * * *"

# 8. Disable the job
atadata jobs disable daily-backup
```

### Batch Operations

```bash
# Create multiple jobs from a script
for i in {1..5}; do
  atadata jobs create \
    --id "job-$i" \
    --title "Test Job $i" \
    --cron "0 */6 * * *"
done

# List all jobs
atadata jobs list

# Disable all jobs
atadata jobs list --json | jq -r '.jobs[].id' | xargs -I {} atadata jobs disable {}
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=atadata_cli

# Run specific test
pytest tests/test_cli.py::test_auth_login
```

### Code Quality

```bash
# Format code
black atadata_cli/ tests/

# Lint code
flake8 atadata_cli/ tests/

# Type checking
mypy atadata_cli/
```

### Building the Package

```bash
# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Build both
python setup.py sdist bdist_wheel
```

## Sample Script

A sample script is included to test all CLI functions. Run it to verify your installation:

```bash
python sample_script.py
```

This script will test:
- Authentication
- Health checks
- Job management operations
- Settings management
- Secret management

## Troubleshooting

### Common Issues

1. **Connection Error**: Make sure the backend server is running and accessible
2. **Authentication Failed**: Verify your API key is correct and not expired
3. **Permission Denied**: Check that your API key has the necessary permissions

### Debug Mode

Enable debug output by setting the environment variable:

```bash
export ATADATA_DEBUG=1
atadata jobs list
```

### Logs

The CLI logs important operations. Check the logs for detailed error information.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [GitHub Wiki](https://github.com/atadata/atadata-cli/wiki)
- **Issues**: [GitHub Issues](https://github.com/atadata/atadata-cli/issues)
- **Email**: support@atadata.com

## Changelog

### Version 1.0.0
- Initial release
- Full job management functionality
- Authentication system
- Settings and secret management
- Health monitoring
- Comprehensive CLI interface
