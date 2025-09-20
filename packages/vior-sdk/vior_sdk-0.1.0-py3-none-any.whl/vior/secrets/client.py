import subprocess
import requests
import json
from .exceptions import AuthenticationError, ConfigurationError, SecretNotFoundError

class SecretsClient:
    def __init__(self):
        self.config = None
        self.access_key = None
        self.private_key = None
        self.server_url = None
        
        self._load_config()
        self._test_api_access()
    
    def _load_config(self):
        try:
            result = subprocess.run(
                ['vior', 'sdk-need-auth'], 
                capture_output=True, 
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                error_msg = result.stdout.strip()
                if "No configuration found" in error_msg:
                    raise AuthenticationError("Configuration not found")
                raise AuthenticationError(f"CLI error: {error_msg}")
            
            self.config = json.loads(result.stdout.strip())
            self.access_key = self.config['access_key']
            self.private_key = self.config['private_key']
            self.server_url = self.config['server_url']
            
        except subprocess.TimeoutExpired:
            raise AuthenticationError("CLI timeout - not responding")
        except FileNotFoundError:
            raise ConfigurationError("Vior CLI not found")
        except json.JSONDecodeError:
            raise AuthenticationError("Invalid CLI response format")
        except AuthenticationError:
            raise
        except Exception as e:
            raise AuthenticationError(f"CLI error: {str(e)}")
    
    def _test_api_access(self):
        try:
            headers = {
                "X-Access-Key": self.access_key,
                "X-Private-Key": self.private_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.server_url}/auth/validate-api-keys",
                headers=headers,
                timeout=10
            )
            
            if response.status_code != 200:
                raise AuthenticationError(f"API access failed: {response.status_code}")
            
            result = response.json()
            if not result.get('valid'):
                raise AuthenticationError("API keys are invalid")
                
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"API connection failed: {str(e)}")
        except Exception as e:
            raise AuthenticationError(f"API validation error: {str(e)}")
    
    def get_secret(self, secret_name, format="dict"):
        """
        Retrieve a secret by name
        
        Args:
            secret_name (str): Name of the secret to retrieve
            format (str): Output format - "dict", "json", "env", or "raw"
        
        Returns:
            Secret data in the specified format
        """
        try:
            headers = {
                "X-Access-Key": self.access_key,
                "X-Private-Key": self.private_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.server_url}/secrets/view-sdk/{secret_name}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 404:
                raise SecretNotFoundError(secret_name)
            elif response.status_code != 200:
                raise Exception(f"Failed to retrieve secret: {response.status_code}")
            
            secret_data = response.json()
            entries = secret_data.get('entries', {})
            
            if format == "dict":
                return entries
            elif format == "json":
                return json.dumps(entries, indent=2)
            elif format == "env":
                return "\n".join([f"{key}={value}" for key, value in entries.items()])
            elif format == "raw":
                if len(entries) == 1:
                    return list(entries.values())[0]
                else:
                    return entries
            else:
                raise Exception(f"Invalid format: {format}. Use 'dict', 'json', 'env', or 'raw'")
                
        except SecretNotFoundError:
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
        except Exception as e:
            raise e
    
    def verify_connection(self):
        try:
            self._test_api_access()
            return {
                "status": "authenticated", 
                "message": "SDK successfully connected and API access verified",
                "server": self.server_url
            }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }
    
    def get_status(self):
        try:
            self._test_api_access()
            return f"Authenticated with API keys via {self.server_url}"
        except AuthenticationError as e:
            return f"Not authenticated: {str(e)}"