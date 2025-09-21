#!/usr/bin/env python3
"""
Unit tests for Mova CLI functions

Tests individual CLI functions and utilities without requiring full server setup.
"""

import pytest
import sys
import io
from unittest.mock import patch, MagicMock, call
import json
import requests
from pathlib import Path

# Add the CLI module to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "cli"))

from mova import (
    parse_time_duration, 
    format_log_output,
    make_request,
    execute_shell_command,
    list_logs,
    send_log,
    execute_http_command,
    check_health
)

class TestParseTimeDuration:
    """Test time duration parsing utility"""
    
    def test_parse_seconds(self):
        assert parse_time_duration("30s") == 0.5  # 30 seconds = 0.5 minutes
        assert parse_time_duration("60s") == 1.0  # 60 seconds = 1 minute
    
    def test_parse_minutes(self):
        assert parse_time_duration("5m") == 5
        assert parse_time_duration("15m") == 15
    
    def test_parse_hours(self):
        assert parse_time_duration("1h") == 60  # 1 hour = 60 minutes
        assert parse_time_duration("2h") == 120  # 2 hours = 120 minutes
    
    def test_parse_none_input(self):
        assert parse_time_duration(None) is None
        assert parse_time_duration("") is None
    
    def test_invalid_format(self):
        with pytest.raises(ValueError):
            parse_time_duration("invalid")
        
        with pytest.raises(ValueError):
            parse_time_duration("5x")  # Invalid unit
        
        with pytest.raises(ValueError):
            parse_time_duration("abc5m")  # Invalid number

class TestFormatLogOutput:
    """Test log output formatting"""
    
    def test_empty_logs(self, capsys):
        format_log_output([])
        captured = capsys.readouterr()
        assert "📭 Brak logów do wyświetlenia" in captured.out
    
    def test_single_log(self, capsys):
        logs = [{
            'timestamp': '2025-09-18T19:30:00.123456',
            'level': 'info',
            'service': 'test-service',
            'message': 'Test message'
        }]
        
        format_log_output(logs)
        captured = capsys.readouterr()
        
        assert "📊 Znaleziono 1 logów:" in captured.out
        assert "🔵" in captured.out  # Info icon
        assert "2025-09-18T19:30:00" in captured.out
        assert "INFO" in captured.out
        assert "test-service" in captured.out
        assert "Test message" in captured.out
    
    def test_multiple_logs_different_levels(self, capsys):
        logs = [
            {
                'timestamp': '2025-09-18T19:30:00.123456',
                'level': 'info',
                'service': 'service1',
                'message': 'Info message'
            },
            {
                'timestamp': '2025-09-18T19:30:01.123456',
                'level': 'warning',
                'service': 'service2',
                'message': 'Warning message'
            },
            {
                'timestamp': '2025-09-18T19:30:02.123456',
                'level': 'error',
                'service': 'service3',
                'message': 'Error message'
            }
        ]
        
        format_log_output(logs)
        captured = capsys.readouterr()
        
        assert "📊 Znaleziono 3 logów:" in captured.out
        assert "🔵" in captured.out  # Info
        assert "🟡" in captured.out  # Warning
        assert "🔴" in captured.out  # Error
        assert "Info message" in captured.out
        assert "Warning message" in captured.out
        assert "Error message" in captured.out

class TestMakeRequest:
    """Test HTTP request wrapper"""
    
    @patch('requests.get')
    def test_successful_get_request(self, mock_get):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "success", "data": "test"}
        mock_get.return_value = mock_response
        
        result = make_request("GET", "/api/test", {"param": "value"})
        
        assert result == {"status": "success", "data": "test"}
        mock_get.assert_called_once_with("http://localhost:8094/api/test", params={"param": "value"})
    
    @patch('requests.post')
    def test_successful_post_request(self, mock_post):
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "logged"}
        mock_post.return_value = mock_response
        
        result = make_request("POST", "/api/log", {"level": "info", "message": "test"})
        
        assert result == {"status": "logged"}
        mock_post.assert_called_once_with("http://localhost:8094/api/log", json={"level": "info", "message": "test"})
    
    @patch('requests.get')
    def test_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        with pytest.raises(SystemExit):
            make_request("GET", "/api/test")
    
    @patch('requests.get')
    def test_http_error(self, mock_get):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response
        
        with pytest.raises(SystemExit):
            make_request("GET", "/api/test")
    
    def test_unsupported_method(self):
        with pytest.raises(SystemExit):
            make_request("DELETE", "/api/test")

