#!/usr/bin/env python3
"""
CLI tool for managing the Job Scheduler Backend API.

This tool provides a command-line interface for all backend operations including:
- Job management (CRUD operations, enable/disable, trigger)
- Settings management (data source configuration, migrations)
- Secret management (validation, generation, encryption status)
- System health monitoring

Usage:
    atadata [command] [options]
"""

import argparse
import json
import sys
import os
from typing import Dict, Any, Optional, List
import requests
from datetime import datetime
import getpass
import base64
from urllib.parse import urljoin
from dotenv import load_dotenv

# Configuration
DEFAULT_BASE_URL = "http://localhost:8000"
CONFIG_FILE = os.path.expanduser("~/.atadata_cli_config.json")

class AtaDataCLI:
    """Main CLI application class."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self.base_url = DEFAULT_BASE_URL
        self.config = self.load_config()
        self.session = requests.Session()
        self.setup_session()
    
    def load_config(self) -> Dict[str, Any]:
        """Load CLI configuration from file."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"base_url": DEFAULT_BASE_URL, "auth": None}
    
    def save_config(self):
        """Save CLI configuration to file."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config: {e}")
    
    def setup_session(self):
        """Setup HTTP session with authentication if configured."""
        # Check for base URL in environment variable first
        env_base_url = os.getenv("ATADATA_BASE_URL")
        if env_base_url:
            self.base_url = env_base_url
        else:
            self.base_url = self.config.get("base_url", DEFAULT_BASE_URL)
        
        # Check for API key in environment variable first (from .env file)
        env_api_key = os.getenv("ATADATA_API_KEY") or os.getenv("API_KEY_ATADATA")
        if env_api_key:
            self.session.headers.update({"Authorization": f"Bearer {env_api_key}"})
            return
        
        # Add basic auth if configured
        auth = self.config.get("auth")
        if auth and auth.get("type") == "basic":
            username = auth.get("username")
            password = auth.get("password")
            if username and password:
                self.session.auth = (username, password)
        
        # Add API key if configured
        elif auth and auth.get("type") == "api_key":
            api_key = auth.get("api_key")
            if api_key:
                self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the API."""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle different content types
            content_type = response.headers.get('content-type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                return {"message": response.text}
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Error: Could not connect to {self.base_url}")
            print("Make sure the backend server is running.")
            sys.exit(1)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("❌ Error: Authentication failed")
                print("Run 'atadata auth login' to authenticate")
                sys.exit(1)
            else:
                print(f"❌ HTTP Error {e.response.status_code}: {e.response.text}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def print_json(self, data: Dict[str, Any], indent: int = 2):
        """Print data as formatted JSON."""
        print(json.dumps(data, indent=indent, default=str))
    
    def print_table(self, headers: List[str], rows: List[List[str]]):
        """Print data in table format."""
        if not rows:
            print("No data to display")
            return
        
        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                if i < len(widths):
                    widths[i] = max(widths[i], len(str(cell)))
        
        # Print header
        header_row = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
        print(header_row)
        print("-" * len(header_row))
        
        # Print rows
        for row in rows:
            row_str = " | ".join(str(cell).ljust(w) for cell, w in zip(row, widths))
            print(row_str)

    # Authentication commands
    def cmd_auth_login(self, args):
        """Login to the backend API."""
        print("🔐 Backend Authentication")
        print("=" * 30)
        
        auth_type = input("Authentication type (api_key) [api_key]: ").strip() or "api_key"
        
        if auth_type == "api_key":
            api_key = getpass.getpass("API Key: ")
            
            self.config["auth"] = {
                "type": "api_key",
                "api_key": api_key
            }
        
        else:
            print("❌ Only API key authentication is supported")
            return
        
        # Test the authentication
        try:
            self.setup_session()
            response = self.make_request("POST", "/atadata/cli", json={"command": "health", "args": []})
            print("✅ Authentication successful!")
            self.save_config()
        except SystemExit:
            print("❌ Authentication failed")
            self.config["auth"] = None
    
    def cmd_auth_logout(self, args):
        """Logout from the backend API."""
        self.config["auth"] = None
        self.save_config()
        print("✅ Logged out successfully")
    
    def cmd_auth_status(self, args):
        """Show authentication status."""
        # Check environment variable first (from .env file)
        env_api_key = os.getenv("ATADATA_API_KEY") or os.getenv("API_KEY_ATADATA")
        if env_api_key:
            print("✅ Authenticated with API key from environment variable (ATADATA_API_KEY or API_KEY_ATADATA)")
            # Test the API key
            try:
                response = self.make_request("POST", "/atadata/cli", json={"command": "health", "args": []})
                print(f"✅ API key is valid: {response.get('message', '')}")
            except SystemExit:
                print("❌ API key is invalid or expired")
            return
        
        # Fallback to config file
        auth = self.config.get("auth")
        if auth:
            auth_type = auth.get("type", "unknown")
            if auth_type == "api_key":
                print("✅ Authenticated with API key from config file")
                # Test the API key
                try:
                    response = self.make_request("POST", "/atadata/cli", json={"command": "health", "args": []})
                    print(f"✅ API key is valid: {response.get('message', '')}")
                except SystemExit:
                    print("❌ API key is invalid or expired")
            else:
                print(f"✅ Authenticated ({auth_type})")
        else:
            print("❌ Not authenticated")
            print("Set ATADATA_API_KEY environment variable in .env file or run 'atadata auth login'")
    
    def cmd_auth_create_key(self, args):
        """Create a new API key."""
        try:
            request_data = {
                "name": args.name,
                "expires_days": args.expires_days
            }
            response = self.make_request("POST", "/api/auth/keys", json=request_data)
            
            print(f"✅ API key created successfully!")
            print(f"Name: {response.get('name')}")
            print(f"API Key: {response.get('api_key')}")
            if response.get('expires_at'):
                print(f"Expires: {response.get('expires_at')}")
            print("\n⚠️  IMPORTANT: Save this API key securely! It won't be shown again.")
            
        except SystemExit:
            print("❌ Failed to create API key")
    
    def cmd_auth_list_keys(self, args):
        """List all API keys."""
        try:
            response = self.make_request("GET", "/api/auth/keys")
            keys = response.get("keys", {})
            
            if not keys:
                print("No API keys found")
                return
            
            headers = ["Key ID", "Name", "Created", "Last Used", "Usage Count", "Status"]
            rows = []
            
            for key_id, key_info in keys.items():
                status = "✅ Active" if key_info.get("active", True) else "❌ Revoked"
                last_used = key_info.get("last_used", "Never")
                if last_used != "Never":
                    try:
                        from datetime import datetime
                        last_used = datetime.fromisoformat(last_used.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                    except:
                        pass
                
                rows.append([
                    key_id,
                    key_info.get("name", ""),
                    key_info.get("created_at", "")[:10],  # Just the date
                    last_used,
                    str(key_info.get("usage_count", 0)),
                    status
                ])
            
            self.print_table(headers, rows)
            
        except SystemExit:
            print("❌ Failed to list API keys")
    
    def cmd_auth_revoke_key(self, args):
        """Revoke an API key."""
        try:
            response = self.make_request("POST", f"/api/auth/keys/{args.api_key}/revoke")
            print(f"✅ {response.get('message', 'API key revoked successfully')}")
            
        except SystemExit:
            print("❌ Failed to revoke API key")
    
    def cmd_config_set(self, args):
        """Set configuration values."""
        if args.key == "base_url":
            self.config["base_url"] = args.value
            self.base_url = args.value
            self.save_config()
            print(f"✅ Set base_url to {args.value}")
        else:
            print(f"❌ Unknown configuration key: {args.key}")
    
    def cmd_config_get(self, args):
        """Get configuration values."""
        if args.key == "base_url":
            print(self.config.get("base_url", DEFAULT_BASE_URL))
        elif args.key == "auth":
            auth = self.config.get("auth")
            if auth:
                self.print_json(auth)
            else:
                print("Not authenticated")
        else:
            print(f"❌ Unknown configuration key: {args.key}")

    # Health and status commands
    def cmd_health(self, args):
        """Check backend health status."""
        response = self.make_request("GET", "/health")
        self.print_json(response)
    
    def cmd_status(self, args):
        """Get system status."""
        response = self.make_request("GET", "/")
        self.print_json(response)

    # Job management commands
    def cmd_jobs_list(self, args):
        """List all jobs."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["list"]})
        
        if args.json:
            self.print_json(response)
        else:
            jobs = response.get("jobs", [])
            if not jobs:
                print("No jobs found")
                return
            
            headers = ["ID", "Title", "Enabled", "Cron", "Last Execution", "Total Runs", "Status"]
            rows = []
            
            for job in jobs:
                stats = job.get("stats", {})
                last_exec = stats.get("last_execution")
                if last_exec:
                    last_exec = datetime.fromisoformat(last_exec.replace('Z', '+00:00')).strftime("%Y-%m-%d %H:%M")
                else:
                    last_exec = "Never"
                
                status = "🟢 Running" if stats.get("is_running") else "⏸️ Idle"
                if stats.get("consecutive_failures", 0) > 0:
                    status = f"🔴 Failed ({stats['consecutive_failures']})"
                
                rows.append([
                    job.get("id", ""),
                    job.get("title", ""),
                    "✅" if job.get("enabled", False) else "❌",
                    job.get("cron", ""),
                    last_exec,
                    str(stats.get("total_executions", 0)),
                    status
                ])
            
            self.print_table(headers, rows)
            print(f"\nTotal jobs: {response.get('total_jobs', 0)}")
            print(f"Enabled jobs: {response.get('enabled_jobs', 0)}")
    
    def cmd_jobs_get(self, args):
        """Get a specific job."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["get", args.job_id]})
        self.print_json(response)
    
    def cmd_jobs_create(self, args):
        """Create a new job."""
        response = self.make_request("POST", "/atadata/cli", json={
            "command": "jobs", 
            "args": ["create", args.id, args.title, args.description or "", args.cron, args.secrets or ""]
        })
        print(f"✅ {response.get('message', 'Job created successfully')}")
    
    def cmd_jobs_update(self, args):
        """Update an existing job."""
        # Build update commands
        updates = []
        if args.title:
            updates.append(["update", args.job_id, "title", args.title])
        if args.description:
            updates.append(["update", args.job_id, "description", args.description])
        if args.cron:
            updates.append(["update", args.job_id, "cron", args.cron])
        if args.secrets:
            updates.append(["update", args.job_id, "secrets", args.secrets])
        if args.enable:
            updates.append(["enable", args.job_id])
        if args.disable:
            updates.append(["disable", args.job_id])
        
        if not updates:
            print("❌ No fields to update. Specify at least one field to update.")
            return
        
        for update_args in updates:
            response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": update_args})
            print(f"✅ {response.get('message', 'Job updated successfully')}")
    
    def cmd_jobs_delete(self, args):
        """Delete a job."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["delete", args.job_id]})
        print(f"✅ {response.get('message', 'Job deleted successfully')}")
    
    def cmd_jobs_enable(self, args):
        """Enable a job."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["enable", args.job_id]})
        print(f"✅ {response.get('message', 'Job enabled successfully')}")
    
    def cmd_jobs_disable(self, args):
        """Disable a job."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["disable", args.job_id]})
        print(f"✅ {response.get('message', 'Job disabled successfully')}")
    
    def cmd_jobs_trigger(self, args):
        """Manually trigger a job."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "jobs", "args": ["trigger", args.job_id]})
        print(f"✅ {response.get('message', 'Job triggered successfully')}")

    # Settings management commands
    def cmd_settings_get(self, args):
        """Get current settings."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "settings", "args": ["get"]})
        self.print_json(response)
    
    def cmd_settings_data_source(self, args):
        """Update data source configuration."""
        config = {
            "data_source_type": args.type,
        }
        
        if args.type == "json" and args.json_file:
            config["json_file_path"] = args.json_file
        elif args.type == "firebase" and args.collection:
            config["firebase_collection"] = args.collection
        
        response = self.make_request("POST", "/api/settings/data-source", json=config)
        print(f"✅ {response.get('message', 'Data source updated successfully')}")
    
    def cmd_settings_test_connection(self, args):
        """Test data source connection."""
        request_data = {
            "data_source_type": args.type
        }
        
        if args.type == "firebase" and args.collection:
            request_data["firebase_collection"] = args.collection
        
        response = self.make_request("POST", "/api/settings/test-connection", json=request_data)
        print(f"✅ {response.get('message', 'Connection test successful')}")
    
    def cmd_settings_migrate(self, args):
        """Migrate data between data sources."""
        request_data = {
            "from_source": args.from_source,
            "to_source": args.to_source
        }
        
        response = self.make_request("POST", "/api/settings/migrate", json=request_data)
        print(f"✅ {response.get('message', 'Migration completed successfully')}")

    # Secret management commands
    def cmd_secrets_validate(self, args):
        """Validate secret strength."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "secrets", "args": ["validate", args.secret]})
        self.print_json(response)
    
    def cmd_secrets_generate(self, args):
        """Generate a secure secret."""
        response = self.make_request("POST", "/atadata/cli", json={"command": "secrets", "args": ["generate", str(args.length)]})
        
        if args.json:
            self.print_json(response)
        else:
            print(f"Generated secret: {response.get('secret')}")
            print(f"Masked: {response.get('masked')}")
            print(f"Length: {response.get('length')}")
    
    def cmd_secrets_encryption_status(self, args):
        """Check encryption status."""
        print("Encryption status: Not implemented in CLI interface")


def main():
    """Main CLI entry point."""
    cli = AtaDataCLI()
    
    # Main parser
    parser = argparse.ArgumentParser(
        description="AtaData Backend CLI - Manage your job scheduler from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Authentication
  atadata auth login
  atadata auth create-key --name "my-key"
  atadata auth list-keys
  atadata auth status
  
  # Job management
  atadata jobs list
  atadata jobs create --id "backup-job" --title "Daily Backup" --cron "0 2 * * *"
  atadata jobs trigger backup-job
  atadata jobs disable backup-job
  
  # Settings
  atadata settings get
  atadata settings data-source --type firebase --collection jobs
  
  # Secrets
  atadata secrets generate --length 32
  atadata secrets validate --secret "my-secret"
  
  # Health check
  atadata health
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Authentication commands
    auth_parser = subparsers.add_parser('auth', help='Authentication management')
    auth_subparsers = auth_parser.add_subparsers(dest='auth_action')
    
    auth_subparsers.add_parser('login', help='Login to the backend')
    auth_subparsers.add_parser('logout', help='Logout from the backend')
    auth_subparsers.add_parser('status', help='Show authentication status')
    
    # Auth create key
    auth_create_parser = auth_subparsers.add_parser('create-key', help='Create a new API key')
    auth_create_parser.add_argument('--name', required=True, help='Name for the API key')
    auth_create_parser.add_argument('--expires-days', type=int, help='Number of days until expiration')
    
    # Auth list keys
    auth_subparsers.add_parser('list-keys', help='List all API keys')
    
    # Auth revoke key
    auth_revoke_parser = auth_subparsers.add_parser('revoke-key', help='Revoke an API key')
    auth_revoke_parser.add_argument('api_key', help='API key to revoke')
    
    # Configuration commands
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_subparsers = config_parser.add_subparsers(dest='config_action')
    
    config_get_parser = config_subparsers.add_parser('get', help='Get configuration value')
    config_get_parser.add_argument('key', choices=['base_url', 'auth'], help='Configuration key')
    
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', choices=['base_url'], help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    
    # Health and status commands
    subparsers.add_parser('health', help='Check backend health')
    subparsers.add_parser('status', help='Get system status')
    
    # Job management commands
    jobs_parser = subparsers.add_parser('jobs', help='Job management')
    jobs_subparsers = jobs_parser.add_subparsers(dest='jobs_action')
    
    # Jobs list
    jobs_list_parser = jobs_subparsers.add_parser('list', help='List all jobs')
    jobs_list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Jobs get
    jobs_get_parser = jobs_subparsers.add_parser('get', help='Get a specific job')
    jobs_get_parser.add_argument('job_id', help='Job ID')
    
    # Jobs create
    jobs_create_parser = jobs_subparsers.add_parser('create', help='Create a new job')
    jobs_create_parser.add_argument('--id', required=True, help='Job ID')
    jobs_create_parser.add_argument('--title', required=True, help='Job title')
    jobs_create_parser.add_argument('--description', help='Job description')
    jobs_create_parser.add_argument('--cron', required=True, help='Cron expression')
    jobs_create_parser.add_argument('--secrets', help='Job secrets')
    jobs_create_parser.add_argument('--disabled', action='store_true', help='Create job as disabled')
    jobs_create_parser.add_argument('--no-encrypt', action='store_true', help='Do not encrypt secrets')
    
    # Jobs update
    jobs_update_parser = jobs_subparsers.add_parser('update', help='Update an existing job')
    jobs_update_parser.add_argument('job_id', help='Job ID')
    jobs_update_parser.add_argument('--title', help='New job title')
    jobs_update_parser.add_argument('--description', help='New job description')
    jobs_update_parser.add_argument('--cron', help='New cron expression')
    jobs_update_parser.add_argument('--secrets', help='New job secrets')
    jobs_update_parser.add_argument('--enable', action='store_true', help='Enable the job')
    jobs_update_parser.add_argument('--disable', action='store_true', help='Disable the job')
    jobs_update_parser.add_argument('--no-encrypt', action='store_true', help='Do not encrypt secrets')
    
    # Jobs delete
    jobs_delete_parser = jobs_subparsers.add_parser('delete', help='Delete a job')
    jobs_delete_parser.add_argument('job_id', help='Job ID')
    
    # Jobs enable/disable
    jobs_enable_parser = jobs_subparsers.add_parser('enable', help='Enable a job')
    jobs_enable_parser.add_argument('job_id', help='Job ID')
    
    jobs_disable_parser = jobs_subparsers.add_parser('disable', help='Disable a job')
    jobs_disable_parser.add_argument('job_id', help='Job ID')
    
    # Jobs trigger
    jobs_trigger_parser = jobs_subparsers.add_parser('trigger', help='Manually trigger a job')
    jobs_trigger_parser.add_argument('job_id', help='Job ID')
    
    # Settings management commands
    settings_parser = subparsers.add_parser('settings', help='Settings management')
    settings_subparsers = settings_parser.add_subparsers(dest='settings_action')
    
    settings_subparsers.add_parser('get', help='Get current settings')
    
    # Settings data source
    settings_ds_parser = settings_subparsers.add_parser('data-source', help='Update data source configuration')
    settings_ds_parser.add_argument('--type', required=True, choices=['json', 'firebase'], help='Data source type')
    settings_ds_parser.add_argument('--json-file', help='JSON file path (for json type)')
    settings_ds_parser.add_argument('--collection', help='Firebase collection name (for firebase type)')
    
    # Settings test connection
    settings_test_parser = settings_subparsers.add_parser('test-connection', help='Test data source connection')
    settings_test_parser.add_argument('--type', required=True, choices=['json', 'firebase'], help='Data source type')
    settings_test_parser.add_argument('--collection', help='Firebase collection name (for firebase type)')
    
    # Settings migrate
    settings_migrate_parser = settings_subparsers.add_parser('migrate', help='Migrate data between sources')
    settings_migrate_parser.add_argument('--from', dest='from_source', required=True, help='Source data source')
    settings_migrate_parser.add_argument('--to', dest='to_source', required=True, help='Target data source')
    
    # Secret management commands
    secrets_parser = subparsers.add_parser('secrets', help='Secret management')
    secrets_subparsers = secrets_parser.add_subparsers(dest='secrets_action')
    
    # Secrets validate
    secrets_validate_parser = secrets_subparsers.add_parser('validate', help='Validate secret strength')
    secrets_validate_parser.add_argument('--secret', required=True, help='Secret to validate')
    
    # Secrets generate
    secrets_generate_parser = secrets_subparsers.add_parser('generate', help='Generate a secure secret')
    secrets_generate_parser.add_argument('--length', type=int, default=32, help='Secret length (default: 32)')
    secrets_generate_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Secrets encryption status
    secrets_subparsers.add_parser('encryption-status', help='Check encryption status')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate command handler
    try:
        if args.command == 'auth':
            if args.auth_action == 'login':
                cli.cmd_auth_login(args)
            elif args.auth_action == 'logout':
                cli.cmd_auth_logout(args)
            elif args.auth_action == 'status':
                cli.cmd_auth_status(args)
            elif args.auth_action == 'create-key':
                cli.cmd_auth_create_key(args)
            elif args.auth_action == 'list-keys':
                cli.cmd_auth_list_keys(args)
            elif args.auth_action == 'revoke-key':
                cli.cmd_auth_revoke_key(args)
            else:
                auth_parser.print_help()
        
        elif args.command == 'config':
            if args.config_action == 'get':
                cli.cmd_config_get(args)
            elif args.config_action == 'set':
                cli.cmd_config_set(args)
            else:
                config_parser.print_help()
        
        elif args.command == 'health':
            cli.cmd_health(args)
        
        elif args.command == 'status':
            cli.cmd_status(args)
        
        elif args.command == 'jobs':
            if args.jobs_action == 'list':
                cli.cmd_jobs_list(args)
            elif args.jobs_action == 'get':
                cli.cmd_jobs_get(args)
            elif args.jobs_action == 'create':
                cli.cmd_jobs_create(args)
            elif args.jobs_action == 'update':
                cli.cmd_jobs_update(args)
            elif args.jobs_action == 'delete':
                cli.cmd_jobs_delete(args)
            elif args.jobs_action == 'enable':
                cli.cmd_jobs_enable(args)
            elif args.jobs_action == 'disable':
                cli.cmd_jobs_disable(args)
            elif args.jobs_action == 'trigger':
                cli.cmd_jobs_trigger(args)
            else:
                jobs_parser.print_help()
        
        elif args.command == 'settings':
            if args.settings_action == 'get':
                cli.cmd_settings_get(args)
            elif args.settings_action == 'data-source':
                cli.cmd_settings_data_source(args)
            elif args.settings_action == 'test-connection':
                cli.cmd_settings_test_connection(args)
            elif args.settings_action == 'migrate':
                cli.cmd_settings_migrate(args)
            else:
                settings_parser.print_help()
        
        elif args.command == 'secrets':
            if args.secrets_action == 'validate':
                cli.cmd_secrets_validate(args)
            elif args.secrets_action == 'generate':
                cli.cmd_secrets_generate(args)
            elif args.secrets_action == 'encryption-status':
                cli.cmd_secrets_encryption_status(args)
            else:
                secrets_parser.print_help()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
