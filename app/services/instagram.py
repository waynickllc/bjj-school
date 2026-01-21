"""
Instagram Service

This module provides the InstagramService class for fetching photos
from the Instagram Graph API.
Will be implemented in task 4.1.
"""

import requests
from typing import List, Dict


class InstagramAPIError(Exception):
    """Exception raised for Instagram API errors"""
    pass


class InstagramService:
    """
    Service for interacting with Instagram Graph API.
    
    Attributes:
        access_token: Instagram API access token
        user_id: Instagram user ID
    """
    
    def __init__(self, access_token: str, user_id: str):
        """
        Initialize InstagramService with credentials.
        
        Args:
            access_token: Instagram API access token
            user_id: Instagram user ID
        """
        self.access_token = access_token
        self.user_id = user_id
        self.base_url = "https://graph.instagram.com"
    
    def fetch_recent_media(self, limit: int = 6) -> List[Dict]:
        """
        Fetch recent media posts from Instagram.
        
        Args:
            limit: Number of posts to fetch (default 6)
            
        Returns:
            List of media dictionaries with keys:
            - id: Media ID
            - media_type: IMAGE, VIDEO, or CAROUSEL_ALBUM
            - media_url: URL to media file
            - permalink: Link to Instagram post
            - caption: Post caption (optional)
            - timestamp: Post timestamp
            
        Raises:
            InstagramAPIError: If API request fails
        """
        try:
            # Construct API endpoint URL
            url = f"{self.base_url}/{self.user_id}/media"
            
            # Define query parameters
            params = {
                'fields': 'id,media_type,media_url,permalink,caption,timestamp',
                'access_token': self.access_token,
                'limit': limit
            }
            
            # Make GET request to Instagram Graph API
            response = requests.get(url, params=params, timeout=10)
            
            # Check if request was successful
            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_message = error_data.get('error', {}).get('message', 'Unknown error')
                raise InstagramAPIError(
                    f"Instagram API request failed with status {response.status_code}: {error_message}"
                )
            
            # Parse JSON response
            data = response.json()
            
            # Extract media data from response
            media_list = data.get('data', [])
            
            return media_list
            
        except requests.exceptions.Timeout:
            raise InstagramAPIError("Instagram API request timed out")
        except requests.exceptions.ConnectionError:
            raise InstagramAPIError("Failed to connect to Instagram API")
        except requests.exceptions.RequestException as e:
            raise InstagramAPIError(f"Instagram API request failed: {str(e)}")
        except (KeyError, ValueError) as e:
            raise InstagramAPIError(f"Failed to parse Instagram API response: {str(e)}")
    
    def is_token_valid(self) -> bool:
        """
        Check if access token is still valid.
        
        Returns:
            bool: True if token is valid
        """
        try:
            # Use the debug_token endpoint to check token validity
            url = f"{self.base_url}/debug_token"
            
            params = {
                'input_token': self.access_token,
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            # If request fails, token is likely invalid
            if response.status_code != 200:
                return False
            
            # Parse response
            data = response.json()
            
            # Check if token data indicates validity
            token_data = data.get('data', {})
            is_valid = token_data.get('is_valid', False)
            
            return is_valid
            
        except (requests.exceptions.RequestException, KeyError, ValueError):
            # If any error occurs, assume token is invalid
            return False
