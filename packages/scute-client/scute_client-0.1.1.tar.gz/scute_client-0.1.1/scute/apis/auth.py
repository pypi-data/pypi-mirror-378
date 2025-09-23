from typing import Dict, Any
from .base import BaseClient

class AuthAPI:
    def __init__(self, client: BaseClient):
        self.client = client

    def get_current_user(self, access_token: str) -> Dict[str, Any]:
        headers = {"X-Authorization": access_token}
        data = self.client.request("GET", f"/auth/{self.client.app_id}/current_user", headers=headers)
        return data.get("user", {}) if data else {}

    def logout_current_user(self, access_token: str) -> bool:
        headers = {"X-Authorization": access_token}
        self.client.request("POST", f"/auth/{self.client.app_id}/current_user/logout", headers=headers)
        return True
