"""
Vior Secrets CLI - Python3

Copyright (c) 2025 ViorCloud
Licensed under MIT License

A secure command-line interface for managing Vior Secrets API credentials.
Provides encrypted local storage of API keys and server configuration management.

Author: Viorcloud Team
Website: https://viorcloud.com
Version: 1.02
"""

import click
from .config_manager import config_manager
from .api_client import api_client
import json
import requests
import re
import base64
from urllib.parse import urlparse

@click.group()
@click.version_option(version="1.0.8", prog_name="vior-cli", message="%(prog)s/%(version)s Python")
def cli():
    pass

@cli.command()
@click.option('--access-key', prompt='Secret Access Key', help='Your secret access key (vsa_...)')
@click.option('--private-key', prompt='Secret Private Key', help='Your secret private key (vsp_...)')
@click.option('--server-url', default='https://secrets.sdk.viorcloud.com', help='Server URL')
def configure(access_key: str, private_key: str, server_url: str):
    status = config_manager.get_status()
    if status['configured']:
        config = config_manager.load_config()
        if config:
            access_key_display = config['access_key'][:5] + "*****" + config['access_key'][-2:]
            private_key_display = config['private_key'][:5] + "******" + config['private_key'][-2:]
            
            click.echo("Secrets are Already Configured")
            click.echo(f"Secret Access Key : {access_key_display}")
            click.echo(f"Secret Private Key: {private_key_display}")
            
            if not click.confirm('Do you want to reconfigure?'):
                click.echo("Configuration unchanged.")
                return
    
    access_key = access_key.strip()
    private_key = private_key.strip()
    
    click.echo(f"\nReceived keys:")
    click.echo(f"Access Key: {access_key[:12]}...{access_key[-8:] if len(access_key) > 20 else access_key}")
    click.echo(f"Private Key: {private_key[:12]}...{private_key[-8:] if len(private_key) > 20 else private_key}")
    click.echo(f"Server URL: {server_url}")
    
    if not access_key.startswith('vsa_'):
        click.echo("Error: Invalid access key format. Must start with 'vsa_'")
        return
    
    if not private_key.startswith('vsp_'):
        click.echo("Error: Invalid private key format. Must start with 'vsp_'")
        return
    
    if len(access_key) < 20 or len(private_key) < 20:
        click.echo("Warning: Keys seem unusually short. Are you sure they're correct?")
        if not click.confirm('Continue anyway?'):
            return
    
    click.echo("\nSaving configuration...")
    
    success = config_manager.save_config(access_key, private_key, server_url)
    
    if success:
        click.echo("Configuration saved successfully!")
        click.echo(f"Config location: {config_manager.config_path}")
        
        click.echo("\nValidating keys with server...")
        try:
            result = api_client.validate_keys()
            user_info = result.get('user', {})
            click.echo(f"Keys validated for user: {user_info.get('username')} ({user_info.get('email')})")
            click.echo("Setup complete! You can now use the CLI.")
        except Exception as e:
            click.echo(f"Configuration saved but validation failed: {str(e)}")
            click.echo("Make sure your server is running and keys are correct.")
    else:
        click.echo("Failed to save configuration")

@cli.command()
def reconfigure():
    current_status = config_manager.get_status()
    
    if current_status['configured']:
        click.echo("Current Configuration:")
        click.echo(f"Server URL: {current_status['server_url']}")
        click.echo(f"Config Path: {current_status['config_path']}")
        click.echo()
        
        if not click.confirm('Do you want to replace the current configuration?'):
            click.echo("Operation cancelled.")
            return
    
    click.echo("Enter your new API keys:")
    access_key = click.prompt('Secret Access Key (vsa_...)', type=str).strip()
    private_key = click.prompt('Secret Private Key (vsp_...)', type=str).strip()
    server_url = click.prompt('Server URL', default='https://secrets.sdk.viorcloud.com', type=str).strip()
    
    click.echo(f"\nKeys entered:")
    click.echo(f"Access Key: {access_key[:12]}...{access_key[-8:]}")
    click.echo(f"Private Key: {private_key[:12]}...{private_key[-8:]}")
    
    if click.confirm('Save this configuration?'):
        if not access_key.startswith('vsa_') or not private_key.startswith('vsp_'):
            click.echo("Error: Invalid key format!")
            return
        
        success = config_manager.save_config(access_key, private_key, server_url)
        
        if success:
            click.echo("Configuration updated successfully!")
            try:
                result = api_client.validate_keys()
                user_info = result.get('user', {})
                click.echo(f"Validated for user: {user_info.get('username')}")
            except Exception as e:
                click.echo(f"Validation failed: {str(e)}")
        else:
            click.echo("Failed to save configuration")

@cli.command()
def status():
    status = config_manager.get_status()
    
    click.echo("Vior Secrets Configuration Status")
    click.echo("-" * 40)
    click.echo(f"Configured: {'Yes' if status['configured'] else 'No'}")
    click.echo(f"Config Path: {status['config_path']}")
    click.echo(f"Server URL: {status['server_url'] or 'Not set'}")
    click.echo(f"Has API Keys: {'Yes' if status['has_keys'] else 'No'}")
    
    if status['configured']:
        click.echo("\nTesting connection...")
        try:
            result = api_client.validate_keys()
            user_info = result.get('user', {})
            click.echo(f"User: {user_info.get('username')} ({user_info.get('email')})")
            click.echo(f"User ID: {user_info.get('id')}")
            click.echo("API Keys: Valid")
        except Exception as e:
            click.echo("API Keys: Invalid")
            click.echo(f"Error: {str(e)}")
            click.echo("Try 'vior reconfigure' to fix this.")

