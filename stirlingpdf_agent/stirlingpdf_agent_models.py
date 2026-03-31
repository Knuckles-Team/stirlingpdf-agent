#!/usr/bin/python

from typing import Optional, Any
from pydantic import BaseModel, ConfigDict, Field
import requests


class Response(BaseModel):
    """
    Standard Response Wrapper.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    response: requests.Response
    data: Any = None


class BaseModelWrapper(BaseModel):
    """
    Base Model wrapping common functionalities such as extracting nested API parameters
    from the root attributes.
    """

    model_config = ConfigDict(populate_by_name=True)

    @property
    def api_parameters(self) -> dict:
        """
        Convert the Pydantic model to a dictionary suitable for passing as API arguments or params.
        Can be customized to exclude specific internal fields like IDs that are passed in the URL.
        """
        return self.model_dump(exclude_none=True, by_alias=True)


class AddWatermarkModel(BaseModelWrapper):
    """
    Input model for adding a watermark.
    """

    watermarkType: str = Field(..., description="Type of watermark (e.g. 'text').")
    watermarkText: str = Field(..., description="The text of the watermark.")
    alphabet: Optional[str] = Field("roman", description="Alphabet type.")
    fontSize: Optional[str] = Field("30", description="Font size.")
    rotation: Optional[str] = Field("0", description="Rotation angle.")
    opacity: Optional[str] = Field("0.5", description="Opacity (0.0 to 1.0).")
    widthSpacer: Optional[str] = Field("50", description="Width spacing.")
    heightSpacer: Optional[str] = Field("50", description="Height spacing.")

    @property
    def api_parameters(self) -> dict:
        return self.model_dump(exclude_none=True, by_alias=True)
