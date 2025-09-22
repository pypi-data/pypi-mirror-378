from __future__ import annotations

import sys
from threading import Lock
from typing import Generic, TypeVar

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Self

else:  # pragma: no cover
    from typing_extensions import Self

SelfNone = Self | None


T = TypeVar("T")


class PerClassData(Generic[T]):
    """Holds per-class data for the singleton metaclass."""

    __slots__: tuple = ("instance", "lock")

    def __init__(self) -> None:
        """Initialize the per-class data."""
        self.instance: T | None = None
        self.lock: Lock = Lock()

    def __repr__(self) -> str:
        """Return a string representation of the PerClassData."""
        return f"ClassData(instance={self.instance}, lock={self.lock})"


def attr_name(cls: str, attr: str = "data") -> str:
    """Generate a standardized attribute name for storing per-class data.

    Args:
        cls (str): The class name.
        attr (str): The attribute name.

    Returns:
        str: The standardized attribute name.
    """
    return f"_{cls}_{attr}"


__all__ = ["Self", "SelfNone", "attr_name"]
