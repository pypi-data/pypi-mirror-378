import requests
import json
import os
from typing import Dict, Optional
from datetime import datetime

class FragmentAPI:
    """Client for interacting with the Fragment API."""
    
    def __init__(self, base_url: str = "https://fragment.starsgrace.ru"):
        """Initialize the Fragment API client.
        
        Args:
            base_url (str): Base URL of the Fragment API (default: https://fragment.starsgrace.ru)
        """
        self.base_url = base_url.rstrip('/')
        self.auth_key: Optional[str] = None
        self.session = requests.Session()
        self.session_file = "fragment_session.json"

    def _print_response(self, response: requests.Response, method: str, url: str) -> None:
        """Helper method to print full server response details.
        
        Args:
            response: The HTTP response object
            method: HTTP method (e.g., GET, POST)
            url: The URL of the request
        """
        print(f"\n--- API Request: {method} {url} ---")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        try:
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
        except ValueError:
            print(f"Response Body (raw): {response.text}")
        print("--- End of Response ---\n")

    def _handle_request(self, method: str, url: str, **kwargs) -> Dict:
        """Helper method to make HTTP requests and handle responses.
        
        Args:
            method: HTTP method (e.g., 'get', 'post')
            url: The URL to send the request to
            **kwargs: Additional arguments for the request (e.g., json, params)
            
        Returns:
            Dict: Parsed JSON response
            
        Raises:
            requests.exceptions.RequestException: For any request failure
        """
        try:
            response = getattr(self.session, method)(url, **kwargs)
            self._print_response(response, method.upper(), url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error occurred: {e}")
            print(f"Response details:")
            self._print_response(e.response, method.upper(), url)
            raise
        except requests.exceptions.RequestException as e:
            print(f"Request Error occurred: {e}")
            raise

    def create_auth(self, wallet_mnemonic: str, cookies: str, hash_value: str) -> Dict:
        """Create a new authentication session.
        
        Args:
            wallet_mnemonic (str): Wallet mnemonic phrase
            cookies (str): Session cookies
            hash_value (str): Hash value for authentication
            
        Returns:
            Dict: Response containing auth_key and timestamps
        """
        payload = {
            "wallet_mnemonic": wallet_mnemonic,
            "cookies": cookies,
            "hash": hash_value
        }
        url = f"{self.base_url}/create_auth"
        result = self._handle_request("post", url, json=payload)
        
        if result.get("ok") and result.get("auth_key"):
            self.auth_key = result["auth_key"]
            self.save_session()
            
        return result

    def save_session(self, filename: Optional[str] = None) -> bool:
        """Save current session to file.
        
        Args:
            filename (str, optional): Filename to save session. Uses default if not specified.
            
        Returns:
            bool: True if session was saved successfully, False otherwise
        """
        if not self.auth_key:
            return False
            
        session_data = {
            "auth_key": self.auth_key,
            "base_url": self.base_url,
            "saved_at": datetime.now().isoformat()
        }
        
        try:
            file_path = filename or self.session_file
            with open(file_path, 'w') as f:
                json.dump(session_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving session: {e}")
            return False

    def load_session(self, filename: Optional[str] = None) -> bool:
        """Load session from file.
        
        Args:
            filename (str, optional): Filename to load session from. Uses default if not specified.
            
        Returns:
            bool: True if session was loaded successfully, False otherwise
        """
        try:
            file_path = filename or self.session_file
            if not os.path.exists(file_path):
                return False
                
            with open(file_path, 'r') as f:
                session_data = json.load(f)
                
            self.auth_key = session_data.get("auth_key")
            if "base_url" in session_data:
                self.base_url = session_data["base_url"]
                
            return self.auth_key is not None
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return False

    def delete_session(self, filename: Optional[str] = None) -> bool:
        """Delete saved session file.
        
        Args:
            filename (str, optional): Filename to delete. Uses default if not specified.
            
        Returns:
            bool: True if session was deleted successfully, False otherwise
        """
        try:
            file_path = filename or self.session_file
            if os.path.exists(file_path):
                os.remove(file_path)
                self.auth_key = None
                return True
            return False
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def has_valid_session(self) -> bool:
        """Check if there's a valid session available.
        
        Returns:
            bool: True if auth_key is set, False otherwise
        """
        return self.auth_key is not None

    def get_balance(self) -> Dict:
        """Get wallet balance.
        
        Returns:
            Dict: Response containing balance information
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        url = f"{self.base_url}/balance/{self.auth_key}"
        return self._handle_request("get", url)

    def buy_stars(self, username: str, quantity: Optional[int] = 50, show_sender: Optional[bool] = False) -> Dict:
        """Buy Telegram Stars for a specified user.
        
        Args:
            username (str): Target username (with @ prefix)
            quantity (int, optional): Number of stars to buy (default: 50)
            show_sender (bool, optional): Whether to show sender information (default: False)
            
        Returns:
            Dict: Response containing transaction details
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        payload = {
            "username": username,
            "quantity": quantity,
            "show_sender": show_sender
        }
        
        url = f"{self.base_url}/buy_stars/{self.auth_key}"
        return self._handle_request("post", url, json=payload)

    def gift_premium(self, username: str, months: Optional[int] = 3, show_sender: Optional[bool] = False) -> Dict:
        """Gift Telegram Premium to a specified user.
        
        Args:
            username (str): Target username (with @ prefix)
            months (int, optional): Number of months for premium gift (default: 3)
            show_sender (bool, optional): Whether to show sender information (default: False)
            
        Returns:
            Dict: Response containing transaction details
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        payload = {
            "username": username,
            "months": months,
            "show_sender": show_sender
        }
        
        url = f"{self.base_url}/gift_premium/{self.auth_key}"
        return self._handle_request("post", url, json=payload)

    def topup_ton(self, username: str, amount: int, show_sender: Optional[bool] = False) -> Dict:
        """Top up TON for a specified user.
        
        Args:
            username (str): Target username (with @ prefix)
            amount (int): Amount in TON to top up
            show_sender (bool, optional): Whether to show sender information (default: False)
            
        Returns:
            Dict: Response containing transaction details
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        payload = {
            "username": username,
            "amount": amount,
            "show_sender": show_sender
        }
        
        url = f"{self.base_url}/topup_ton/{self.auth_key}"
        return self._handle_request("post", url, json=payload)

    def get_user_stars(self, username: str) -> Dict:
        """Search user for Telegram Stars transactions.
        
        Args:
            username (str): Target username (with @ prefix)
            
        Returns:
            Dict: Response containing user information
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        payload = {"username": username}
        url = f"{self.base_url}/get_user_stars/{self.auth_key}"
        return self._handle_request("post", url, json=payload)

    def get_user_premium(self, username: str) -> Dict:
        """Search user for Telegram Premium transactions.
        
        Args:
            username (str): Target username (with @ prefix)
            
        Returns:
            Dict: Response containing user information
            
        Raises:
            ValueError: If auth_key is not set
        """
        if not self.auth_key:
            raise ValueError("Authentication key not set. Please create_auth first.")
            
        payload = {"username": username}
        url = f"{self.base_url}/get_user_premium/{self.auth_key}"
        return self._handle_request("post", url, json=payload)

    def health_check(self) -> Dict:
        """Check API health status.
        
        Returns:
            Dict: Response containing health status and timestamp
        """
        url = f"{self.base_url}/health"
        return self._handle_request("get", url)

    def close(self):
        """Close the session."""
        self.session.close()
        self.auth_key = None