class TestCLICommands:
    """Test CLI command functions"""
    
    @patch('mova.make_request')
    def test_execute_shell_command_success(self, mock_request, capsys):
        mock_request.return_value = {
            "success": True,
            "returncode": 0,
            "stdout": "Hello World\n",
            "stderr": ""
        }
        
        # Mock args object
        args = MagicMock()
        args.cmd = "echo 'Hello World'"
        args.timeout = 30
        args.server = "http://localhost:8094"
        
        execute_shell_command(args)
        captured = capsys.readouterr()
        
        assert "🐚 Wykonywanie komendy shell: echo 'Hello World'" in captured.out
        assert "✅ Komenda wykonana pomyślnie (kod: 0)" in captured.out
        assert "Hello World" in captured.out
        
        mock_request.assert_called_once_with(
            "POST", "/api/shell", 
            {"cmd": "echo 'Hello World'", "timeout": 30}, 
            "http://localhost:8094"
        )
    
    @patch('mova.make_request')
    def test_execute_shell_command_failure(self, mock_request, capsys):
        mock_request.return_value = {
            "success": False,
            "returncode": 1,
            "stdout": "",
            "stderr": "Command not found\n"
        }
        
        args = MagicMock()
        args.cmd = "nonexistent_command"
        args.timeout = 30
        args.server = "http://localhost:8094"
        
        execute_shell_command(args)
        captured = capsys.readouterr()
        
        assert "❌ Komenda zakończona błędem (kod: 1)" in captured.out
        assert "Command not found" in captured.out
    
    @patch('mova.make_request')
    def test_send_log_info(self, mock_request, capsys):
        mock_request.return_value = {
            "status": "logged",
            "entry": {"timestamp": "2025-09-18T19:30:00.123456"}
        }
        
        args = MagicMock()
        args.command = "info"
        args.message = "Test info message"
        args.service = "test-service"
        args.server = "http://localhost:8094"
        
        send_log(args)
        captured = capsys.readouterr()
        
        assert "🔵 Wysyłanie logu INFO: Test info message" in captured.out
        assert "✅ Log zapisany pomyślnie" in captured.out
        
        mock_request.assert_called_once_with(
            "POST", "/api/log", 
            {"level": "info", "message": "Test info message", "service": "test-service"}, 
            "http://localhost:8094"
        )
    
    @patch('mova.make_request')
    def test_send_log_warning(self, mock_request, capsys):
        mock_request.return_value = {
            "status": "logged",
            "entry": {"timestamp": "2025-09-18T19:30:00.123456"}
        }
        
        args = MagicMock()
        args.command = "warning"
        args.message = "Test warning message"
        args.service = None
        args.server = "http://localhost:8094"
        
        send_log(args)
        captured = capsys.readouterr()
        
        assert "🟡 Wysyłanie logu WARNING: Test warning message" in captured.out
        assert "✅ Log zapisany pomyślnie" in captured.out
    
    @patch('mova.make_request')
    def test_send_log_error(self, mock_request, capsys):
        mock_request.return_value = {
            "status": "logged",
            "entry": {"timestamp": "2025-09-18T19:30:00.123456"}
        }
        
        args = MagicMock()
        args.command = "error"
        args.message = "Test error message"
        args.service = "critical-service"
        args.server = "http://localhost:8094"
        
        send_log(args)
        captured = capsys.readouterr()
        
        assert "🔴 Wysyłanie logu ERROR: Test error message" in captured.out
        assert "✅ Log zapisany pomyślnie" in captured.out
    
    @patch('mova.make_request')
    @patch('mova.format_log_output')
    def test_list_logs(self, mock_format, mock_request, capsys):
        mock_request.return_value = {
            "logs": [
                {
                    "timestamp": "2025-09-18T19:30:00.123456",
                    "level": "info",
                    "service": "test",
                    "message": "Test message"
                }
            ],
            "count": 1,
            "total_stored": 10
        }
        
        args = MagicMock()
        args.level = "info"
        args.service = None
        args.limit = 20
        args.last = None
        args.server = "http://localhost:8094"
        
        list_logs(args)
        captured = capsys.readouterr()
        
        assert "📋 Pobieranie logów (poziom: info)" in captured.out
        assert "📊 Znaleziono 1 logów z 10 zapisanych" in captured.out
        
        mock_format.assert_called_once()
        mock_request.assert_called_once()
    
    @patch('mova.make_request')
    @patch('mova.parse_time_duration')
    def test_list_logs_with_time_filter(self, mock_parse_time, mock_request, capsys):
        mock_parse_time.return_value = 30
        mock_request.return_value = {
            "logs": [],
            "count": 0,
            "total_stored": 0
        }
        
        args = MagicMock()
        args.level = "all"
        args.service = "test-service"
        args.limit = 5
        args.last = "30m"
        args.server = "http://localhost:8094"
        
        list_logs(args)
        
        mock_parse_time.assert_called_once_with("30m")
        expected_params = {
            "service": "test-service",
            "limit": 5,
            "last_minutes": 30
        }
        mock_request.assert_called_once_with("GET", "/api/logs", expected_params, "http://localhost:8094")
    
    @patch('mova.make_request')
    def test_execute_http_command(self, mock_request, capsys):
        mock_request.return_value = {
            "status": "queued",
            "target": "localhost",
            "message": "JavaScript execution queued"
        }
        
        args = MagicMock()
        args.address = "localhost"
        args.js_code = "console.log('Hello from CLI');"
        args.server = "http://localhost:8094"
        
        execute_http_command(args)
        captured = capsys.readouterr()
        
        assert "🌐 Wysyłanie komendy JS do localhost: console.log('Hello from CLI');" in captured.out
        assert "✅ Komenda JavaScript została umieszczona w kolejce" in captured.out
        assert "🎯 Cel: localhost" in captured.out
        
        mock_request.assert_called_once_with(
            "POST", "/api/http-exec",
            {"js_code": "console.log('Hello from CLI');", "target": "localhost"},
            "http://localhost:8094"
        )
    
    @patch('mova.make_request')
    def test_check_health_healthy(self, mock_request, capsys):
        mock_request.side_effect = [
            {
                "status": "healthy",
                "timestamp": "2025-09-18T19:30:00.123456",
                "version": "1.0.0",
                "shell_enabled": True
            },
            {"message": "Mova server running"}  # Root endpoint response
        ]
        
        args = MagicMock()
        args.server = "http://localhost:8094"
        
        check_health(args)
        captured = capsys.readouterr()
        
        assert "🔍 Sprawdzanie statusu serwera: http://localhost:8094" in captured.out
        assert "✅ Serwer jest zdrowy" in captured.out
        assert "🏷️ Wersja: 1.0.0" in captured.out
        assert "🐚 Shell włączony: ✅ TAK" in captured.out
        assert "🌐 Połączenie HTTP: ✅ OK" in captured.out
    
    @patch('mova.make_request')
    def test_check_health_unhealthy(self, mock_request, capsys):
        mock_request.side_effect = [
            {
                "status": "degraded",
                "timestamp": "2025-09-18T19:30:00.123456",
                "version": "1.0.0",
                "shell_enabled": False
            },
            Exception("Connection failed")  # Root endpoint fails
        ]
        
        args = MagicMock()
        args.server = "http://localhost:8094"
        
        check_health(args)
        captured = capsys.readouterr()
        
        assert "⚠️ Status serwera: degraded" in captured.out
        assert "🐚 Shell włączony: ❌ NIE" in captured.out
        assert "🌐 Połączenie HTTP: ❌ BŁĄD" in captured.out

