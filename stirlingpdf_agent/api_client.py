from agent_utilities.core.transport_security import ResolvedTLSProfile

from stirlingpdf_agent.api.api_client_watermark import WatermarkClient

__all__ = ["StirlingPdfApi"]


class StirlingPdfApi(WatermarkClient):
    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        tls_profile: ResolvedTLSProfile | None = None,
    ):
        super().__init__(
            base_url=base_url,
            token=token,
            tls_profile=tls_profile,
        )
