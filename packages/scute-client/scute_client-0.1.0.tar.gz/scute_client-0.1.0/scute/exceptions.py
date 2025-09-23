from typing import Optional

import requests


class APIClientError(Exception):
    """Base exception for all client errors."""

class APIRequestError(APIClientError):
    def __init__(self, status_code: int, message: str, response: Optional[requests.Response] = None):
        super().__init__(f"API request failed with status {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.response = response