class TestCLIIntegration:
    """Integration tests for CLI command combinations"""
    
    @patch('mova.make_request')
    def test_logging_and_retrieval_workflow(self, mock_request, capsys):
        # Mock responses for log sending and retrieval
        mock_request.side_effect = [
            {"status": "logged", "entry": {"timestamp": "2025-09-18T19:30:00.123456"}},  # Send log
            {  # Retrieve logs
                "logs": [
                    {
                        "timestamp": "2025-09-18T19:30:00.123456",
                        "level": "info",
                        "service": "test",
                        "message": "Test workflow message"
                    }
                ],
                "count": 1,
                "total_stored": 1
            }
        ]
        
        # Send a log
        send_args = MagicMock()
        send_args.command = "info"
        send_args.message = "Test workflow message"
        send_args.service = "test"
        send_args.server = "http://localhost:8094"
        
        send_log(send_args)
        
        # Retrieve logs
        list_args = MagicMock()
        list_args.level = "info"
        list_args.service = "test"
        list_args.limit = 10
        list_args.last = None
        list_args.server = "http://localhost:8094"
        
        list_logs(list_args)
        
        captured = capsys.readouterr()
        
        # Verify both operations completed
        assert "🔵 Wysyłanie logu INFO: Test workflow message" in captured.out
        assert "✅ Log zapisany pomyślnie" in captured.out
        assert "📋 Pobieranie logów (poziom: info)" in captured.out
        assert "Test workflow message" in captured.out

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
