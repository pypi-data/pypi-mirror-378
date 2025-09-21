# MCP Proxy Adapter

**Author:** Vasiliy Zdanovskiy  
**Email:** vasilyvz@gmail.com

## Overview

MCP Proxy Adapter is a comprehensive framework for building JSON-RPC API servers with built-in security, SSL/TLS support, and proxy registration capabilities. It provides a unified interface for command execution, protocol management, and security enforcement.

## Features

- **JSON-RPC API**: Full JSON-RPC 2.0 support with built-in commands
- **Security Framework**: Integrated authentication, authorization, and SSL/TLS
- **Protocol Management**: HTTP, HTTPS, and mTLS protocol support
- **Proxy Registration**: Automatic registration with proxy servers
- **Command System**: Extensible command registry with built-in commands
- **Configuration Management**: Comprehensive configuration with environment variable overrides

## Quick Start

1. **Installation**:
   ```bash
   pip install mcp-proxy-adapter
   ```

2. **Basic Configuration**:
   ```bash
   # Use the comprehensive config with all options disabled by default
   python -m mcp_proxy_adapter --config config.json
   ```

3. **Access the API**:
   - Health check: `GET http://localhost:8000/health`
   - JSON-RPC: `POST http://localhost:8000/api/jsonrpc`
   - REST API: `POST http://localhost:8000/cmd`
   - Documentation: `http://localhost:8000/docs`

## Configuration

The adapter uses a comprehensive JSON configuration file (`config.json`) that includes all available options with sensible defaults. All features are disabled by default and can be enabled as needed:

- **Server settings**: Host, port, debug mode
- **Security**: Authentication methods, SSL/TLS, permissions
- **Protocols**: HTTP/HTTPS/mTLS configuration
- **Proxy registration**: Automatic server registration
- **Logging**: Comprehensive logging configuration
- **Commands**: Built-in and custom command management

See `docs/EN/configuration.md` for complete configuration documentation.

## Built-in Commands

- `health` - Server health check
- `echo` - Echo test command
- `config` - Configuration management
- `help` - Command help and documentation
- `reload` - Configuration reload
- `settings` - Settings management
- `load`/`unload` - Command loading/unloading
- `plugins` - Plugin management
- `proxy_registration` - Proxy registration control
- `transport_management` - Transport protocol management
- `role_test` - Role-based access testing

## Security Features

- **Authentication**: API keys, JWT tokens, certificate-based auth
- **Authorization**: Role-based permissions with wildcard support
- **SSL/TLS**: Full SSL/TLS and mTLS support
- **Rate Limiting**: Configurable request rate limiting
- **Security Headers**: Automatic security header injection

## Examples

The `mcp_proxy_adapter/examples/` directory contains comprehensive examples for different use cases:

- **Basic Framework**: Simple HTTP server setup
- **Full Application**: Complete application with custom commands and hooks
- **Security Testing**: Comprehensive security test suite
- **Certificate Generation**: SSL/TLS certificate management

## Development

The project follows a modular architecture:

- `mcp_proxy_adapter/api/` - FastAPI application and handlers
- `mcp_proxy_adapter/commands/` - Command system and built-in commands
- `mcp_proxy_adapter/core/` - Core functionality and utilities
- `mcp_proxy_adapter/config.py` - Configuration management

## License

This project is licensed under the MIT License.

## Support

For issues and questions, please contact vasilyvz@gmail.com.
