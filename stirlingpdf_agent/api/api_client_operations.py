"""Typed per-operation Stirling PDF calls that take and return file bytes."""

from __future__ import annotations

import requests
from scion_sdk.exceptions import (
    AuthError,
    ParameterError,
    UnauthorizedError,
    require_auth,
)

from stirlingpdf_agent.api.api_client_base import BaseApiClient
from stirlingpdf_agent.api.files import max_file_bytes, read_input
from stirlingpdf_agent.stirlingpdf_agent_models import Response


class OperationsClient(BaseApiClient):
    """Single- and multi-file PDF operations (``POST /api/v1/...`` multipart)."""

    def _post_files(
        self,
        route: str,
        files: list[tuple[str, bytes]],
        data: dict[str, str] | None = None,
    ) -> Response:
        multipart = [
            ("fileInput", (name, content, "application/pdf")) for name, content in files
        ]
        try:
            response = self._session.post(
                url=f"{self.url}/{route}",
                data={k: v for k, v in (data or {}).items() if v is not None},
                files=multipart,
                headers=self.headers,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                exc = AuthError if e.response.status_code == 401 else UnauthorizedError
                raise exc from e
            raise
        if len(response.content) > max_file_bytes():
            raise ValueError("operation output exceeds the configured size limit")
        return Response(response=response, data=response.content)

    @require_auth
    def rotate_pdf(
        self,
        angle: int,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Rotate every page of a PDF by a multiple of 90 degrees (POST /api/v1/general/rotate-pdf)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "general/rotate-pdf", [(name, content)], {"angle": str(angle)}
        )

    @require_auth
    def compress_pdf(
        self,
        optimize_level: int = 5,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Compress a PDF at an optimization level from 1 to 9 (POST /api/v1/misc/compress-pdf)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "misc/compress-pdf",
            [(name, content)],
            {"optimizeLevel": str(optimize_level)},
        )

    @require_auth
    def split_pdf(
        self,
        page_numbers: str,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Split a PDF after the listed pages, for example '1,3,7-9'; the result is a ZIP (POST /api/v1/general/split-pages)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "general/split-pages", [(name, content)], {"pageNumbers": page_numbers}
        )

    @require_auth
    def merge_pdfs(
        self,
        files_base64: list[str],
        sort_type: str = "orderProvided",
    ) -> Response:
        """Merge several base64 PDFs, in the given order, into one PDF (POST /api/v1/general/merge-pdfs)."""
        if len(files_base64) < 2:
            raise ParameterError("merge_pdfs needs at least two files")
        files = [
            read_input(None, item, f"input-{index}.pdf")
            for index, item in enumerate(files_base64, start=1)
        ]
        return self._post_files("general/merge-pdfs", files, {"sortType": sort_type})

    @require_auth
    def add_password(
        self,
        password: str,
        owner_password: str | None = None,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Encrypt a PDF with a user password and an optional owner password (POST /api/v1/security/add-password)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "security/add-password",
            [(name, content)],
            {"password": password, "ownerPassword": owner_password},
        )

    @require_auth
    def remove_password(
        self,
        password: str,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Remove the password from an encrypted PDF (POST /api/v1/security/remove-password)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "security/remove-password", [(name, content)], {"password": password}
        )

    @require_auth
    def sanitize_pdf(
        self,
        remove_javascript: bool = True,
        remove_embedded_files: bool = True,
        remove_metadata: bool = False,
        remove_links: bool = False,
        filepath: str | None = None,
        file_base64: str | None = None,
        filename: str | None = None,
    ) -> Response:
        """Strip scripts, embedded files, metadata or links from a PDF (POST /api/v1/security/sanitize-pdf)."""
        name, content = read_input(filepath, file_base64, filename)
        return self._post_files(
            "security/sanitize-pdf",
            [(name, content)],
            {
                "removeJavaScript": str(remove_javascript).lower(),
                "removeEmbeddedFiles": str(remove_embedded_files).lower(),
                "removeMetadata": str(remove_metadata).lower(),
                "removeLinks": str(remove_links).lower(),
            },
        )
