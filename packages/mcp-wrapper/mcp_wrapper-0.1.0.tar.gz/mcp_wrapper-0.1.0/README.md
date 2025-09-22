# Akto MCP Wrapper

A Model Context Protocol wrapper that supports threat detection, blocking, and tool discovery.

## Usage

Run the wrapper using the installed script:

```bash
akto-mcp-wrapper stdio --name <project-name> [--akto-api-token <token>] --exec '<command>'
```

Examples:

```bash
# 1) Run an MCP server from npm package
akto-mcp-wrapper stdio --name my-project --akto-api-token abc123 --exec 'npx -y your-mcp-server'

# 3) Run an MCP server via Docker
akto-mcp-wrapper stdio --name dockerized --akto-api-token $AKTO_API_TOKEN --exec 'docker run --rm -i yourorg/your-mcp-server:latest'
```
