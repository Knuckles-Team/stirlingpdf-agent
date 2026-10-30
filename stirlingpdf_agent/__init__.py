#!/usr/bin/env python

from scion_sdk.connector import Connector

from stirlingpdf_agent.api_client import StirlingPdfApi
from stirlingpdf_agent.auth import get_client
from stirlingpdf_agent.mcp_server import register_prompts

connector = Connector(
    api=StirlingPdfApi,
    get_client=get_client,
    tools="stirlingpdf_agent.mcp_server",
    instructions="Stirling PDF Agent MCP Server",
    extra_registrations=(register_prompts,),
)
