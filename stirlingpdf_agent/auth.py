#!/usr/bin/python
# coding: utf-8

import os
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# TODO: Import your API wrapper class here
# from stirlingpdf_agent.stirlingpdf_api import StirlingpdfApi

_client = None


def get_client():
    """Get or create a singleton API client instance."""
    global _client
    if _client is None:
        base_url = os.getenv("STIRLINGPDF_URL", "http://localhost:8080")
        token = os.getenv("STIRLINGPDF_API_KEY", "")
        verify = os.getenv("STIRLINGPDF_AGENT_VERIFY", "True").lower() in (
            "true",
            "1",
            "yes",
        )

        # TODO: Uncomment and configure once the API wrapper class is created
        # _client = StirlingpdfApi(
        #     base_url=base_url,
        #     token=token,
        #     verify=verify,
        # )

        # Placeholder: return a simple session-based client
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {token}"})
        session.verify = verify
        _client = type("Client", (), {"session": session, "base_url": base_url})()

    return _client