@cli.command()
def server():
    status = config_manager.get_status()
    
    if not status['configured']:
        click.echo("No configuration found. Run 'vior configure' first.")
        return
    
    config = config_manager.load_config()
    current_url = config.get('server_url', 'Not set')
    
    click.echo(f"Server URL: {current_url}")
    
    click.echo("Testing server connection...")
    try:
        response = requests.get(f"{current_url}/auth/wh/return-verify", timeout=10)
        if response.status_code == 200:
            click.echo("Status: Connected")
        else:
            click.echo(f"Status: Server returned {response.status_code}")
    except Exception as e:
        click.echo(f"Status: Unable to connect - {str(e)}")
    
    click.echo()
    
    if click.confirm('Do you want to change the Server URL?'):
        new_url = click.prompt('Enter new Server URL', type=str).strip()
        
        if not _is_valid_url(new_url):
            click.echo("Error: Invalid URL format. Please use format: http://domain.com or http://domain.com:8080")
            return
        
        new_url = new_url.rstrip('/')
        
        click.echo(f"\nTesting new server: {new_url}")
        
        try:
            response = requests.get(f"{new_url}/auth/wh/return-verify", timeout=10)
            if response.status_code == 200:
                success = config_manager.save_config(
                    config['access_key'],
                    config['private_key'],
                    new_url
                )
                
                if success:
                    click.echo("URL Changed Successfully")
                else:
                    click.echo("Error: Failed to save new configuration")
            else:
                click.echo("Unable to Connect with Server please use valid Server URL")
        except Exception as e:
            click.echo("Unable to Connect with Server please use valid Server URL")

def _is_valid_url(url):
    url = url.rstrip('/')
    
    url_pattern = re.compile(
        r'^https?://'
        r'(?:'
        r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)*'
        r'[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?'
        r'|'
        r'localhost'
        r'|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        r')'
        r'(?::\d{2,5})?'
        r'/?$', re.IGNORECASE)
    
    if not url_pattern.match(url):
        return False
    
    try:
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and parsed.netloc
    except:
        return False

@cli.command()
def clear():
    status = config_manager.get_status()
    
    if not status['configured']:
        click.echo("No configuration found to clear.")
        return
    
    click.echo("Are you sure you want to clear all stored configurations? Doing so may cause instability in the existing codebase that relies on Vior Secrets, and those integrations may stop working. Proceed with caution before removing them.")
    
    if click.confirm(''):
        success = config_manager.clear_config()
        if success:
            click.echo("Configuration cleared successfully")
            click.echo("Use 'vior configure' to set up again.")
        else:
            click.echo("Failed to clear configuration")

@cli.command()
def validate():
    status = config_manager.get_status()
    
    if not status['configured']:
        click.echo("No configuration found. Run 'vior configure' first.")
        return
    
    click.echo("Validating API keys...")
    try:
        result = api_client.validate_keys()
        user_info = result.get('user', {})
        click.echo("API keys are valid!")
        click.echo(f"User: {user_info.get('username')} ({user_info.get('email')})")
        click.echo(f"User ID: {user_info.get('id')}")
        click.echo(f"Server: {status['server_url']}")
    except Exception as e:
        click.echo("API key validation failed!")
        click.echo(f"Error: {str(e)}")
        click.echo("Possible issues:")
        click.echo("   • Server is not running")
        click.echo("   • API keys are incorrect or expired")
        click.echo("   • Network connection issues")
        click.echo("   • Wrong server URL")

@cli.command(name='sdk-need-auth')
def sdk_need_auth():
    status = config_manager.get_status()
    
    if not status['configured']:
        click.echo("Error: No configuration found")
        exit(1)
    
    try:
        config = config_manager.load_config()
        if not config:
            click.echo("Error: Unable to load configuration")
            exit(1)
        
        output = {
            "access_key": config['access_key'],
            "private_key": config['private_key'], 
            "server_url": config['server_url']
        }
        
        click.echo(json.dumps(output))
        exit(0)
    except Exception as e:
        click.echo(f"Error: {str(e)}")
        exit(1)

@cli.command()
def show():
    status = config_manager.get_status()
    
    if not status['configured']:
        click.echo("No configuration found.")
        return
    
    config = config_manager.load_config()
    
    if config:
        click.echo("Current Configuration:")
        click.echo("-" * 30)
        click.echo(f"Server URL: {config['server_url']}")
        click.echo(f"Config Path: {status['config_path']}")
        
        access_key = config['access_key']
        private_key = config['private_key']
        
        click.echo(f"Access Key: {access_key[:12]}...{access_key[-8:]}")
        click.echo(f"Private Key: {private_key[:12]}...{private_key[-8:]}")
        
        click.echo("\nUse 'vior validate' to test these keys.")

@cli.command()
def info():
    click.echo("Vior Secrets CLI - Configuration Tool")
    click.echo("=" * 40)
    click.echo()
    click.echo("This CLI tool helps you configure API keys for accessing")
    click.echo("the Vior Secrets service. Your credentials are stored")
    click.echo("securely on your local machine.")
    click.echo()
    click.echo("Available Commands:")
    click.echo("  configure        - Set up API keys (first time setup)")
    click.echo("  reconfigure      - Change existing configuration")
    click.echo("  status           - Show configuration status")
    click.echo("  validate         - Test your API keys")
    click.echo("  show             - Display current config (keys masked)")
    click.echo("  server           - Show and manage server URL")
    click.echo("  clear            - Remove all configuration")
    click.echo("  sdk-need-auth    - Provide SDK authentication data")
    click.echo("  info             - Show this help information")
    click.echo()
    click.echo("Powered by Python3 & Made by Viorcloud")

if __name__ == '__main__':
    cli()