import requests
from typing import Dict, Optional
from config_manager import config_manager

class APIClient:
    def __init__(self):
        self.session = requests.Session()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers from stored config"""
        config = config_manager.load_config()
        if not config:
            raise Exception("No configuration found. Run 'vior configure' first.")
        
        return {
            "X-Access-Key": config["access_key"],
            "X-Private-Key": config["private_key"],
            "Content-Type": "application/json"
        }
    
    def _get_base_url(self) -> str:
        """Get server URL from config"""
        config = config_manager.load_config()
        if not config:
            raise Exception("No configuration found. Run 'vior configure' first.")
        
        return config["server_url"]
    
    def validate_keys(self) -> Dict:
        """Validate stored API keys with server"""
        try:
            url = f"{self._get_base_url()}/auth/validate"
            headers = self._get_headers()
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def get_user_info(self) -> Dict:
        """Get current user information"""
        try:
            url = f"{self._get_base_url()}/auth/me"
            headers = self._get_headers()
            
            response = self.session.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")

# Global API client instance
api_client = APIClient()