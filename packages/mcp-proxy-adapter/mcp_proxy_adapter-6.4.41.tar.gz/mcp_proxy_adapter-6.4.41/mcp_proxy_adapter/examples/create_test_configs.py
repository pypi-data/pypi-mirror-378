#!/usr/bin/env python3
"""
Test Configuration Generator
Creates test configurations by copying the comprehensive config and enabling/disabling specific options.
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


class TestConfigGenerator:
    """Generator for test configurations based on comprehensive config."""

    def __init__(self, comprehensive_config_path: str, output_dir: str = "configs"):
        """
        Initialize the generator.
        
        Args:
            comprehensive_config_path: Path to the comprehensive configuration file
            output_dir: Directory to output test configurations
        """
        self.comprehensive_config_path = Path(comprehensive_config_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Load the comprehensive config
        with open(self.comprehensive_config_path, 'r', encoding='utf-8') as f:
            self.base_config = json.load(f)

    def create_config(self, name: str, modifications: Dict[str, Any]) -> Path:
        """
        Create a test configuration with specific modifications.
        
        Args:
            name: Name of the configuration (without .json extension)
            modifications: Dictionary of modifications to apply
            
        Returns:
            Path to the created configuration file
        """
        # Deep copy the base config
        config = json.loads(json.dumps(self.base_config))
        
        # Apply modifications
        for key, value in modifications.items():
            self._set_nested_value(config, key, value)
        
        # Save the configuration
        output_path = self.output_dir / f"{name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Created test config: {output_path}")
        return output_path

    def _set_nested_value(self, config: Dict, key: str, value: Any):
        """Set a nested value in the configuration using dot notation."""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value

    def create_all_test_configs(self):
        """Create all standard test configurations."""
        print("🔧 Creating test configurations from comprehensive config...")
        
        # 1. HTTP Simple
        self.create_config("http_simple", {
            "server.port": 20020,  # Dedicated port for basic_http
            "ssl.enabled": False,
            "security.enabled": False,
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["http"],
            "protocols.default_protocol": "http"
        })
        
        # 2. HTTP with Auth (renamed to http_token for security tests)
        self.create_config("http_token", {
            "server.port": 20021,  # Dedicated port for http_token
            "ssl.enabled": False,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["api_key"],
            "security.auth.api_keys": {
                "admin": "admin-secret-key",
                "user": "user-secret-key"
            },
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["http"],
            "protocols.default_protocol": "http"
        })
        
        # 3. HTTPS Simple
        self.create_config("https_simple", {
            "server.port": 20022,  # Dedicated port for https
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/server_key.pem",
            "security.enabled": False,
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["https"],
            "protocols.default_protocol": "https"
        })
        
        # 4. HTTPS with Auth (renamed to https_token for security tests)
        self.create_config("https_token", {
            "server.port": 20023,  # Dedicated port for https_token
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/server_key.pem",
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["api_key"],
            "security.auth.api_keys": {
                "admin": "admin-secret-key",
                "user": "user-secret-key"
            },
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["https"],
            "protocols.default_protocol": "https"
        })
        
        # 5. mTLS Simple
        self.create_config("mtls_simple", {
            "server.port": 20025,  # Different port for mtls_simple
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/server_key.pem",
            "ssl.ca_cert": "certs/mcp_proxy_adapter_ca_ca.crt",
            "ssl.verify_client": True,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["certificate"],
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["https", "mtls"],
            "protocols.default_protocol": "mtls"
        })
        
        # 6. mTLS with Roles
        self.create_config("mtls_with_roles", {
            "server.port": 20026,  # Different port for mtls_with_roles
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/server_key.pem",
            "ssl.ca_cert": "certs/mcp_proxy_adapter_ca_ca.crt",
            "ssl.verify_client": True,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["certificate"],
            "security.permissions.enabled": True,
            "security.permissions.roles_file": "configs/roles.json",
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["https", "mtls"],
            "protocols.default_protocol": "mtls"
        })
        
        # 6a. mTLS without Roles (for security tests)
        self.create_config("mtls_no_roles", {
            "server.port": 20024,  # Dedicated port for mtls
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/server_key.pem",
            "ssl.ca_cert": "certs/mcp_proxy_adapter_ca_ca.crt",
            "ssl.verify_client": True,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["certificate"],
            "security.permissions.enabled": False,
            "proxy_registration.enabled": False,
            "protocols.allowed_protocols": ["https", "mtls"],
            "protocols.default_protocol": "mtls"
        })
        
        # 7. mTLS with Proxy Registration
        self.create_config("mtls_with_proxy", {
            "server.port": 8007,
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/localhost_server.key",
            "ssl.ca_cert": "certs/mcp_proxy_adapter_ca_ca.crt",
            "ssl.verify_client": True,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["certificate"],
            "proxy_registration.enabled": True,
            "proxy_registration.proxy_url": "http://127.0.0.1:3006",
            "proxy_registration.server_id": "mcp_test_server",
            "proxy_registration.server_name": "MCP Test Server",
            "protocols.allowed_protocols": ["https", "mtls"]
        })
        
        # 8. HTTP with Token Auth (for security tests) - REMOVED DUPLICATE
        # This is already created above with correct port 20021
        
        # 9. HTTPS with Token Auth (for security tests) - REMOVED DUPLICATE  
        # This is already created above with correct port 20023
        
        # 10. Full Featured (everything enabled)
        self.create_config("full_featured", {
            "server.port": 8008,
            "ssl.enabled": True,
            "ssl.cert_file": "certs/localhost_server.crt",
            "ssl.key_file": "keys/localhost_server.key",
            "ssl.ca_cert": "certs/mcp_proxy_adapter_ca_ca.crt",
            "ssl.verify_client": True,
            "security.enabled": True,
            "security.auth.enabled": True,
            "security.auth.methods": ["certificate", "api_key"],
            "security.auth.api_keys": {
                "admin": "admin-secret-key",
                "user": "user-secret-key"
            },
            "security.permissions.enabled": True,
            "security.permissions.roles_file": "configs/roles.json",
            "security.rate_limit.enabled": True,
            "proxy_registration.enabled": True,
            "proxy_registration.proxy_url": "http://127.0.0.1:3006",
            "proxy_registration.server_id": "mcp_full_server",
            "proxy_registration.server_name": "MCP Full Featured Server",
            "protocols.allowed_protocols": ["http", "https", "mtls", "jsonrpc"]
        })
        
        print(f"✅ Created {10} test configurations in {self.output_dir}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test configurations")
    parser.add_argument(
        "--comprehensive-config", 
        default="comprehensive_config.json",
        help="Path to comprehensive configuration file"
    )
    parser.add_argument(
        "--output-dir",
        default="configs",
        help="Output directory for test configurations"
    )
    parser.add_argument(
        "--config-name",
        help="Create a specific configuration (http_simple, https_auth, mtls_with_roles, etc.)"
    )
    parser.add_argument(
        "--modifications",
        help="JSON string of modifications to apply (for custom configs)"
    )
    
    args = parser.parse_args()
    
    generator = TestConfigGenerator(args.comprehensive_config, args.output_dir)
    
    if args.config_name:
        # Create a specific configuration
        if args.modifications:
            modifications = json.loads(args.modifications)
        else:
            # Use predefined modifications
            predefined = {
                "http_simple": {"server.port": 8001, "ssl.enabled": False, "security.enabled": False},
                "https_simple": {"server.port": 8003, "ssl.enabled": True},
                "mtls_simple": {"server.port": 8005, "ssl.enabled": True, "ssl.verify_client": True},
            }
            modifications = predefined.get(args.config_name, {})
        
        generator.create_config(args.config_name, modifications)
    else:
        # Create all test configurations
        generator.create_all_test_configs()


if __name__ == "__main__":
    main()
