import requests
import urllib3
from agent_utilities.core.exceptions import MissingParameterError


class BaseApiClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        proxies: dict | None = None,
        verify: bool | None = True,
    ):
        if base_url is None:
            raise MissingParameterError("base_url is required")

        self._session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/api/v1"
        self.headers = {}
        self.api_key = token
        self.verify = verify
        self.proxies = proxies

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if self.api_key:
            self.headers["X-API-KEY"] = self.api_key
