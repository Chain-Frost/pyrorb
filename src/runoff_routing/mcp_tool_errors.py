"""Expose bounded, actionable anticipated MCP tool errors without changing Python APIs.

The MCP SDK hides unexpected exception messages by design. Wrap only expected
input/filesystem failures in ToolError; unexpected defects retain that protection.
"""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps

from mcp.server.mcpserver.exceptions import ToolError

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


def _known_failure(exc: OSError | ValueError) -> str:
    """Classify caller-correctable failures, including wrapped filesystem causes."""
    if isinstance(exc, ExpectedMCPError):
        return f"[{exc.code}] {_detail(exc)}"
    if isinstance(exc, OSError):
        return _filesystem_failure(exc)
    # The existing project reader wraps its original OSError in ProjectError;
    # follow that cause rather than exposing its potentially absolute source path.
    if isinstance(exc.__cause__, OSError):
        return _filesystem_failure(exc.__cause__)
    message = _detail(exc)
    lowered = message.lower()
    if "exceeds" in lowered or "too large" in lowered or "larger than" in lowered:
        return f"[input_limit_exceeded] {message} Reduce the input size or requested population."
    if "numerical" in lowered or "engineering-v1" in lowered or "computation engine" in lowered:
        return f"[invalid_engine_selection] {message} Check get_engine_capabilities."
    if "unsupported" in lowered or "not supported" in lowered:
        return f"[unsupported_input] {message} Check the capability catalogue and source documentation."
    return f"[invalid_input] {message} Correct the input and revalidate before retrying."


def explain_expected_errors[**P, R](function: Callable[P, R]) -> Callable[P, R]:
    """Adapt a Python function only at MCP registration, preserving its native API errors."""

    @wraps(function)
    def invoke(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return function(*args, **kwargs)
        except (OSError, ValueError) as exc:
            raise ToolError(_known_failure(exc)) from exc

    return invoke
