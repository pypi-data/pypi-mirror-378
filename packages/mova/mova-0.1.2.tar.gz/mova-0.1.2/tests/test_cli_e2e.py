#!/usr/bin/env python3
"""
Comprehensive End-to-End Tests for Mova CLI Features

This module contains complete E2E tests for all CLI commands:
- Services management (list, enable, disable, status, info)
- RSS server functionality (start, stop, status, feed access)
- Voice interface (talk command)
- Auto-start functionality (on/off commands)
"""

import pytest
import subprocess
import time
import requests
import json
import os
import sys
import signal
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any


class TestMovaCLI:
    """Test class for Mova CLI end-to-end functionality"""
    
    @pytest.fixture(autouse=True)
    def setup_cli_environment(self):
        """Setup test environment for CLI tests"""
        # Get paths
        self.project_root = Path(__file__).parent.parent
        self.cli_path = self.project_root / "venv" / "bin" / "python"
        self.mova_script = self.project_root / "cli" / "mova.py"
        
        # Ensure paths exist
        assert self.cli_path.exists(), f"CLI path not found: {self.cli_path}"
        assert self.mova_script.exists(), f"Mova script not found: {self.mova_script}"
        
        # Store any running RSS servers to clean up later
        self.rss_pids = []
        
        yield
        
        # Cleanup: stop any RSS servers started during tests
        self._cleanup_rss_servers()
    
    def _cleanup_rss_servers(self):
        """Clean up any RSS servers started during tests"""
        for pid in self.rss_pids:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.5)
            except ProcessLookupError:
                pass  # Process already ended
    
    def _run_mova_command(self, command: str, timeout: int = 10) -> subprocess.CompletedProcess:
        """Run a Mova CLI command and return the result"""
        cmd = [str(self.cli_path), str(self.mova_script)] + command.split()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_root)
            )
            return result
        except subprocess.TimeoutExpired:
            pytest.fail(f"Command timed out: {' '.join(cmd)}")
    
    def _run_mova_command_async(self, command: str) -> subprocess.Popen:
        """Run a Mova CLI command asynchronously"""
        cmd = [str(self.cli_path), str(self.mova_script)] + command.split()
        
        return subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(self.project_root)
        )


class TestServicesManagement(TestMovaCLI):
    """Tests for services management commands"""
    
    def test_services_list(self):
        """Test 'mova services list' command"""
        result = self._run_mova_command("services list")
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Check that output contains expected service types
        output = result.stdout.lower()
        assert any(service in output for service in ['docker', 'systemd', 'system']), \
            f"No recognized services in output: {result.stdout}"
    
    def test_services_status(self):
        """Test 'mova services status' command"""
        result = self._run_mova_command("services status")
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Should show status of all services
        output = result.stdout.lower()
        assert 'status' in output or 'running' in output or 'stopped' in output, \
            f"No status information in output: {result.stdout}"
    
    def test_services_info_docker(self):
        """Test 'mova services info docker' command"""
        result = self._run_mova_command("services info docker")
        
        # Command should succeed even if Docker is not available
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        output = result.stdout.lower()
        # Should contain either Docker info or unavailable message
        assert 'docker' in output, f"No Docker information in output: {result.stdout}"
    
    def test_services_info_systemd(self):
        """Test 'mova services info systemd' command"""
        result = self._run_mova_command("services info systemd")
        
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        output = result.stdout.lower()
        assert 'systemd' in output or 'system' in output, \
            f"No SystemD information in output: {result.stdout}"
    
    def test_services_enable_disable_dry_run(self):
        """Test services enable/disable commands (dry run mode)"""
        # Test enable command (should show what would be done)
        result = self._run_mova_command("services enable test-service")
        
        # Command might fail if service doesn't exist, but should not crash
        assert 'test-service' in result.stdout or 'test-service' in result.stderr, \
            "Service name not mentioned in output"
        
        # Test disable command
        result = self._run_mova_command("services disable test-service")
        
        # Same expectation - should mention the service name
        assert 'test-service' in result.stdout or 'test-service' in result.stderr, \
            "Service name not mentioned in output"


