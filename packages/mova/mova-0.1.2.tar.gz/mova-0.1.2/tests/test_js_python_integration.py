#!/usr/bin/env python3
"""
Comprehensive JavaScript-Python Backend Integration Tests

Tests the complete communication flow between browser JavaScript and Python backend
through Mova CLI and server APIs.
"""

import pytest
import pytest_asyncio
import asyncio
import json
import subprocess
import time
import requests
import websockets
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tempfile
import os
from pathlib import Path

class TestJSPythonIntegration:
    """Test suite for JavaScript-Python integration via Mova CLI"""
    
    @pytest.fixture(scope="class")
    def mova_server(self):
        """Start Mova server for testing"""
        # Start server in background
        server_process = subprocess.Popen(
            ["./venv/bin/python", "server/app.py"],
            cwd=Path(__file__).parent.parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Verify server is running
        try:
            response = requests.get("http://localhost:8094/health")
            assert response.status_code == 200
        except Exception as e:
            server_process.terminate()
            raise Exception(f"Server failed to start: {e}")
        
        yield server_process
        
        # Cleanup
        server_process.terminate()
        server_process.wait()
    
    @pytest.fixture
    def mova_cli(self):
        """Mova CLI command runner"""
        def run_command(cmd_args):
            cli_path = Path(__file__).parent.parent / "venv/bin/mova"
            result = subprocess.run(
                [str(cli_path)] + cmd_args,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        return run_command
    
    @pytest.fixture
    def browser_driver(self):
        """Selenium WebDriver for browser testing"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=chrome_options)
            yield driver
            driver.quit()
        except Exception:
            # If Chrome is not available, skip browser tests
            pytest.skip("Chrome WebDriver not available")
    
    def test_mova_server_health_check(self, mova_server, mova_cli):
        """Test basic Mova server health via CLI"""
        result = mova_cli(["health"])
        
        assert result["success"], f"Health check failed: {result['stderr']}"
        assert "✅ Serwer jest zdrowy" in result["stdout"]
        assert "🐚 Shell włączony: ✅ TAK" in result["stdout"]
    
    def test_shell_command_execution(self, mova_server, mova_cli):
        """Test shell command execution via Mova CLI"""
        # Test basic command
        result = mova_cli(["shell", "echo 'Test from Python backend'"])
        
        assert result["success"], f"Shell command failed: {result['stderr']}"
        assert "✅ Komenda wykonana pomyślnie" in result["stdout"]
        assert "Test from Python backend" in result["stdout"]
    
    def test_logging_functionality(self, mova_server, mova_cli):
        """Test comprehensive logging functionality"""
        test_message = f"Test log message {int(time.time())}"
        service_name = "python-integration-test"
        
        # Test info logging
        result = mova_cli(["info", test_message, "--service", service_name])
        assert result["success"], f"Info logging failed: {result['stderr']}"
        assert "✅ Log zapisany pomyślnie" in result["stdout"]
        
        # Test warning logging
        warning_msg = f"Test warning {int(time.time())}"
        result = mova_cli(["warning", warning_msg, "--service", service_name])
        assert result["success"], f"Warning logging failed: {result['stderr']}"
        
        # Test error logging
        error_msg = f"Test error {int(time.time())}"
        result = mova_cli(["error", error_msg, "--service", service_name])
        assert result["success"], f"Error logging failed: {result['stderr']}"
        
        # Verify logs can be retrieved
        result = mova_cli(["list", "all", "--service", service_name, "--limit", "10"])
        assert result["success"], f"Log retrieval failed: {result['stderr']}"
        assert test_message in result["stdout"]
        assert warning_msg in result["stdout"]
        assert error_msg in result["stdout"]
    
    def test_javascript_execution_queueing(self, mova_server, mova_cli):
        """Test JavaScript execution queueing"""
        js_code = "console.log('Hello from Python test via Mova CLI');"
        target_host = "test-browser.local"
        
        result = mova_cli(["http", target_host, js_code])
        
        assert result["success"], f"JS execution queueing failed: {result['stderr']}"
        assert "✅ Komenda JavaScript została umieszczona w kolejce" in result["stdout"]
        assert f"🎯 Cel: {target_host}" in result["stdout"]
    
    def test_log_filtering_and_retrieval(self, mova_server, mova_cli):
        """Test advanced log filtering and retrieval"""
        # Create logs with different levels and services
        test_data = [
            ("info", "Service A startup", "service-a"),
            ("warning", "High memory usage", "service-a"),
            ("error", "Database connection lost", "service-b"),
            ("info", "Service B ready", "service-b"),
        ]
        
        for level, message, service in test_data:
            result = mova_cli([level, message, "--service", service])
            assert result["success"], f"Failed to log {level}: {result['stderr']}"
        
        # Test filtering by level
        result = mova_cli(["list", "error", "--limit", "5"])
        assert result["success"], f"Error log filtering failed: {result['stderr']}"
        assert "Database connection lost" in result["stdout"]
        assert "High memory usage" not in result["stdout"]
        
        # Test filtering by service
        result = mova_cli(["list", "all", "--service", "service-a", "--limit", "5"])
        assert result["success"], f"Service filtering failed: {result['stderr']}"
        assert "Service A startup" in result["stdout"]
        assert "Service B ready" not in result["stdout"]
    
    def test_concurrent_operations(self, mova_server, mova_cli):
        """Test concurrent CLI operations"""
        import threading
        results = []
        
        def run_concurrent_command(cmd_args, identifier):
            result = mova_cli(cmd_args)
            results.append((identifier, result))
        
        # Start multiple concurrent operations
        threads = []
        for i in range(5):
            # Mix of different operations
            if i % 3 == 0:
                cmd = ["shell", f"echo 'Concurrent test {i}'"]
            elif i % 3 == 1:
                cmd = ["info", f"Concurrent log {i}", "--service", f"concurrent-{i}"]
            else:
                cmd = ["health"]
            
            thread = threading.Thread(
                target=run_concurrent_command, 
                args=(cmd, f"thread-{i}")
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)
        
        # Verify all operations succeeded
        assert len(results) == 5, f"Not all concurrent operations completed: {len(results)}"
        for identifier, result in results:
            assert result["success"], f"Concurrent operation {identifier} failed: {result['stderr']}"

class TestBrowserJSIntegration:
    """Test browser JavaScript integration with Mova backend"""
    
    @pytest.fixture
    def test_html_page(self):
        """Create a test HTML page with Mova integration"""
        html_content = '''
<!DOCTYPE html>
<html>
<head>
    <title>Mova CLI JavaScript Integration Test</title>
</head>
<body>
    <h1>Mova CLI Test Page</h1>
    <div id="status">Loading...</div>
    <button id="test-button">Test Mova Integration</button>
    <div id="results"></div>
    
    <script>
        // Mock Mova CLI JavaScript client
        class MovaClient {
            constructor(serverUrl = 'http://localhost:8094') {
                this.serverUrl = serverUrl;
            }
            
            async sendLog(level, message, service = 'browser-client') {
                try {
                    const response = await fetch(`${this.serverUrl}/api/log`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            level: level,
                            message: message,
                            service: service
                        })
                    });
                    
                    const result = await response.json();
                    this.displayResult(`Log sent: ${level} - ${message}`);
                    return result;
                } catch (error) {
                    this.displayResult(`Error sending log: ${error.message}`);
                    throw error;
                }
            }
            
            async executeShell(command) {
                try {
                    const response = await fetch(`${this.serverUrl}/api/shell`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            cmd: command
                        })
                    });
                    
                    const result = await response.json();
                    this.displayResult(`Shell executed: ${command}`);
                    return result;
                } catch (error) {
                    this.displayResult(`Error executing shell: ${error.message}`);
                    throw error;
                }
            }
            
            async checkHealth() {
                try {
                    const response = await fetch(`${this.serverUrl}/health`);
                    const result = await response.json();
                    this.displayResult(`Server health: ${result.status}`);
                    return result;
                } catch (error) {
                    this.displayResult(`Error checking health: ${error.message}`);
                    throw error;
                }
            }
            
            displayResult(message) {
                const resultsDiv = document.getElementById('results');
                const p = document.createElement('p');
                p.textContent = `${new Date().toLocaleTimeString()}: ${message}`;
                resultsDiv.appendChild(p);
            }
        }
        
        // Initialize Mova client
        const mova = new MovaClient();
        
        // Set up event handlers
        document.addEventListener('DOMContentLoaded', async function() {
            document.getElementById('status').textContent = 'Ready';
            
            document.getElementById('test-button').addEventListener('click', async function() {
                try {
                    // Test health check
                    await mova.checkHealth();
                    
                    // Test logging
                    await mova.sendLog('info', 'Browser integration test started');
                    
                    // Test shell command
                    await mova.executeShell('echo "Hello from browser via Mova"');
                    
                    // Test warning log
                    await mova.sendLog('warning', 'Test warning from browser');
                    
                    mova.displayResult('All tests completed successfully!');
                } catch (error) {
                    mova.displayResult(`Test failed: ${error.message}`);
                }
            });
        });
        
        // Auto-run basic test
        window.addEventListener('load', function() {
            setTimeout(async () => {
                try {
                    await mova.checkHealth();
                    mova.displayResult('Auto health check completed');
                } catch (error) {
                    mova.displayResult(`Auto health check failed: ${error.message}`);
                }
            }, 1000);
        });
    </script>
</body>
</html>
        '''
        
        # Create temporary HTML file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False)
        temp_file.write(html_content)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
    
    def test_browser_mova_integration(self, browser_driver, test_html_page):
        """Test full browser-to-Mova integration"""
        # Load the test page
        browser_driver.get(f"file://{test_html_page}")
        
        # Wait for page to load
        WebDriverWait(browser_driver, 10).until(
            EC.text_to_be_present_in_element((By.ID, "status"), "Ready")
        )
        
        # Click test button
        test_button = browser_driver.find_element(By.ID, "test-button")
        test_button.click()
        
        # Wait for results
        time.sleep(5)
        
        # Check results
        results_div = browser_driver.find_element(By.ID, "results")
        results_text = results_div.text
        
        assert "Server health: healthy" in results_text
        assert "Log sent: info" in results_text
        assert "Shell executed: echo" in results_text
        assert "All tests completed successfully!" in results_text

class TestWebSocketIntegration:
    """Test WebSocket communication between JavaScript and Python"""
    
    @pytest_asyncio.fixture
    async def websocket_test_server(self):
        """Simple WebSocket server for testing"""
        async def echo_server(websocket, path):
            try:
                async for message in websocket:
                    data = json.loads(message)
                    
                    # Simulate Mova CLI processing
                    if data.get("type") == "shell":
                        response = {
                            "type": "shell_result",
                            "success": True,
                            "output": f"Executed: {data.get('command', '')}"
                        }
                    elif data.get("type") == "log":
                        response = {
                            "type": "log_result",
                            "success": True,
                            "message": "Log recorded"
                        }
                    else:
                        response = {
                            "type": "error",
                            "message": "Unknown command type"
                        }
                    
                    await websocket.send(json.dumps(response))
            except websockets.exceptions.ConnectionClosed:
                pass
        
        # Start WebSocket server using current event loop with proper handler
        async def handler(websocket):
            await echo_server(websocket, "/")  # Use default path
        
        server_instance = await websockets.serve(handler, "localhost", 8765)
        
        yield server_instance
        
        # Cleanup
        server_instance.close()
        await server_instance.wait_closed()
    
    @pytest.mark.asyncio
    async def test_websocket_communication(self, websocket_test_server):
        """Test WebSocket communication flow"""
        # Wait a moment for server to be ready
        await asyncio.sleep(0.1)
        
        uri = "ws://localhost:8765"
        async with websockets.connect(uri) as websocket:
            # Test shell command
            shell_msg = {
                "type": "shell",
                "command": "echo 'WebSocket test'"
            }
            await websocket.send(json.dumps(shell_msg))
            response = await websocket.recv()
            shell_result = json.loads(response)
            
            assert shell_result["type"] == "shell_result"
            assert shell_result["success"] is True
            assert "WebSocket test" in shell_result["output"]
            
            # Test logging
            log_msg = {
                "type": "log",
                "level": "info",
                "message": "WebSocket log test"
            }
            await websocket.send(json.dumps(log_msg))
            response = await websocket.recv()
            log_result = json.loads(response)
            
            assert log_result["type"] == "log_result"
            assert log_result["success"] is True

# Test configuration
def pytest_configure(config):
    """Pytest configuration for JavaScript-Python integration tests"""
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests requiring full setup"
    )
    config.addinivalue_line(
        "markers",
        "browser: marks tests requiring browser driver (selenium)"
    )
    config.addinivalue_line(
        "markers",
        "websocket: marks tests requiring WebSocket functionality"
    )

if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
