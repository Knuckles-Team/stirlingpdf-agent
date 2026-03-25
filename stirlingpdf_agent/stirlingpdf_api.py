#!/usr/bin/python
# coding: utf-8
from typing import Optional

import requests
import urllib3
from pydantic import ValidationError

from stirlingpdf_agent.stirlingpdf_agent_models import AddWatermarkModel, Response
from agent_utilities.decorators import require_auth
from agent_utilities.exceptions import (
    AuthError,
    UnauthorizedError,
    ParameterError,
    MissingParameterError,
)


class StirlingPdfApi(object):

    def __init__(
        self,
        base_url: str = None,
        token: Optional[str] = None,
        proxies: Optional[dict] = None,
        verify: Optional[bool] = True,
    ):
        if base_url is None:
            raise MissingParameterError("base_url is required")

        self._session = requests.Session()
        self.base_url = base_url.rstrip("/")
        self.url = f"{self.base_url}/api/v1"
        self.headers = {}
        self.api_key = token
        self.verify = verify
        self.proxies = proxies

        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if self.api_key:
            self.headers["X-API-KEY"] = self.api_key

        # Authentication check moved to method calls via require_auth

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

            # Requires multipart/form-data for file upload
            with open(filepath, "rb") as f:
                files = {"fileInput": (filepath, f, "application/pdf")}
                response = self._session.post(
                    url=f"{self.url}/general/add-watermark",  # Depending on API endpoint structure
                    data=model.api_parameters,
                    files=files,
                    headers=self.headers,
                    verify=self.verify,
                    proxies=self.proxies,
                )

            response.raise_for_status()

            # Return raw content since it replies with the modified PDF file
            return Response(response=response, data=response.content)

        except ValidationError as ve:
            print(f"Invalid parameters or response data: {ve.errors()}")
            raise ParameterError(f"Invalid parameters: {ve.errors()}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in [401, 403]:
                raise AuthError if e.response.status_code == 401 else UnauthorizedError
            raise e
        except Exception as e:
            print(f"Error during API call: {e}")
            raise
