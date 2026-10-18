import sys

import requests
from agent_connector_sdk.exceptions import (
    AuthError,
    ParameterError,
    UnauthorizedError,
    require_auth,
)
from pydantic import ValidationError

from stirlingpdf_agent.api.api_client_base import BaseApiClient
from stirlingpdf_agent.stirlingpdf_agent_models import AddWatermarkModel, Response


class WatermarkClient(BaseApiClient):
    @staticmethod
    def _ingest_watermark(filepath: str, output_bytes: bytes, params: dict) -> None:
        """Best-effort native KG ingestion of a completed add-watermark operation.

        Records a :PdfOperation
        with :usedTool / :produced / :derivedFrom / :appliedWatermark provenance. Fully
        guarded: no-ops when the epistemic-graph engine or agent-connector-sdk KG stack is
        absent, so the watermark call never fails because of ingestion.
        """
        try:
            from stirlingpdf_agent.kg_ingest import ingest_operation

            ingest_operation(
                "add_watermark",
                params=params,
                size_bytes=len(output_bytes) if output_bytes else None,
            )
        except Exception as e:  # noqa: BLE001 — ingestion is strictly best-effort
            print(f"KG ingest skipped: {type(e).__name__}", file=sys.stderr)

    @require_auth
    def add_watermark(self, filepath: str, **kwargs) -> Response:
        """
        Add a watermark to a PDF file.

        :param filepath: Path to the input PDF file.
        :type filepath: str

        :return: Response containing the raw PDF bytes.
        :rtype: Response
        """
        try:
            model = AddWatermarkModel(**kwargs)

            with open(filepath, "rb") as f:
                files = {"fileInput": (filepath, f, "application/pdf")}
                response = self._session.post(
                    url=f"{self.url}/general/add-watermark",
                    data=model.api_parameters,
                    files=files,
                    headers=self.headers,
                )

            response.raise_for_status()

            self._ingest_watermark(filepath, response.content, kwargs)

            return Response(response=response, data=response.content)

        except ValidationError as ve:
            print(
                f"Invalid parameters or response data: {ve.errors()}", file=sys.stderr
            )
            raise ParameterError(f"Invalid parameters: {ve.errors()}") from ve
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                exc = AuthError if e.response.status_code == 401 else UnauthorizedError
                raise exc from e
            raise e from e
        except Exception as e:
            print(f"API call failed: {type(e).__name__}", file=sys.stderr)
            raise e from e
