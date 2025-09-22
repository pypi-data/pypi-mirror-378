"""
Tests for the AtaData CLI module.
"""

import pytest
import json
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from atadata_cli.cli import AtaDataCLI


class TestAtaDataCLI:
    """Test cases for AtaDataCLI class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = AtaDataCLI()
        self.cli.config = {"base_url": "http://localhost:8000", "auth": None}
    
    def test_init(self):
        """Test CLI initialization."""
        cli = AtaDataCLI()
        assert cli.base_url == "http://localhost:8000"
        assert cli.config is not None
        assert cli.session is not None
    
    def test_load_config_file_exists(self):
        """Test loading config from existing file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_data = {"base_url": "http://test:9000", "auth": {"type": "api_key", "api_key": "test-key"}}
            json.dump(config_data, f)
            temp_file = f.name
        
        try:
            with patch('atadata_cli.cli.CONFIG_FILE', temp_file):
                cli = AtaDataCLI()
                assert cli.config["base_url"] == "http://test:9000"
                assert cli.config["auth"]["api_key"] == "test-key"
        finally:
            os.unlink(temp_file)
    
    def test_load_config_file_not_exists(self):
        """Test loading config when file doesn't exist."""
        with patch('atadata_cli.cli.CONFIG_FILE', '/nonexistent/path/config.json'):
            cli = AtaDataCLI()
            assert cli.config["base_url"] == "http://localhost:8000"
            assert cli.config["auth"] is None
    
    def test_load_config_invalid_json(self):
        """Test loading config with invalid JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name
        
        try:
            with patch('atadata_cli.cli.CONFIG_FILE', temp_file):
                cli = AtaDataCLI()
                assert cli.config["base_url"] == "http://localhost:8000"
                assert cli.config["auth"] is None
        finally:
            os.unlink(temp_file)
    
    def test_save_config(self):
        """Test saving config to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, 'test_config.json')
            
            with patch('atadata_cli.cli.CONFIG_FILE', config_file):
                cli = AtaDataCLI()
                cli.config["test_key"] = "test_value"
                cli.save_config()
                
                assert os.path.exists(config_file)
                with open(config_file, 'r') as f:
                    saved_config = json.load(f)
                assert saved_config["test_key"] == "test_value"
    
    @patch('atadata_cli.cli.load_dotenv')
    def test_setup_session_with_api_key(self, mock_load_dotenv):
        """Test session setup with API key."""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
            cli = AtaDataCLI()
            cli.config["auth"] = {"type": "api_key", "api_key": "test-key"}
            cli.setup_session()
            
            assert "Authorization" in cli.session.headers
            assert cli.session.headers["Authorization"] == "Bearer test-key"
    
    def test_setup_session_with_env_api_key(self):
        """Test session setup with environment API key."""
        with patch.dict(os.environ, {"ATADATA_API_KEY": "env-test-key"}):
            cli = AtaDataCLI()
            cli.setup_session()
            
            assert "Authorization" in cli.session.headers
            assert cli.session.headers["Authorization"] == "Bearer env-test-key"
    
    @patch('atadata_cli.cli.load_dotenv')
    def test_setup_session_with_basic_auth(self, mock_load_dotenv):
        """Test session setup with basic auth."""
        with patch.dict(os.environ, {}, clear=True):  # Clear environment variables
            cli = AtaDataCLI()
            cli.config["auth"] = {"type": "basic", "username": "user", "password": "pass"}
            cli.setup_session()
            
            assert cli.session.auth == ("user", "pass")
    
    @patch('atadata_cli.cli.requests.Session.request')
    def test_make_request_success(self, mock_request):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {"status": "success"}
        mock_response.raise_for_status.return_value = None
        mock_request.return_value = mock_response
        
        cli = AtaDataCLI()
        result = cli.make_request("GET", "/test")
        
        assert result == {"status": "success"}
        mock_request.assert_called_once()
    
    @patch('atadata_cli.cli.requests.Session.request')
    def test_make_request_connection_error(self, mock_request):
        """Test API request with connection error."""
        from requests.exceptions import ConnectionError
        mock_request.side_effect = ConnectionError()
        
        cli = AtaDataCLI()
        
        with pytest.raises(SystemExit):
            cli.make_request("GET", "/test")
    
    @patch('atadata_cli.cli.requests.Session.request')
    def test_make_request_http_error_401(self, mock_request):
        """Test API request with 401 HTTP error."""
        from requests.exceptions import HTTPError
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_request.side_effect = HTTPError(response=mock_response)
        
        cli = AtaDataCLI()
        
        with pytest.raises(SystemExit):
            cli.make_request("GET", "/test")
    
    def test_print_json(self, capsys):
        """Test JSON printing."""
        cli = AtaDataCLI()
        test_data = {"key": "value", "number": 123}
        
        cli.print_json(test_data)
        captured = capsys.readouterr()
        
        assert "key" in captured.out
        assert "value" in captured.out
        assert "123" in captured.out
    
    def test_print_table(self, capsys):
        """Test table printing."""
        cli = AtaDataCLI()
        headers = ["Name", "Age", "City"]
        rows = [
            ["John", "25", "New York"],
            ["Jane", "30", "Los Angeles"]
        ]
        
        cli.print_table(headers, rows)
        captured = capsys.readouterr()
        
        assert "Name" in captured.out
        assert "John" in captured.out
        assert "Jane" in captured.out
    
    def test_print_table_empty(self, capsys):
        """Test table printing with empty data."""
        cli = AtaDataCLI()
        headers = ["Name", "Age"]
        rows = []
        
        cli.print_table(headers, rows)
        captured = capsys.readouterr()
        
        assert "No data to display" in captured.out


