#!/usr/bin/env python3
"""Debug MCP protocol interaction with Docker container."""

import json
import subprocess
import sys

def test_mcp_docker():
    """Test MCP protocol with Docker container."""
    
    # Docker command
    docker_cmd = [
        "docker", "run", "-i", "--rm",
        "-e", "JIRA_URL=https://royashish.atlassian.net",
        "-e", "JIRA_USERNAME=royashish@gmail.com", 
        "-e", "JIRA_API_TOKEN=ATATT3xFfGF0ei2SBmhpyNuqHPg-VWc86WuuDl7fRQC7LVWKNlwd0RM5SCS7X2FvU0KtRd7M6yfbYl1fMP-WsxBVuIPjagHbava-z_ds7d8ofKOwYQP4GsdCCWxWpvF4SqpWQsBaUay8OboXlD1q1XhJOyWtHSh-2QvO2Vegm6es9oRNpxYqC6o=BCBFAD6C",
        "royashish/jira-mcp-server:latest"
    ]
    
    # MCP messages
    messages = [
        # Initialize
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        },
        # List tools
        {
            "jsonrpc": "2.0", 
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # Call get_projects tool
        {
            "jsonrpc": "2.0",
            "id": 3, 
            "method": "tools/call",
            "params": {
                "name": "get_projects",
                "arguments": {}
            }
        }
    ]
    
    # Prepare input
    input_data = "\n".join(json.dumps(msg) for msg in messages) + "\n"
    
    print("🔧 Testing MCP protocol with Docker container...")
    print(f"📤 Sending {len(messages)} messages")
    
    try:
        # Run Docker container
        process = subprocess.run(
            docker_cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=30
        )
        
        print(f"📊 Exit code: {process.returncode}")
        
        if process.stdout:
            print("📥 STDOUT:")
            for line in process.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        response = json.loads(line)
                        print(f"  {json.dumps(response, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"  {line}")
        
        if process.stderr:
            print("⚠️  STDERR:")
            print(process.stderr)
            
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout - container took too long to respond")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_mcp_docker()
    sys.exit(0 if success else 1)