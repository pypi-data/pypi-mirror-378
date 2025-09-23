# Data Intelligence MCP Server

This project provides a modular, scalable Model Context Protocol (MCP) server designed for extensibility. It features a decorator-based registration system and a developer CLI to streamline the creation and management of new services and tools.


```mermaid
flowchart LR
    github["data-intelligence-mcp Github"] -- publish --> registry
    registry["PyPi registry"] -- pip install data-intelligence-mcp-server--> server
    subgraph MCP Host
        client["MCP Client"] <-- MCP/STDIO --> server("Data Intelligence MCP Server")
    end
    server -- HTTPS --> runtime("IBM Data Intelligence")
    subgraph id["Services"]
        runtime
    end
    client <-- MCP/HTTP --> server2("DI MCP Server") -- HTTPS --> runtime

```
---

## Table of Contents

1. [Quick Install - PyPI](#quick-install---pypi)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
2. [Server](#server)
   - [HTTP Mode](#http-mode)
   - [HTTPS Mode](#https-mode)
3. [Client Configuration](#client-configuration)
   - [Claude Desktop](#claude-desktop)
     - [stdio (Recommended for local setup)](#stdio-recommended-for-local-setup)
     - [http/https (Remote setup)](#httphttps-remote-setup)
   - [VS Code Copilot](#vs-code-copilot)
     - [stdio (Recommended for local setup)](#stdio-recommended-for-local-setup-1)
     - [http/https (Remote setup)](#httphttps-remote-setup-1)
   - [Watsonx Orchestrate](#watsonx-orchestrate)
4. [Configuration](#configuration)
   - [Client Settings](#client-settings)
   - [SSL/TLS Configuration](#ssltls-configuration)

---

## Quick Install - PyPI

### Prerequisites
- Python 3.11 or higher

### Installation

#### Standard Installation

Use pip/pip3 for standard installation with colon-separated tool names:
```bash
pip install data-intelligence-mcp-server
```
---

## Server

If you have installed the data-intelligence-mcp-server locally on your host machine and want to connect from a client such as Claude, Copilot, or LMStudio, you can use the stdio mode as described in the examples under the [Client Configuration](#client-configuration) section.

The server can also be configured and run in http/https mode.

### HTTP Mode
```bash
data-intelligence-mcp-server --transport http --host 0.0.0.0 --port 3000
```

### HTTPS Mode
Refer to [server_https.md](server_https.md) for detailed HTTPS server configuration and setup.

---

## Client Configuration

If data-intelligence-mcp-server is installed on local host machine, then it's recommended to use stdio mode. Use https mode if it has been set up remotely.

### Claude Desktop

#### stdio (Recommended for local setup)
To run the server in stdio mode, make sure server is installed locally using [PyPI](#quick-install---pypi).

Add the MCP server to your Claude Desktop configuration:
```json
{
  "mcpServers": {
    "wxdi-mcp-server": {
      "command": "data-intelligence-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
         "DI_SERVICE_URL": "https://api.dataplatform.cloud.ibm.com",
         "DI_APIKEY": "<data intelligence api key>",
         "ENV_MODE": "SaaS"
      }
    }
  }
}
```

#### http/https (Remote setup)
If the MCP server is running on a local/remote server in http/https mode.

For Cloud SaaS:
```json
{
  "mcpServers": {
    "wxdi-mcp-server": {
      "url": "<url_to_mcp_server>",
      "type": "http",
      "headers": {
        "X-API-KEY": "your api key from cloud SaaS"
      }
    }
  }
}
```

For CPD:
```json
{
  "mcpServers": {
    "wxdi-mcp-server": {
      "url": "<url_to_mcp_server>",
      "type": "http",
      "headers": {
        "X-API-KEY": "your api key from cpd env",
        "USERNAME": "<user name from cpd env>"
      }
    }
  }
}
```

### VS Code Copilot

#### stdio (Recommended for local setup)
To run the server in stdio mode, make sure server is installed locally using [PyPI](#quick-install---pypi).

Add the MCP server to your VS Code Copilot MCP configuration:
```json
{
  "servers": {
    "wxdi-mcp-server": {
      "command": "data-intelligence-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
         "DI_SERVICE_URL": "https://api.dataplatform.cloud.ibm.com",
         "DI_APIKEY": "<data intelligence api key>",
         "ENV_MODE": "SaaS"
      }
    }
  }
}
```

#### http/https (Remote setup)
If the MCP server is running on a local/remote server in http/https mode.

For Cloud SaaS:
```json
{
  "servers": {
    "wxdi-mcp-server": {
      "url": "<url_to_mcp_server>",
      "type": "http",
      "headers": {
        "X-API-KEY": "your api key from cloud SaaS"
      }
    }
  }
}
```

For CPD:
```json
{
  "servers": {
    "wxdi-mcp-server": {
      "url": "<url_to_mcp_server>",
      "type": "http",
      "headers": {
        "X-API-KEY": "your api key for cpd env",
        "USERNAME": "<user name from cpd env>"
      }
    }
  }
}
```

### Watsonx Orchestrate
**Work in Progress**

---
## Configuration

The MCP server can be configured using environment variables or a `.env` file. Copy `.env.example` to `.env` and modify the values as needed.

### Client Settings

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `DI_SERVICE_URL` | `None` | Base URL for Watsonx Data Intelligence instance |
| `DI_AUTH_TOKEN` | `None` | Bearer token for stdio mode (optional) |
| `DI_APIKEY` | `None` | API key for authentication |
| `DI_USERNAME` | `None` | Username (required when using API key for CPD) |
| `ENV_MODE` | `SaaS` | Environment mode (`SaaS` or `CPD`) |
| `REQUEST_TIMEOUT_S` | `30` | HTTP request timeout in seconds |


### SSL/TLS Configuration

If running in CPD environment, you might need to configure SSL certificate for client connection. Please look into [SSL_CERTIFICATE_GUIDE.md](SSL_CERTIFICATE_GUIDE.md) for more details.