class TestCLICommands:
    """Test cases for CLI command methods."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cli = AtaDataCLI()
        self.cli.config = {"base_url": "http://localhost:8000", "auth": None}
    
    @patch.object(AtaDataCLI, 'make_request')
    def test_cmd_health(self, mock_make_request):
        """Test health command."""
        mock_make_request.return_value = {"status": "healthy"}
        
        with patch.object(self.cli, 'print_json') as mock_print:
            self.cli.cmd_health(None)
            mock_make_request.assert_called_once_with("GET", "/health")
            mock_print.assert_called_once_with({"status": "healthy"})
    
    @patch.object(AtaDataCLI, 'make_request')
    def test_cmd_status(self, mock_make_request):
        """Test status command."""
        mock_make_request.return_value = {"version": "1.0.0"}
        
        with patch.object(self.cli, 'print_json') as mock_print:
            self.cli.cmd_status(None)
            mock_make_request.assert_called_once_with("GET", "/")
            mock_print.assert_called_once_with({"version": "1.0.0"})
    
    @patch.object(AtaDataCLI, 'make_request')
    def test_cmd_jobs_list(self, mock_make_request):
        """Test jobs list command."""
        mock_response = {
            "jobs": [
                {
                    "id": "test-job",
                    "title": "Test Job",
                    "enabled": True,
                    "cron": "0 2 * * *",
                    "stats": {
                        "last_execution": "2023-01-01T02:00:00Z",
                        "total_executions": 5,
                        "is_running": False,
                        "consecutive_failures": 0
                    }
                }
            ],
            "total_jobs": 1,
            "enabled_jobs": 1
        }
        mock_make_request.return_value = mock_response
        
        class MockArgs:
            json = False
        
        with patch.object(self.cli, 'print_table') as mock_print_table:
            self.cli.cmd_jobs_list(MockArgs())
            mock_make_request.assert_called_once()
            mock_print_table.assert_called_once()
    
    @patch.object(AtaDataCLI, 'make_request')
    def test_cmd_jobs_create(self, mock_make_request):
        """Test jobs create command."""
        mock_make_request.return_value = {"message": "Job created successfully"}
        
        class MockArgs:
            id = "test-job"
            title = "Test Job"
            description = "A test job"
            cron = "0 2 * * *"
            secrets = "TEST_SECRET=value"
        
        with patch('builtins.print') as mock_print:
            self.cli.cmd_jobs_create(MockArgs())
            mock_make_request.assert_called_once()
            mock_print.assert_called_with("✅ Job created successfully")
    
    @patch.object(AtaDataCLI, 'make_request')
    def test_cmd_secrets_generate(self, mock_make_request):
        """Test secrets generate command."""
        mock_make_request.return_value = {
            "secret": "generated-secret-123",
            "masked": "generated-secret-***",
            "length": 20
        }
        
        class MockArgs:
            length = 20
            json = False
        
        with patch('builtins.print') as mock_print:
            self.cli.cmd_secrets_generate(MockArgs())
            mock_make_request.assert_called_once()
            assert mock_print.call_count >= 2  # Should print multiple lines


if __name__ == "__main__":
    pytest.main([__file__])
