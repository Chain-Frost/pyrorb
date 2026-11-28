"""Immutable typed computational event and domain errors."""

from dataclasses import dataclass
from typing import Literal

from .precision import UnsupportedNumericPath


class InvalidInputError(ValueError):
    """Typed JSON event violates the declared structural or physical input contract."""


# Preserve the submitted public exception import and catch identity.
InvalidInput = InvalidInputError


@dataclass(frozen=True, slots=True)
class NumberInput:
    """Original decimal numeric token and the admitted binary64 -> binary32 value."""

    lexeme: str
    binary64: float
    stored: float


@dataclass(frozen=True, slots=True)
class Control:
    """Input-order control, with original numeric length identity."""

    code: int
    length: NumberInput


@dataclass(frozen=True, slots=True)
class Event:
    """One ordinary start-zero event, including original input text and identity."""

    event_id: str
    input_sha256: str
    original_json: str
    controls: tuple[Control, ...]
    areas: tuple[NumberInput, ...]
    depths: tuple[NumberInput, ...]
    impervious: tuple[NumberInput, ...]
    weights: tuple[NumberInput, ...]
    h: NumberInput
    kc: NumberInput
    m: NumberInput
    il: NumberInput
    cl: NumberInput
    n: int
    loss_model: Literal[1, 2] = 1

    def validate_code11_layout(self) -> None:
        """Do not reinterpret arbitrary diagnostic placement in the internal kernel."""
        codes = tuple(control.code for control in self.controls)
        if 11 in codes and (codes[0] != 11 or codes.count(11) != 1 or codes.count(7) != 1 or codes[-1] != 7):
            message = "Code 11 requires one first-source diagnostic control and one terminal print"
            raise UnsupportedNumericPath(message)

    @property
    def source_count(self) -> int:
        """Number of sources in original encounter order."""
        return len(self.areas)

    @property
    def reach_count(self) -> int:
        """Number of source and routing reaches, including the first code-11 reach."""
        return sum(control.code in (1, 2, 5, 11) for control in self.controls)
