#!/usr/bin/python
from agent_utilities.core.config import setting
from agent_utilities.core.exceptions import AuthError, UnauthorizedError
from agent_utilities.core.transport_security import (
    ResolvedTLSProfile,
    resolve_configured_tls_profile,
)

from stirlingpdf_agent.api_client import StirlingPdfApi

_client = None


def get_client(tls_profile: ResolvedTLSProfile | None = None):
    """Get or create a singleton API client instance."""
    global _client
    if _client is None:
        base_url = setting("STIRLINGPDF_URL", "")
        token = setting("STIRLINGPDF_TOKEN", "") or setting("STIRLINGPDF_API_KEY", "")
        if not base_url:
            raise RuntimeError("STIRLINGPDF_URL is required")

        try:
            _client = StirlingPdfApi(
                base_url=base_url,
                token=token,
                tls_profile=tls_profile
                or resolve_configured_tls_profile("stirlingpdf"),
            )
        except (AuthError, UnauthorizedError) as e:
            raise RuntimeError(
                "AUTHENTICATION ERROR: The configured API key was rejected. "
                f"Please check your STIRLINGPDF_API_KEY and STIRLINGPDF_URL environment variables. "
                f"Error details: {type(e).__name__}"
            ) from e

    return _client