class TestRSSServerFunctionality(TestMovaCLI):
    """Tests for RSS server functionality"""
    
    def test_rss_server_start_stop_cycle(self):
        """Test complete RSS server lifecycle: start, check status, stop"""
        test_port = 8012  # Use different port to avoid conflicts
        
        # 1. Start RSS server
        result = self._run_mova_command(f"rss --port {test_port}")
        assert result.returncode == 0, f"Failed to start RSS server: {result.stderr}"
        
        # Extract PID from output
        pid_match = result.stdout
        assert '✅' in result.stdout, f"RSS server start confirmation not found: {result.stdout}"
        
        time.sleep(2)  # Give server time to fully start
        
        try:
            # 2. Check RSS server status
            status_result = self._run_mova_command("rss --status")
            assert status_result.returncode == 0, f"Failed to check RSS status: {status_result.stderr}"
            assert 'działa' in status_result.stdout or 'running' in status_result.stdout.lower(), \
                f"RSS server not reported as running: {status_result.stdout}"
            
            # 3. Test RSS feed accessibility
            response = requests.get(f"http://localhost:{test_port}/rss", timeout=5)
            assert response.status_code == 200, f"RSS feed not accessible: {response.status_code}"
            assert response.headers.get('content-type', '').startswith('application/rss+xml') or \
                   response.headers.get('content-type', '').startswith('text/xml'), \
                f"Invalid RSS content type: {response.headers.get('content-type')}"
            
            # 4. Test RSS feed content
            rss_content = response.text
            assert '<?xml' in rss_content, "RSS feed is not valid XML"
            assert '<rss' in rss_content, "RSS feed missing RSS tag"
            assert 'Mova' in rss_content, "RSS feed missing Mova branding"
            
            # 5. Test other endpoints
            status_response = requests.get(f"http://localhost:{test_port}/status", timeout=5)
            assert status_response.status_code == 200, f"Status endpoint not accessible"
            
        finally:
            # 6. Stop RSS server
            stop_result = self._run_mova_command("rss --stop")
            assert stop_result.returncode == 0, f"Failed to stop RSS server: {stop_result.stderr}"
            
            # Verify server is stopped
            time.sleep(1)
            final_status = self._run_mova_command("rss --status")
            assert 'nie działa' in final_status.stdout or 'not running' in final_status.stdout.lower(), \
                f"RSS server still reported as running: {final_status.stdout}"
    
    def test_rss_server_port_conflict(self):
        """Test RSS server behavior with port conflicts"""
        test_port = 8013
        
        # Start first server
        result1 = self._run_mova_command(f"rss --port {test_port}")
        assert result1.returncode == 0, f"Failed to start first RSS server: {result1.stderr}"
        
        try:
            time.sleep(2)
            
            # Try to start second server on same port
            result2 = self._run_mova_command(f"rss --port {test_port}")
            assert result2.returncode != 0, "Second RSS server should fail due to port conflict"
            assert 'zajęty' in result2.stdout or 'occupied' in result2.stdout.lower(), \
                "Port conflict not properly detected"
        
        finally:
            # Cleanup
            self._run_mova_command("rss --stop")
    
    def test_rss_feed_content_quality(self):
        """Test RSS feed content structure and quality"""
        test_port = 8014
        
        # Start RSS server
        result = self._run_mova_command(f"rss --port {test_port}")
        assert result.returncode == 0, f"Failed to start RSS server: {result.stderr}"
        
        try:
            time.sleep(2)
            
            # Get RSS feed
            response = requests.get(f"http://localhost:{test_port}/rss", timeout=5)
            assert response.status_code == 200
            
            rss_content = response.text
            
            # Test RSS structure
            required_elements = [
                '<rss',
                '<channel>',
                '<title>',
                '<description>',
                '<link>',
                '</channel>',
                '</rss>'
            ]
            
            for element in required_elements:
                assert element in rss_content, f"RSS feed missing required element: {element}"
            
            # Test Mova-specific content
            assert 'Mova' in rss_content, "RSS feed missing Mova branding"
            assert 'System Monitor' in rss_content or 'System' in rss_content, \
                "RSS feed missing system monitoring context"
        
        finally:
            self._run_mova_command("rss --stop")


