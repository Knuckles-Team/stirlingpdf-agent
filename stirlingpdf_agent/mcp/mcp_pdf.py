"""MCP tools for pdf operations.

Auto-generated from mcp_server.py during ecosystem standardization.
"""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from stirlingpdf_agent.auth import get_client


def register_pdf_tools(mcp: FastMCP):
    @mcp.tool(tags={"PDF"}, name="pdf_action")
    async def pdf_action(
        action: str = Field(
            description="The action/method name to execute on Stirling PDF API (e.g. add_watermark)"
        ),
        params_json: str = Field(
            default="{}",
            description="JSON string of parameters to pass to the action (e.g. {'filepath': 'input.pdf', 'watermarkText': 'DRAFT'}).",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(
            default=None, description="MCP context for progress reporting"
        ),
    ) -> dict:
        """Execute any Stirling PDF API action dynamically."""
        if ctx:
            await ctx.info(f"Executing Stirling PDF action: {action}...")
        import json

        try:
            kwargs = json.loads(params_json) if params_json else {}
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Dynamic method lookup
        method = getattr(client, action, None)
        if method is None:
            raise ValueError(f"Unknown action '{action}' on StirlingPdfApi")

        res = method(**kwargs)

        if hasattr(res, "dict") and callable(res.dict):
            res_dict = res.dict()
            if isinstance(res_dict, dict):
                # If Response wraps binary data, encode it as base64 and remove requests.Response
                if "data" in res_dict and isinstance(res_dict["data"], bytes):
                    import base64

                    res_dict["data"] = base64.b64encode(res_dict["data"]).decode(
                        "utf-8"
                    )
                if "response" in res_dict:
                    res_dict.pop("response", None)
                return res_dict
        elif hasattr(res, "model_dump") and callable(res.model_dump):
            res_dict = res.model_dump()
            if isinstance(res_dict, dict):
                if "data" in res_dict and isinstance(res_dict["data"], bytes):
                    import base64

                    res_dict["data"] = base64.b64encode(res_dict["data"]).decode(
                        "utf-8"
                    )
                if "response" in res_dict:
                    res_dict.pop("response", None)
                return res_dict

        return {"status": "success", "result": str(res)}
