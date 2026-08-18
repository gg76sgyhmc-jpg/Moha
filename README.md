# Moha

## MCP servers

This project ships a [21st.dev](https://21st.dev) MCP server in `.mcp.json`.

The config reads the API key from the environment rather than storing it in the
repo, so export it before starting Claude Code:

```bash
export API_KEY_21ST="your-21st-api-key"
```

Claude Code asks for approval the first time it loads a project-scoped MCP
server. Confirm the prompt, then check the connection with:

```bash
claude mcp list
```
