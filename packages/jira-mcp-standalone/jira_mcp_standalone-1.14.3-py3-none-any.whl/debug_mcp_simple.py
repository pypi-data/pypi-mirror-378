#!/usr/bin/env python3
"""Simple MCP test with proper protocol flow."""

import json
import subprocess

def test_simple_mcp():
    """Test with minimal MCP protocol."""
    
    docker_cmd = [
        "docker", "run", "-i", "--rm",
        "-e", "JIRA_URL=https://royashish.atlassian.net",
        "-e", "JIRA_USERNAME=royashish@gmail.com", 
        "-e", "JIRA_API_TOKEN=ATATT3xFfGF0ei2SBmhpyNuqHPg-VWc86WuuDl7fRQC7LVWKNlwd0RM5SCS7X2FvU0KtRd7M6yfbYl1fMP-WsxBVuIPjagHbava-z_ds7d8ofKOwYQP4GsdCCWxWpvF4SqpWQsBaUay8OboXlD1q1XhJOyWtHSh-2QvO2Vegm6es9oRNpxYqC6o=BCBFAD6C",
        "royashish/jira-mcp-server:latest"
    ]
    
    # Try just initialization and then a simple notification
    messages = [
        # Initialize
        json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }),
        # Initialized notification (required by MCP)
        json.dumps({
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        }),
        # Now try tools/list
        json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        })
    ]
    
    input_data = "\n".join(messages) + "\n"
    
    print("🔧 Testing MCP with proper initialization flow...")
    
    try:
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
                        print(f"  ✅ {json.dumps(response, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"  📝 {line}")
        
        if process.stderr:
            print("⚠️  STDERR:")
            print(process.stderr)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_mcp()