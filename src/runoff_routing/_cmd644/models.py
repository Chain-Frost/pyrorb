"""Immutable typed computational event and domain errors."""

from dataclasses import dataclass


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

    @property
    def source_count(self) -> int:
        """Number of code-1 records in original encounter order."""
        return len(self.areas)

    @property
    def reach_count(self) -> int:
        """Number of code-1 and code-5 reaches."""
        return sum(control.code in (1, 2, 5) for control in self.controls)
