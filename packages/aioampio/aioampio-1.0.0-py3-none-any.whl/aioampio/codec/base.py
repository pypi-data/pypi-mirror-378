"""Base frame codes."""

from __future__ import annotations
from dataclasses import dataclass
from typing import runtime_checkable, Protocol, Any


@dataclass(frozen=True)
class CANFrame:
    """Class representing a CAN frame."""

    can_id: int
    data: memoryview


@dataclass(frozen=True)
class AmpioMessage:
    """Class representing an Ampio message."""

    raw: CANFrame
    payload: Any
    topic: str


@runtime_checkable
class Codec(Protocol):
    """Protocol for codec implementations."""

    # def encode(self, message: AmpioMessage) -> CANFrame | None:
    #     """Encode data into CAN frames."""
    #     ...

    def decode(self, frame: CANFrame) -> list[AmpioMessage] | None:
        """Decode a CAN frame into data."""
