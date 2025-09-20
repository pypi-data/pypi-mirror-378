import os
import stat
import json
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
import base64
import hashlib

class ConfigManager:
    def __init__(self, app_name: str = "vior_secrets"):
        self.app_name = app_name
        
        # Get secure storage path based on OS
        self.config_path = self._get_config_storage_path()
        self._ensure_storage_directory()
        
        # Get or create a persistent encryption key
        self.cipher = self._get_or_create_cipher()
    
    def _get_config_storage_path(self) -> Path:
        """Get OS-specific config storage path"""
        if os.name == 'nt':  # Windows
            base_path = Path(os.getenv('LOCALAPPDATA', Path.home() / 'AppData' / 'Local'))
            return base_path / self.app_name
        
        elif os.uname().sysname == 'Darwin':  # macOS
            return Path.home() / 'Library' / 'Application Support' / self.app_name
        
        else:  # Linux and other Unix-like
            base_path = Path(os.getenv('XDG_CONFIG_HOME', Path.home() / '.config'))
            return base_path / self.app_name
    
    def _ensure_storage_directory(self):
        """Create storage directory with secure permissions"""
        try:
            self.config_path.mkdir(parents=True, exist_ok=True)
            
            # Set secure permissions on Unix-like systems
            if os.name != 'nt':
                self.config_path.chmod(stat.S_IRWXU)  # 700
                
        except Exception as e:
            raise Exception(f"Error creating config directory {self.config_path}: {e}")
    
    def _get_or_create_cipher(self):
        """Get or create a persistent encryption key"""
        key_file = self.config_path / '.key'
        
        try:
            if key_file.exists():
                # Load existing key
                key_data = key_file.read_bytes()
                key = base64.urlsafe_b64decode(key_data)
                return Fernet(key)
            else:
                # Create new key
                key = Fernet.generate_key()
                key_data = base64.urlsafe_b64encode(key)
                
                # Save key to file
                key_file.write_bytes(key_data)
                
                # Set secure file permissions
                if os.name != 'nt':
                    key_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
                
                return Fernet(key)
                
        except Exception as e:
            # Fallback to deterministic key generation based on machine info
            return self._create_deterministic_cipher()
    
    def _create_deterministic_cipher(self):
        """Create deterministic cipher based on machine characteristics"""
        try:
            # Create a deterministic key based on username and config path
            username = os.getenv('USERNAME', os.getenv('USER', 'default'))
            machine_info = f"{username}:{str(self.config_path)}:vior_secrets"
            
            # Generate key from machine info
            key_material = hashlib.sha256(machine_info.encode()).digest()
            key = base64.urlsafe_b64encode(key_material)
            
            return Fernet(key)
            
        except Exception as e:
            # Last resort: use a fixed key (less secure but functional)
            fixed_key = base64.urlsafe_b64encode(b'vior_secrets_fixed_key_32_byte!')
            return Fernet(fixed_key)
    
    def save_config(self, access_key: str, private_key: str, server_url: str = "http://localhost:8000") -> bool:
        """Save API keys and configuration"""
        try:
            config_data = {
                "access_key": access_key,
                "private_key": private_key,
                "server_url": server_url,
                "created_at": str(os.path.getmtime(__file__) if os.path.exists(__file__) else "unknown"),
                "version": "1.0"
            }
            
            # Encrypt the configuration
            json_string = json.dumps(config_data)
            encrypted_config = self.cipher.encrypt(json_string.encode()).decode()
            
            config_file = self.config_path / 'config'
            config_file.write_text(encrypted_config, encoding='utf-8')
            
            # Set secure file permissions
            if os.name != 'nt':
                config_file.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 600
            
            return True
            
        except Exception as e:
            return False
    
    def load_config(self) -> Optional[Dict]:
        """Load and decrypt configuration"""
        try:
            config_file = self.config_path / 'config'
            
            if not config_file.exists():
                return None
            
            encrypted_config = config_file.read_text(encoding='utf-8').strip()
            
            if not encrypted_config:
                return None
            
            decrypted_data = self.cipher.decrypt(encrypted_config.encode()).decode()
            config_data = json.loads(decrypted_data)
            return config_data
            
        except Exception as e:
            return None
    
    def clear_config(self) -> bool:
        """Clear stored configuration"""
        try:
            config_file = self.config_path / 'config'
            key_file = self.config_path / '.key'
            
            if config_file.exists():
                config_file.unlink()
            
            if key_file.exists():
                key_file.unlink()
            
            return True
            
        except Exception as e:
            return False
    
    def get_status(self) -> Dict:
        """Get configuration status"""
        config = self.load_config()
        
        return {
            "configured": config is not None,
            "config_path": str(self.config_path),
            "server_url": config.get("server_url") if config else None,
            "has_keys": bool(config and config.get("access_key") and config.get("private_key")) if config else False
        }

# Global config manager instance
config_manager = ConfigManager()