import requests
from agent_utilities.core.exceptions import MissingParameterError
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)


class BaseApiClient:
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        if base_url is None:
            raise MissingParameterError("base_url is required")

        self.tls_profile = tls_profile or resolve_configured_tls_profile("stirlingpdf")
        self._session = self.tls_profile.configure_requests_session(requests.Session())
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/api/v1"
        self.headers = {}
        self.api_key = token
        if self.api_key:
            self.headers["X-API-KEY"] = self.api_key

    def close(self) -> None:
        """Release transport resources and runtime-only TLS material."""
        self._session.close()
        self.tls_profile.cleanup()
