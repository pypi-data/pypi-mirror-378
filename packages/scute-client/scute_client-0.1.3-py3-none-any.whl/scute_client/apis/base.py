import logging
import requests
from typing import Optional, Dict, Any

from requests.adapters import HTTPAdapter
from urllib3 import Retry

from scute.exceptions import APIRequestError

logger = logging.getLogger(__name__)

class BaseClient:
    def __init__(self, app_id: str, app_secret: str, base_url: str, api_version: str, timeout: int):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip("/")
        self.api_version = api_version
        self.timeout = timeout
        self.session = requests.Session()

        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "POST", "DELETE", "OPTIONS", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

    def request(
            self,
            method: str,
            path: str,
            headers: Optional[Dict[str, str]] = None,
            params: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            data: Optional[Dict[str, Any]] = None,
            files: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        url = f"{self.base_url}/{self.api_version}{path}"
        logger.debug(
            f"Scute request to {url} with method={method}, headers={headers}, "
            f"params={params}, json={json}, data={data}, files={files}"
        )

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                files=files,
                timeout=self.timeout,
            )
        except requests.RequestException as e:
            logger.error(f"Request to {url} failed: {str(e)}")
            raise APIRequestError(status_code=-1, message=str(e))

        logger.debug(f"Scute response {response.status_code} from {url}: {response.text}")

        if response.status_code == 200:
            if response.content:
                try:
                    return response.json()
                except ValueError:
                    logger.warning(f"Invalid JSON from {url}")
                    return None
            return None

        raise APIRequestError(
            status_code=response.status_code,
            message=response.text,
            response=response,
        )
