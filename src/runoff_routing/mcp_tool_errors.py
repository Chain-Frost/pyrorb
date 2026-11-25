"""Expose bounded, actionable anticipated MCP tool errors without changing Python APIs.

The MCP SDK hides unexpected exception messages by design. Wrap only expected
input/filesystem failures in ToolError; unexpected defects retain that protection.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

from mcp.server.mcpserver.exceptions import ToolError

_EXPLAIN_EXPECTED_ERRORS_P = ParamSpec("_EXPLAIN_EXPECTED_ERRORS_P")
_EXPLAIN_EXPECTED_ERRORS_R = TypeVar("_EXPLAIN_EXPECTED_ERRORS_R")

MAX_DETAIL_CHARS = 200


class ExpectedMCPError(ValueError):
    """Local MCP preflight failure with an explicit, stable user-facing code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _detail(exc: ValueError) -> str:
    """Bound/control-clean input diagnostics before forwarding them to an agent."""
    preview = str(exc)[:MAX_DETAIL_CHARS]
    return "".join(character if character.isprintable() else " " for character in preview).strip()


def _filesystem_failure(exc: OSError) -> str:
    """Report a corrective action, not the potentially sensitive OS exception text."""
    if isinstance(exc, FileExistsError):
        return "[output_exists] Destination already exists. Choose an unused output filename or prefix."
    if isinstance(exc, FileNotFoundError):
        return "[input_missing] Required file was not found. Check the local input path and try again."
    if isinstance(exc, IsADirectoryError):
        return "[invalid_file_path] A file path names a directory. Supply a regular file."
    if isinstance(exc, PermissionError):
        return "[file_permission_denied] Cannot access the selected local file. Check permissions."
    return "[file_io_error] Local file access failed. Check paths and permissions; no retry was attempted."


def _validation_failure(exc: ValueError) -> str:
    """Classify parser failures, but never send untrusted parser text to MCP clients."""
    category = str(exc)[:320].lower()
    if "exceeds" in category or "too large" in category or "larger than" in category:
        return "[input_limit_exceeded] Input exceeds an established size limit. Reduce the input and retry."
    if "duplicate" in category and "key" in category:
        return "[invalid_input] Duplicate JSON key. Remove duplicate keys and revalidate."
    if "numerical" in category or "engineering-v1" in category or "computation engine" in category:
        return "[invalid_engine_selection] Invalid engine or numerical profile. Check get_engine_capabilities."
    if "unsupported" in category or "not supported" in category:
        return "[unsupported_input] Input uses an unsupported feature. Check the capability catalogue."
    return "[invalid_input] Input validation failed. Check the source schema and revalidate."


def _known_failure(exc: OSError | ValueError) -> str:
    """Classify caller-correctable failures without exposing private paths or data."""
    if isinstance(exc, ExpectedMCPError):
        return f"[{exc.code}] {_detail(exc)}"
    if isinstance(exc, OSError):
        return _filesystem_failure(exc)
    # Original project readers wrap OSError in ProjectError. Do not echo their
    # messages, which can contain absolute paths and raw input key/value text.
    if isinstance(exc.__cause__, OSError):
        return _filesystem_failure(exc.__cause__)
    return _validation_failure(exc)


def explain_expected_errors(
    function: Callable[_EXPLAIN_EXPECTED_ERRORS_P, _EXPLAIN_EXPECTED_ERRORS_R],
) -> Callable[_EXPLAIN_EXPECTED_ERRORS_P, _EXPLAIN_EXPECTED_ERRORS_R]:
    """Adapt a Python function only at MCP registration, preserving its native API errors."""

    @wraps(function)
    def invoke(
        *args: _EXPLAIN_EXPECTED_ERRORS_P.args, **kwargs: _EXPLAIN_EXPECTED_ERRORS_P.kwargs
    ) -> _EXPLAIN_EXPECTED_ERRORS_R:
        try:
            return function(*args, **kwargs)
        except (OSError, ValueError) as exc:
            raise ToolError(_known_failure(exc)) from exc

    return invoke
