#!/usr/bin/env python3
"""Test MCP server locally."""

import json
import subprocess
import sys
import os

def test_local_mcp():
    """Test MCP server locally."""
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "JIRA_URL": "https://royashish.atlassian.net",
        "JIRA_USERNAME": "royashish@gmail.com",
        "JIRA_API_TOKEN": "ATATT3xFfGF0ei2SBmhpyNuqHPg-VWc86WuuDl7fRQC7LVWKNlwd0RM5SCS7X2FvU0KtRd7M6yfbYl1fMP-WsxBVuIPjagHbava-z_ds7d8ofKOwYQP4GsdCCWxWpvF4SqpWQsBaUay8OboXlD1q1XhJOyWtHSh-2QvO2Vegm6es9oRNpxYqC6o=BCBFAD6C"
    })
    
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
        # Initialized notification
        {
            "jsonrpc": "2.0",
            "method": "initialized",
            "params": {}
        },
        # List tools
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        },
        # Call get_projects
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
    
    input_data = "\n".join(json.dumps(msg) for msg in messages) + "\n"
    
    print("🔧 Testing local MCP server...")
    
    try:
        process = subprocess.run(
            ["uv", "run", "python", "server.py"],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=30,
            env=env
        )
        
        print(f"📊 Exit code: {process.returncode}")
        
        if process.stdout:
            print("📥 STDOUT:")
            lines = process.stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            print(f"  ✅ Success: {response.get('method', 'response')}")
                            if response.get("id") == 2:  # tools/list response
                                tools = response.get("result", {}).get("tools", [])
                                print(f"     Found {len(tools)} tools")
                            elif response.get("id") == 3:  # get_projects response
                                print(f"     Projects call successful")
                        elif "error" in response:
                            print(f"  ❌ Error: {response['error']['message']}")
                        else:
                            print(f"  📝 {json.dumps(response, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"  📝 {line}")
        
        if process.stderr:
            print("⚠️  STDERR:")
            # Filter out build messages
            stderr_lines = [line for line in process.stderr.split('\n') 
                          if not any(x in line for x in ['Building', 'Built', 'Installed', 'package'])]
            if stderr_lines:
                print('\n'.join(stderr_lines))
        
        return process.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_local_mcp()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)