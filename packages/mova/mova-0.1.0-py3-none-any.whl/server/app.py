#!/usr/bin/env python3

"""Mova Server - serwer RPC/HTTP/WebSocket dla warstwy komunikacyjnej Mova."""

import os
import json
import subprocess
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mova.server")

# Wczytaj konfigurację
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/default.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

PORT = config['server']['port']
HOST = config['server']['host']
MOVA_ALLOW_SHELL = config['shell']['allow']

logger.info(f"Serwer Mova uruchamia się na porcie {PORT}")

# Data models
class ShellCommand(BaseModel):
    cmd: str
    timeout: Optional[int] = 30

class LogMessage(BaseModel):
    level: str
    message: str
    service: Optional[str] = None
    metadata: Optional[dict] = None

class HttpExecution(BaseModel):
    js_code: str
    target: Optional[str] = "localhost"

class Message(BaseModel):
    type: str
    payload: str
    timestamp: Optional[str] = None

# In-memory log storage (for development)
logs_storage = []

# Mount static files
app.mount("/examples", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../examples")), name="examples")
app.mount("/sdk", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "../sdk")), name="sdk")

@app.get("/")
async def get():
    return HTMLResponse(content="<h1>Mova Server</h1><p>Warstwa komunikacyjna Mova jest aktywna.</p>")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "shell_enabled": MOVA_ALLOW_SHELL
    }

@app.post("/api/shell")
async def execute_shell(command: ShellCommand):
    """Execute shell command (if enabled)"""
    if not MOVA_ALLOW_SHELL:
        raise HTTPException(status_code=403, detail="Shell execution is disabled")
    
    try:
        result = subprocess.run(
            command.cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=command.timeout
        )
        
        response = {
            "command": command.cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Log the command execution
        log_entry = {
            "level": "info" if result.returncode == 0 else "error",
            "message": f"Shell command executed: {command.cmd}",
            "service": "shell",
            "metadata": response,
            "timestamp": datetime.now().isoformat()
        }
        logs_storage.append(log_entry)
        
        return response
        
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Command timed out after {command.timeout} seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Shell execution error: {str(e)}")

@app.post("/api/log")
async def add_log(log: LogMessage):
    """Add log message"""
    log_entry = {
        "level": log.level,
        "message": log.message,
        "service": log.service or "unknown",
        "metadata": log.metadata or {},
        "timestamp": datetime.now().isoformat()
    }
    logs_storage.append(log_entry)
    logger.info(f"Log added: {log.level.upper()} - {log.message}")
    return {"status": "logged", "entry": log_entry}

@app.get("/api/logs")
async def get_logs(
    level: Optional[str] = None,
    service: Optional[str] = None,
    last_minutes: Optional[int] = None,
    limit: Optional[int] = 100
):
    """Get logs with filtering"""
    filtered_logs = logs_storage.copy()
    
    # Filter by level
    if level and level != "all":
        filtered_logs = [log for log in filtered_logs if log["level"] == level]
    
    # Filter by service
    if service:
        filtered_logs = [log for log in filtered_logs if log["service"] == service]
    
    # Filter by time
    if last_minutes:
        cutoff_time = datetime.now() - timedelta(minutes=last_minutes)
        filtered_logs = [
            log for log in filtered_logs 
            if datetime.fromisoformat(log["timestamp"]) > cutoff_time
        ]
    
    # Apply limit
    filtered_logs = filtered_logs[-limit:] if limit else filtered_logs
    
    return {
        "logs": filtered_logs,
        "count": len(filtered_logs),
        "total_stored": len(logs_storage)
    }

@app.post("/api/message")
async def send_message(message: Message):
    """Handle messages sent via SDK"""
    # Log the message
    log_entry = {
        "level": "info",
        "message": f"Message received: {message.payload}",
        "service": "chat",
        "metadata": {
            "type": message.type,
            "payload": message.payload,
            "timestamp": message.timestamp or datetime.now().isoformat()
        },
        "timestamp": datetime.now().isoformat()
    }
    logs_storage.append(log_entry)
    
    # Process different message types
    if message.type == "chat":
        # Handle chat messages
        response_payload = f"Received chat message: {message.payload}"
    elif message.type == "shell" and MOVA_ALLOW_SHELL:
        # Handle shell commands
        try:
            result = subprocess.run(
                message.payload,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            response_payload = f"Command executed. Return code: {result.returncode}\nOutput: {result.stdout}\nError: {result.stderr}"
        except Exception as e:
            response_payload = f"Command execution failed: {str(e)}"
    else:
        response_payload = f"Processed {message.type} message: {message.payload}"
    
    return {
        "status": "received",
        "type": message.type,
        "payload": message.payload,
        "response": response_payload,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/http-exec")
async def http_execute(execution: HttpExecution):
    """Store JavaScript for execution (simulation)"""
    log_entry = {
        "level": "info",
        "message": f"HTTP execution requested for {execution.target}",
        "service": "http-exec",
        "metadata": {
            "js_code": execution.js_code,
            "target": execution.target
        },
        "timestamp": datetime.now().isoformat()
    }
    logs_storage.append(log_entry)
    
    return {
        "status": "queued",
        "target": execution.target,
        "js_code": execution.js_code,
        "message": "JavaScript execution queued (use WebSocket for real-time execution)"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Otrzymano wiadomość: {data}")
            
            try:
                message = json.loads(data)
                if message.get("type") == "http-exec":
                    # Handle JavaScript execution request
                    response = {
                        "type": "http-exec-result",
                        "status": "executed",
                        "js_code": message.get("js_code", ""),
                        "timestamp": datetime.now().isoformat()
                    }
                    await websocket.send_text(json.dumps(response))
                else:
                    await websocket.send_text(f"Echo: {data}")
            except json.JSONDecodeError:
                await websocket.send_text(f"Echo: {data}")
                
    except Exception as e:
        logger.error(f"Błąd WebSocket: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)
