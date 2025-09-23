from typing import Dict, Any
from .base import BaseClient
from scute.exceptions import APIRequestError

class TokensAPI:
    def __init__(self, client: BaseClient):
        self.client = client

    def refresh_access_token(
        self,
        refresh_token: str,
        csrf_token: str
    ) -> Dict[str, Any]:
        """
        Refreshes the access token using the refresh and CSRF tokens.
        """
        headers = {
            "X-Refresh-Token": refresh_token,
            "X-CSRF-Token": csrf_token
        }
        path = f"/auth/{self.client.app_id}/tokens/refresh"
        return self.client.request("POST", path, headers=headers) or {}

    def verify_access_token(self, access_token: str) -> bool:
        """
        Verifies the validity of an access token.
        """
        headers = {"X-Authorization": access_token}
        path = f"/auth/{self.client.app_id}/tokens/access/verify"
        try:
            self.client.request("POST", path, headers=headers)
            return True
        except APIRequestError as e:
            if e.status_code == 401:
                return False
            raise

    def verify_refresh_token(self, refresh_token: str, csrf_token: str) -> bool:
        """
        Verifies the validity of a refresh token and CSRF token.
        """
        headers = {
            "X-Refresh-Token": refresh_token,
            "X-CSRF-Token": csrf_token
        }
        path = f"/auth/{self.client.app_id}/tokens/refresh/verify"
        try:
            self.client.request("POST", path, headers=headers)
            return True
        except APIRequestError as e:
            if e.status_code == 401:
                return False
            raise

    def rotate_access_token(
        self,
        access_token: str
    ) -> Dict[str, Any]:
        """
        Refreshes the access token using the access token and API secret.
        Specifically for server-side http-only cookie flows.
        """
        headers = {
            "X-Authorization": access_token,
            "Authorization": self.client.app_secret
        }
        path = f"/auth/{self.client.app_id}/tokens/rotate_access"
        return self.client.request("POST", path, headers=headers) or {}

    def force_refresh_token(
        self,
        refresh_token: str,
        csrf_token: str
    ) -> Dict[str, Any]:
        """
        Forces a refresh of the access token using the refresh token,
        CSRF token, and API secret. Intended for secure, server-side
        cookie-based rotation flows.
        """
        headers = {
            "X-Refresh-Token": refresh_token,
            "X-CSRF-Token": csrf_token,
            "Authorization": self.client.app_secret
        }
        path = f"/auth/{self.client.app_id}/tokens/force_refresh"
        return self.client.request("POST", path, headers=headers) or {}
