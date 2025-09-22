#!/usr/bin/env python3
"""
Sample script to test all AtaData CLI functions.

This script demonstrates how to use the AtaData CLI programmatically
and can be used to verify that all functions are working correctly.

Usage:
    python sample_script.py [--base-url URL] [--api-key KEY] [--dry-run]
"""

import argparse
import os
import sys
import time
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Add the package to the path so we can import it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from atadata_cli.cli import AtaDataCLI


class SampleScript:
    """Sample script to test all CLI functions."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, dry_run: bool = False):
        # Load environment variables from .env file
        load_dotenv()
        
        self.base_url = base_url
        self.api_key = api_key
        self.dry_run = dry_run
        self.cli = AtaDataCLI()
        
        # Override CLI configuration
        self.cli.config["base_url"] = base_url
        if api_key:
            self.cli.config["auth"] = {
                "type": "api_key",
                "api_key": api_key
            }
        self.cli.setup_session()
        
        # Test job ID for demonstration
        self.test_job_id = "sample-test-job"
        
    def print_section(self, title: str):
        """Print a section header."""
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    
    def print_result(self, operation: str, success: bool, details: str = ""):
        """Print operation result."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        print(f"{status}: {operation}")
        if details:
            print(f"    Details: {details}")
    
    def test_authentication(self):
        """Test authentication functions."""
        self.print_section("AUTHENTICATION TESTS")
        
        # Test auth status
        try:
            print("Testing authentication status...")
            if not self.dry_run:
                self.cli.cmd_auth_status(None)
            self.print_result("Authentication status check", True)
        except Exception as e:
            self.print_result("Authentication status check", False, str(e))
        
        # Test auth create key (if not dry run)
        if not self.dry_run:
            try:
                print("Testing API key creation...")
                # Create a mock args object
                class MockArgs:
                    name = "sample-script-key"
                    expires_days = 1
                
                self.cli.cmd_auth_create_key(MockArgs())
                self.print_result("API key creation", True)
            except Exception as e:
                self.print_result("API key creation", False, str(e))
        
        # Test auth list keys
        try:
            print("Testing API key listing...")
            if not self.dry_run:
                self.cli.cmd_auth_list_keys(None)
            self.print_result("API key listing", True)
        except Exception as e:
            self.print_result("API key listing", False, str(e))
    
    def test_health_and_status(self):
        """Test health and status functions."""
        self.print_section("HEALTH & STATUS TESTS")
        
        # Test health check
        try:
            print("Testing health check...")
            if not self.dry_run:
                self.cli.cmd_health(None)
            self.print_result("Health check", True)
        except Exception as e:
            self.print_result("Health check", False, str(e))
        
        # Test status check
        try:
            print("Testing status check...")
            if not self.dry_run:
                self.cli.cmd_status(None)
            self.print_result("Status check", True)
        except Exception as e:
            self.print_result("Status check", False, str(e))
    
    def test_job_management(self):
        """Test job management functions."""
        self.print_section("JOB MANAGEMENT TESTS")
        
        # Test jobs list
        try:
            print("Testing jobs list...")
            if not self.dry_run:
                class MockArgs:
                    json = False
                self.cli.cmd_jobs_list(MockArgs())
            self.print_result("Jobs list", True)
        except Exception as e:
            self.print_result("Jobs list", False, str(e))
        
        # Test job creation
        try:
            print("Testing job creation...")
            if not self.dry_run:
                class MockArgs:
                    id = self.test_job_id
                    title = "Sample Test Job"
                    description = "A job created by the sample script"
                    cron = "0 */6 * * *"  # Every 6 hours
                    secrets = "TEST_SECRET=sample_value"
                
                self.cli.cmd_jobs_create(MockArgs())
            self.print_result("Job creation", True)
        except Exception as e:
            self.print_result("Job creation", False, str(e))
        
        # Test job get
        try:
            print("Testing job retrieval...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                self.cli.cmd_jobs_get(MockArgs())
            self.print_result("Job retrieval", True)
        except Exception as e:
            self.print_result("Job retrieval", False, str(e))
        
        # Test job update
        try:
            print("Testing job update...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                    title = "Updated Sample Test Job"
                    description = "An updated job description"
                    cron = None
                    secrets = None
                    enable = False
                    disable = False
                
                self.cli.cmd_jobs_update(MockArgs())
            self.print_result("Job update", True)
        except Exception as e:
            self.print_result("Job update", False, str(e))
        
        # Test job enable
        try:
            print("Testing job enable...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                self.cli.cmd_jobs_enable(MockArgs())
            self.print_result("Job enable", True)
        except Exception as e:
            self.print_result("Job enable", False, str(e))
        
        # Test job trigger
        try:
            print("Testing job trigger...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                self.cli.cmd_jobs_trigger(MockArgs())
            self.print_result("Job trigger", True)
        except Exception as e:
            self.print_result("Job trigger", False, str(e))
        
        # Test job disable
        try:
            print("Testing job disable...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                self.cli.cmd_jobs_disable(MockArgs())
            self.print_result("Job disable", True)
        except Exception as e:
            self.print_result("Job disable", False, str(e))
        
        # Test job deletion
        try:
            print("Testing job deletion...")
            if not self.dry_run:
                class MockArgs:
                    job_id = self.test_job_id
                self.cli.cmd_jobs_delete(MockArgs())
            self.print_result("Job deletion", True)
        except Exception as e:
            self.print_result("Job deletion", False, str(e))
    
    def test_settings_management(self):
        """Test settings management functions."""
        self.print_section("SETTINGS MANAGEMENT TESTS")
        
        # Test settings get
        try:
            print("Testing settings retrieval...")
            if not self.dry_run:
                self.cli.cmd_settings_get(None)
            self.print_result("Settings retrieval", True)
        except Exception as e:
            self.print_result("Settings retrieval", False, str(e))
        
        # Test data source configuration (JSON)
        try:
            print("Testing JSON data source configuration...")
            if not self.dry_run:
                class MockArgs:
                    type = "json"
                    json_file = "/tmp/sample_jobs.json"
                    collection = None
                
                self.cli.cmd_settings_data_source(MockArgs())
            self.print_result("JSON data source configuration", True)
        except Exception as e:
            self.print_result("JSON data source configuration", False, str(e))
        
        # Test data source configuration (Firebase)
        try:
            print("Testing Firebase data source configuration...")
            if not self.dry_run:
                class MockArgs:
                    type = "firebase"
                    json_file = None
                    collection = "sample_jobs"
                
                self.cli.cmd_settings_data_source(MockArgs())
            self.print_result("Firebase data source configuration", True)
        except Exception as e:
            self.print_result("Firebase data source configuration", False, str(e))
        
        # Test connection test
        try:
            print("Testing connection test...")
            if not self.dry_run:
                class MockArgs:
                    type = "json"
                    collection = None
                
                self.cli.cmd_settings_test_connection(MockArgs())
            self.print_result("Connection test", True)
        except Exception as e:
            self.print_result("Connection test", False, str(e))
        
        # Test migration
        try:
            print("Testing data migration...")
            if not self.dry_run:
                class MockArgs:
                    from_source = "json"
                    to_source = "firebase"
                
                self.cli.cmd_settings_migrate(MockArgs())
            self.print_result("Data migration", True)
        except Exception as e:
            self.print_result("Data migration", False, str(e))
    
    def test_secret_management(self):
        """Test secret management functions."""
        self.print_section("SECRET MANAGEMENT TESTS")
        
        # Test secret generation
        try:
            print("Testing secret generation...")
            if not self.dry_run:
                class MockArgs:
                    length = 32
                    json = False
                
                self.cli.cmd_secrets_generate(MockArgs())
            self.print_result("Secret generation", True)
        except Exception as e:
            self.print_result("Secret generation", False, str(e))
        
        # Test secret validation
        try:
            print("Testing secret validation...")
            if not self.dry_run:
                class MockArgs:
                    secret = "SampleSecret123!@#"
                
                self.cli.cmd_secrets_validate(MockArgs())
            self.print_result("Secret validation", True)
        except Exception as e:
            self.print_result("Secret validation", False, str(e))
        
        # Test encryption status
        try:
            print("Testing encryption status...")
            if not self.dry_run:
                self.cli.cmd_secrets_encryption_status(None)
            self.print_result("Encryption status", True)
        except Exception as e:
            self.print_result("Encryption status", False, str(e))
    
    def test_configuration(self):
        """Test configuration functions."""
        self.print_section("CONFIGURATION TESTS")
        
        # Test config get
        try:
            print("Testing configuration retrieval...")
            if not self.dry_run:
                class MockArgs:
                    key = "base_url"
                
                self.cli.cmd_config_get(MockArgs())
            self.print_result("Configuration retrieval", True)
        except Exception as e:
            self.print_result("Configuration retrieval", False, str(e))
        
        # Test config set
        try:
            print("Testing configuration setting...")
            if not self.dry_run:
                class MockArgs:
                    key = "base_url"
                    value = self.base_url
                
                self.cli.cmd_config_set(MockArgs())
            self.print_result("Configuration setting", True)
        except Exception as e:
            self.print_result("Configuration setting", False, str(e))
    
    def run_all_tests(self):
        """Run all tests."""
        print("🚀 Starting AtaData CLI Sample Script")
        print(f"Base URL: {self.base_url}")
        print(f"API Key: {'Set' if self.api_key else 'Not set'}")
        print(f"Dry Run: {self.dry_run}")
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual API calls will be made")
        
        # Run all test suites
        self.test_authentication()
        self.test_health_and_status()
        self.test_job_management()
        self.test_settings_management()
        self.test_secret_management()
        self.test_configuration()
        
        self.print_section("TEST SUMMARY")
        print("✅ All tests completed!")
        print("\nIf you see any failures above, check:")
        print("1. Backend server is running and accessible")
        print("2. API key is valid and has proper permissions")
        print("3. Network connectivity to the backend")
        print("4. Backend API endpoints are working correctly")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Sample script to test all AtaData CLI functions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings
  python sample_script.py
  
  # Run with custom base URL
  python sample_script.py --base-url http://localhost:3000
  
  # Run with API key
  python sample_script.py --api-key your-api-key-here
  
  # Dry run (no actual API calls)
  python sample_script.py --dry-run
  
  # Full example
  python sample_script.py --base-url http://localhost:3000 --api-key your-key --dry-run
        """
    )
    
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL for the AtaData backend API (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--api-key",
        help="API key for authentication (can also be set via API_KEY_ATADATA env var)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no actual API calls)"
    )
    
    args = parser.parse_args()
    
    # Get API key from environment if not provided
    api_key = args.api_key or os.getenv("ATADATA_API_KEY") or os.getenv("API_KEY_ATADATA")
    
    # Create and run the sample script
    script = SampleScript(
        base_url=args.base_url,
        api_key=api_key,
        dry_run=args.dry_run
    )
    
    try:
        script.run_all_tests()
    except KeyboardInterrupt:
        print("\n❌ Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
