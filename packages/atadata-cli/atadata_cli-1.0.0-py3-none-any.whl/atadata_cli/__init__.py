"""
AtaData CLI Package

A comprehensive command-line interface for managing your AtaData Job Scheduler Backend API.

This package provides full access to all backend operations including:
- Job management (CRUD operations, enable/disable, trigger)
- Settings management (data source configuration, migrations)
- Secret management (validation, generation, encryption status)
- System health monitoring
- Authentication management

Usage:
    atadata --help
    atadata jobs list
    atadata jobs create --id "my-job" --title "My Job" --cron "0 2 * * *"
"""

__version__ = "1.0.0"
__author__ = "AtaData Team"
__email__ = "support@atadata.com"

from .cli import main

__all__ = ["main"]
