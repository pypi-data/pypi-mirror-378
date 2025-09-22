"""A base class for singleton classes using a metaclass to enforce the singleton pattern."""

from __future__ import annotations

from typing import TYPE_CHECKING
from warnings import warn

from singleton_base.singleton_meta import SingletonMeta

if TYPE_CHECKING:  # pragma: no cover
    from singleton_base._common import Self


class SingletonBase(metaclass=SingletonMeta, bypass=True):
    """A base class for singleton classes"""

    @classmethod
    def init(cls, *args, **kwargs) -> Self:
        """Initialize the singleton instance.

        If the instance already exists, it is returned. Uses a lock to ensure thread safety.

        Args:
            **kwargs: Arguments passed to ``cls`` when creating the instance.

        Returns:
            Self: The singleton instance of the class.
        """
        if cls._instance is not None:
            return cls._instance
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(*args, **kwargs)
        return cls._instance

    @classmethod
    def has_instance(cls) -> bool:
        """Return ``True`` if the singleton instance has been initialized.

        Returns:
            bool: ``True`` if the instance exists, ``False`` otherwise.
        """
        return cls._instance is not None

    @classmethod
    def get_instance(cls, *args, **kwargs) -> Self:
        """Return the singleton instance.

        If the instance does not yet exist, it is created using the provided arguments. Uses a lock to ensure thread safety.

        Args:
            **kwargs: Arguments passed to ``cls`` when creating the instance.

        Returns:
            Self: The singleton instance of the class.

        Raises:
            RuntimeError: If ``init`` is ``False`` and the instance has not been initialized.
        """
        if kwargs.pop("init", False):  # Remove 'init' if present as a backwards compatibility measure
            warn(
                "'init' argument is deprecated and will be removed in a future version. "
                "No need to pass 'init=True' when calling get_instance().",
                DeprecationWarning,
                stacklevel=2,
            )
        return cls.init(*args, **kwargs)

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance to allow re-initialization.

        Uses a lock to ensure thread safety.
        """
        with cls._lock:
            cls._instance = None
