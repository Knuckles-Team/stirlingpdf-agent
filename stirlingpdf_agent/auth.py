#!/usr/bin/python
import os

import urllib3

from stirlingpdf_agent.api_client import StirlingPdfApi

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from agent_utilities.core.exceptions import AuthError, UnauthorizedError

_client = None


def get_client():
    """Get or create a singleton API client instance."""
    global _client
    if _client is None:
        base_url = os.getenv("STIRLINGPDF_URL", "http://localhost:8080")
        token = os.getenv("STIRLINGPDF_TOKEN") or os.getenv("STIRLINGPDF_API_KEY", "")
        verify_env = os.getenv("STIRLINGPDF_SSL_VERIFY")
        if verify_env is None:
            verify_env = os.getenv("STIRLINGPDF_AGENT_VERIFY", "True")
        verify: bool = verify_env.lower() in ("true", "1", "yes")

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
