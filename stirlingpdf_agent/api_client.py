from agent_utilities.core.exceptions import (
    AuthError,
    MissingParameterError,
    ParameterError,
    UnauthorizedError,
)

from stirlingpdf_agent.api.api_client_watermark import WatermarkClient

# Expose classes and exceptions for backwards compatibility
__all__ = [
    "StirlingPdfApi",
    "AuthError",
    "MissingParameterError",
    "ParameterError",
    "UnauthorizedError",
]


class StirlingPdfApi(WatermarkClient):
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        proxies: dict | None = None,
        verify: bool | None = True,
    ):
        super().__init__(
            base_url=base_url,
            token=token,
            proxies=proxies,
            verify=verify,
        )
