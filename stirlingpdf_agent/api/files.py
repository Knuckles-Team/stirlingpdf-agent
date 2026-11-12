"""File-bytes handling for Stirling PDF operations.

Design: a tool accepts a PDF either as ``file_base64`` (the bytes travel with the
call, so the caller needs no shared filesystem) or as ``filepath`` (a path the server
process can read). Exactly one is given. Results come back as the operation's
``data`` field, which the SDK encodes as base64. Inputs and outputs are bounded by
``STIRLINGPDF_MAX_FILE_BYTES`` (default 25 MiB); larger documents belong in an object
store, passed by reference through a store connector, not through a tool call.
"""

from __future__ import annotations

import base64
import binascii
from pathlib import Path

from scion_sdk.config import setting
from scion_sdk.exceptions import ParameterError

DEFAULT_MAX_FILE_BYTES = 25 * 1024 * 1024


def max_file_bytes() -> int:
    """The per-file byte bound for tool inputs."""
    try:
        return int(setting("STIRLINGPDF_MAX_FILE_BYTES", DEFAULT_MAX_FILE_BYTES))
    except (TypeError, ValueError):
        return DEFAULT_MAX_FILE_BYTES


def read_input(
    filepath: str | None, file_base64: str | None, filename: str | None
) -> tuple[str, bytes]:
    """Return ``(name, content)`` from exactly one of ``filepath`` or ``file_base64``."""
    if bool(filepath) == bool(file_base64):
        raise ParameterError("Provide exactly one of filepath or file_base64")
    limit = max_file_bytes()
    if file_base64:
        if len(file_base64) > (limit * 4) // 3 + 8:
            raise ParameterError("file_base64 exceeds the configured size limit")
        try:
            content = base64.b64decode(file_base64, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ParameterError("file_base64 is not valid base64") from exc
        return filename or "input.pdf", content
    path = Path(str(filepath))
    if not path.is_file():
        raise ParameterError("filepath is not a readable file")
    if path.stat().st_size > limit:
        raise ParameterError("filepath exceeds the configured size limit")
    return filename or str(filepath), path.read_bytes()
