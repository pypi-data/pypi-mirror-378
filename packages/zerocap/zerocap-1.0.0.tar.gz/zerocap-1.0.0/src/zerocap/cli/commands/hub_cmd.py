# src/zerocap/cli/commands/hub_cmd.py
"""
CLI commands for interacting with the Zerocap Hub.
"""
import typer
from zerocap.daemon import hub_client

app = typer.Typer(help="View hub status and discover registered services.")

@app.command()
def status():
    """
    Show the status of the local hubs and everything they know about.
    """
    print("🔎 Querying Zerocap Hub for status...")
    try:
        hub_data = hub_client.get_hub_status()
        
        print("\n--- 🟢 MCP Servers ---")
        mcp_servers = hub_data.get("mcp_servers", {})
        if not mcp_servers:
            print("No MCP Servers registered.")
        else:
            for name, info in mcp_servers.items():
                address = info.get('address', 'N/A')
                tool_count = len(info.get('manifest', {}).get('tools', []))
                print(f"  - {name}")
                print(f"    - Address: {address}")
                print(f"    - Tools: {tool_count}")

        print("\n--- 🔵 ACP Agents ---")
        acp_agents = hub_data.get("acp_agents", {})
        if not acp_agents:
            print("No ACP Agents registered.")
        else:
            for name, info in acp_agents.items():
                address = info.get('address', 'N/A')
                capabilities = info.get('manifest', {}).get('capabilities', [])
                print(f"  - {name}")
                print(f"    - Address: {address}")
                print(f"    - Capabilities: {', '.join(capabilities)}")

    except ConnectionError as e:
        print(f"\n❌ Error: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")