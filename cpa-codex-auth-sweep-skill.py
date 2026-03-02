#!/usr/bin/env python3
"""
AI Agent Skill Server for Codex Auth Scanner (scanner.py).
This server exposes a tool that allows AI models to directly discover, analyze,
and optionally delete Codex authentication files.
Uses the MCP (Model Context Protocol) SDK internally for stdio transport.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Uses the MCP SDK for stdio-based AI tool serving.
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: The 'mcp' package is required. Install with 'pip install mcp'")
    sys.exit(1)


# The path to our optimized scanner script
TP_SCRIPT_PATH = Path(__file__).parent / "scanner.py"

server = Server("codex-auth-sweep-skill")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Expose the scan_auth_files tool to the AI."""
    return [
        Tool(
            name="scan_codex_auths",
            description="""Scan the local Codex authentication directory for valid/invalid/quota-exceeded tokens.
Can optionally delete tokens that returned HTTP 401 Unauthorized.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "auth_dir": {
                        "type": "string",
                        "description": "Directory containing the auth JSON files. Defaults to ~/.cli-proxy-api."
                    },
                    "delete_401": {
                        "type": "boolean",
                        "description": "If true, permanently delete files that return HTTP 401 Unauthorized."
                    },
                    "no_quarantine": {
                        "type": "boolean",
                        "description": "If true, do NOT move quota-exceeded files into an 'exceeded' subfolder (Recommended true for read-only)."
                    }
                },
                "required": []
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute the scanner as a subprocess returning JSON."""
    if name != "scan_codex_auths":
        raise ValueError(f"Unknown tool: {name}")

    if not TP_SCRIPT_PATH.exists():
        return [TextContent(type="text", text=f"Scanner script missing at {TP_SCRIPT_PATH}")]

    args = arguments or {}
    auth_dir = args.get("auth_dir")
    delete_401 = args.get("delete_401", False)
    no_quarantine = args.get("no_quarantine", True)

    # Build the command payload
    cmd = [sys.executable, str(TP_SCRIPT_PATH), "--output-json"]
    
    if auth_dir:
        cmd.extend(["--auth-dir", str(auth_dir)])
    
    if no_quarantine:
        cmd.append("--no-quarantine")
        
    if delete_401:
        cmd.extend(["--delete-401", "--yes"])

    # Launch scanner.py in an isolated headless process to avoid stdio corruption
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    
    if process.returncode != 0 and process.returncode != 1:
        # Exit code 1 means 401s were found, which is normal. Other codes are failures.
        err_msg = stderr.decode('utf-8', errors='replace').strip()
        out_msg = stdout.decode('utf-8', errors='replace').strip()
        return [TextContent(type="text", text=f"Scanner failed (exit code {process.returncode}):\n{err_msg}\n{out_msg}")]

    # Parse JSON stdout
    try:
        raw_output = stdout.decode('utf-8', errors='replace')
        # We only want the JSON output, sometimes there might be other unexpected prints. 
        # Attempting to load everything as JSON.
        result_payload = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        return [TextContent(type="text", text=f"Failed to parse scanner JSON output: {exc}\nRaw output:\n{stdout.decode('utf-8')}")]

    # Assemble a helpful markdown report for the AI
    results = result_payload.get("results", [])
    deletion = result_payload.get("deletion", {})
    
    total = len(results)
    unauth = sum(1 for r in results if r.get("unauthorized_401"))
    exceeded = sum(1 for r in results if r.get("quota_exceeded") and not r.get("unauthorized_401"))
    ok_count = sum(1 for r in results if r.get("status_code") is not None and 200 <= r.get("status_code", 0) < 300)
    
    report_lines = [
        "## Codex Auth Scan Report",
        f"- **Total Files Scanned**: {total}",
        f"- **Valid (200 OK)**: {ok_count}",
        f"- **Unauthorized (401)**: {unauth}",
        f"- **Quota Exceeded (429/LIM)**: {exceeded}",
        f"- **Others/Errors**: {total - ok_count - unauth - exceeded}"
    ]
    
    if deletion.get("requested"):
        deleted_count = deletion.get("deleted_count", 0)
        report_lines.append("")
        report_lines.append("### Deletion Action")
        report_lines.append(f"- `delete_401` was **ENABLED**.")
        report_lines.append(f"- Successfully removed **{deleted_count}** expired credentials.")
        
        errors = deletion.get("errors", [])
        if errors:
            report_lines.append(f"- Could not delete {len(errors)} files due to disk errors.")

    return [TextContent(type="text", text="\n".join(report_lines))]


async def main():
    # Run the skill server loop using MCP stdio transport
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

def main_sync():
    """Synchronous entry point for package console scripts."""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()
