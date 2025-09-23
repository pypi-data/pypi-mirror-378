from typing import List, Dict, Any
from .base import BaseClient

class DevicesAPI:
    def __init__(self, client: BaseClient):
        self.client = client

    def list_devices(self, access_token: str) -> List[Dict[str, Any]]:
        headers = {"X-Authorization": access_token}
        data = self.client.request("GET", f"/auth/{self.client.app_id}/devices", headers=headers)
        return data if isinstance(data, list) else []
