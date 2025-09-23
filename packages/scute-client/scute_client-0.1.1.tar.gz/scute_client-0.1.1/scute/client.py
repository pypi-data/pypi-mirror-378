from scute.apis.base import BaseClient
from scute.apis.auth import AuthAPI
from scute.apis.users import UsersAPI
from scute.apis.devices import DevicesAPI
from scute.apis.tokens import TokensAPI

class ScuteClient:
    def __init__(
        self,
        app_id: str,
        app_secret: str,
        base_url: str = "https://api.scute.io",
        api_version: str = "v1",
        timeout: int = 5,
    ):
        self.base = BaseClient(app_id=app_id, app_secret=app_secret, base_url=base_url, api_version=api_version, timeout=timeout)
        self.auth = AuthAPI(client=self.base)
        self.tokens = TokensAPI(client=self.base)
        self.users = UsersAPI(client=self.base)
        self.devices = DevicesAPI(client=self.base)
