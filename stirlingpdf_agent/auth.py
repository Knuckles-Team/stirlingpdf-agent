#!/usr/bin/python
import urllib3
from agent_utilities.core.config import setting

from stirlingpdf_agent.api_client import StirlingPdfApi

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from agent_utilities.core.exceptions import AuthError, UnauthorizedError

_client = None


def get_client():
    """Get or create a singleton API client instance."""
    global _client
    if _client is None:
        base_url = setting("STIRLINGPDF_URL", "http://localhost:8080")
        token = setting("STIRLINGPDF_TOKEN", "") or setting("STIRLINGPDF_API_KEY", "")
        verify = bool(
            setting("STIRLINGPDF_SSL_VERIFY", setting("STIRLINGPDF_AGENT_VERIFY", True))
        )

        try:
            _client = StirlingPdfApi(
                base_url=base_url,
                token=token,
                verify=verify,
            )
        except (AuthError, UnauthorizedError) as e:
            raise RuntimeError(
                f"AUTHENTICATION ERROR: The Stirling PDF API key provided is not valid for '{base_url}'. "
                f"Please check your STIRLINGPDF_API_KEY and STIRLINGPDF_URL environment variables. "
                f"Error details: {str(e)}"
            ) from e

    return _client