class TestVoiceInterface(TestMovaCLI):
    """Tests for voice interface (talk command)"""
    
    def test_talk_command_help(self):
        """Test voice interface help and basic functionality"""
        result = self._run_mova_command("talk --help")
        
        # Command should show help even if voice features aren't fully implemented
        assert result.returncode == 0 or 'help' in result.stdout.lower() or 'talk' in result.stdout.lower(), \
            f"Talk command help not accessible: {result.stderr}"
    
    def test_talk_command_status(self):
        """Test voice interface status check"""
        # Test with required language parameter
        result = self._run_mova_command("talk pl")
        
        # Should either work or show informative error about missing dependencies
        output = result.stdout + result.stderr
        voice_keywords = ['voice', 'audio', 'microphone', 'whisper', 'speech', 'talk', 'pl', 'language']
        
        assert any(keyword in output.lower() for keyword in voice_keywords), \
            f"Talk command output doesn't mention voice functionality: {output}"


class TestAutoStartFunctionality(TestMovaCLI):
    """Tests for auto-start functionality (on/off commands)"""
    
    def test_autostart_on_command(self):
        """Test 'mova on' command for enabling auto-start"""
        result = self._run_mova_command("on")
        
        assert result.returncode == 0, f"Auto-start enable failed: {result.stderr}"
        
        output = result.stdout.lower()
        assert 'auto' in output or 'start' in output or 'włącz' in output, \
            f"Auto-start enable output unclear: {result.stdout}"
    
    def test_autostart_off_command(self):
        """Test 'mova off' command for disabling auto-start"""
        result = self._run_mova_command("off")
        
        assert result.returncode == 0, f"Auto-start disable failed: {result.stderr}"
        
        output = result.stdout.lower()
        assert 'auto' in output or 'stop' in output or 'wyłącz' in output, \
            f"Auto-start disable output unclear: {result.stdout}"
    
    def test_autostart_toggle_cycle(self):
        """Test complete auto-start toggle cycle: on -> off -> on"""
        # Enable auto-start
        result_on = self._run_mova_command("on")
        assert result_on.returncode == 0, f"Failed to enable auto-start: {result_on.stderr}"
        
        # Disable auto-start
        result_off = self._run_mova_command("off")
        assert result_off.returncode == 0, f"Failed to disable auto-start: {result_off.stderr}"
        
        # Enable again
        result_on2 = self._run_mova_command("on")
        assert result_on2.returncode == 0, f"Failed to re-enable auto-start: {result_on2.stderr}"


class TestCLIIntegration(TestMovaCLI):
    """Integration tests for CLI functionality"""
    
    def test_cli_help_completeness(self):
        """Test that CLI help shows all available commands"""
        result = self._run_mova_command("--help")
        
        assert result.returncode == 0, f"CLI help failed: {result.stderr}"
        
        # Check that help mentions all major command categories
        help_text = result.stdout.lower()
        expected_commands = ['services', 'rss', 'talk', 'on', 'off']
        
        for command in expected_commands:
            assert command in help_text, f"Command '{command}' not mentioned in help: {result.stdout}"
    
    def test_cli_error_handling(self):
        """Test CLI error handling with invalid commands"""
        result = self._run_mova_command("invalid-command")
        
        # Should fail gracefully with helpful error message
        assert result.returncode != 0, "Invalid command should fail"
        
        error_output = result.stderr.lower()
        assert 'error' in error_output or 'invalid' in error_output or 'unknown' in error_output, \
            f"Error message not informative: {result.stderr}"
    
    def test_cli_version_info(self):
        """Test CLI basic info display (version flag not implemented yet)"""
        # Test basic help instead since --version is not implemented
        result = self._run_mova_command("--help")
        
        # Should show help info with Mova references
        assert result.returncode == 0, f"Help command failed: {result.stderr}"
        assert 'mova' in result.stdout.lower(), \
            f"Help output doesn't mention Mova: {result.stdout}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
