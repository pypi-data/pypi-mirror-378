#!/usr/bin/env python3
"""Test Docker MCP server with correct protocol."""

import json
import subprocess
import sys
import time

def test_docker_mcp():
    """Test Docker MCP server with proper protocol."""
    
    docker_cmd = [
        "docker", "run", "-i", "--rm",
        "-e", "JIRA_URL=https://royashish.atlassian.net",
        "-e", "JIRA_USERNAME=royashish@gmail.com", 
        "-e", "JIRA_API_TOKEN=ATATT3xFfGF0ei2SBmhpyNuqHPg-VWc86WuuDl7fRQC7LVWKNlwd0RM5SCS7X2FvU0KtRd7M6yfbYl1fMP-WsxBVuIPjagHbava-z_ds7d8ofKOwYQP4GsdCCWxWpvF4SqpWQsBaUay8OboXlD1q1XhJOyWtHSh-2QvO2Vegm6es9oRNpxYqC6o=BCBFAD6C",
        "royashish/jira-mcp-server:latest"
    ]
    
    # Correct MCP protocol messages
    messages = [
        # 1. Initialize
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
        # 2. Initialized notification (correct method name)
        json.dumps({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }),
        # 3. List tools
        json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }),
        # 4. Call get_projects
        json.dumps({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_projects",
                "arguments": {}
            }
        })
    ]
    
    input_data = "\n".join(messages) + "\n"
    
    print("🔧 Testing Docker MCP server with correct protocol...")
    print(f"📤 Sending {len(messages)} messages")
    
    try:
        process = subprocess.run(
            docker_cmd,
            input=input_data,
            text=True,
            capture_output=True,
            timeout=45
        )
        
        print(f"📊 Exit code: {process.returncode}")
        
        if process.stdout:
            print("📥 STDOUT:")
            lines = process.stdout.strip().split('\n')
            for i, line in enumerate(lines, 1):
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "result" in response:
                            if response.get("id") == 1:
                                print(f"  ✅ [{i}] Initialization successful")
                                server_info = response["result"].get("serverInfo", {})
                                print(f"      Server: {server_info.get('name')} v{server_info.get('version')}")
                            elif response.get("id") == 2:
                                tools = response["result"].get("tools", [])
                                print(f"  ✅ [{i}] Found {len(tools)} tools")
                                if tools:
                                    print(f"      Sample tools: {', '.join([t.get('name', 'unknown') for t in tools[:3]])}...")
                            elif response.get("id") == 3:
                                print(f"  ✅ [{i}] get_projects call successful")
                                # Try to parse the result
                                result = response.get("result", [])
                                if result and isinstance(result, list) and len(result) > 0:
                                    content = result[0].get("text", "")
                                    if content:
                                        try:
                                            projects_data = json.loads(content)
                                            projects = projects_data.get("projects", [])
                                            print(f"      Found {len(projects)} JIRA projects")
                                            if projects:
                                                print(f"      Sample: {projects[0].get('key')} - {projects[0].get('name')}")
                                        except:
                                            print(f"      Response: {content[:100]}...")
                            else:
                                print(f"  ✅ [{i}] Response ID {response.get('id')}")
                        elif "error" in response:
                            error = response["error"]
                            print(f"  ❌ [{i}] Error {error.get('code')}: {error.get('message')}")
                        else:
                            print(f"  📝 [{i}] {json.dumps(response, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"  📝 [{i}] {line}")
        
        if process.stderr:
            print("⚠️  STDERR:")
            print(process.stderr)
        
        # Check if we got successful responses
        success = process.returncode == 0 and "get_projects call successful" in process.stdout
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ Timeout - container took too long")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_docker_mcp()
    print(f"\n{'🎉 DOCKER IMAGE VALIDATION SUCCESSFUL!' if success else '❌ DOCKER IMAGE VALIDATION FAILED'}")
    
    if success:
        print("\n✅ Docker image is working correctly:")
        print("   • MCP protocol initialization ✓")
        print("   • Tools listing ✓") 
        print("   • JIRA API connection ✓")
        print("   • Project data retrieval ✓")
    
    sys.exit(0 if success else 1)