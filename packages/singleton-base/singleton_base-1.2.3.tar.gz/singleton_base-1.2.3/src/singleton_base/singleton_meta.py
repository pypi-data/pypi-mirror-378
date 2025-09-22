"""Metaclass for singleton pattern enforcement."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from singleton_base._common import PerClassData, SelfNone, attr_name

if TYPE_CHECKING:
    from threading import Lock

T = TypeVar("T")


class MetaBase(ABCMeta, Generic[T]):
    """Abstract base metaclass for singleton pattern enforcement."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict, bypass: bool = False) -> MetaBase:
        """Create a new class with the singleton metaclass."""
        if bypass or not bases:  # Allow bypassing for base class or if no bases (i.e., the base class itself)
            return super().__new__(mcs, name, bases, namespace)
        namespace[attr_name(name)] = PerClassData()
        return super().__new__(mcs, name, bases, namespace)

    @property
    def name(cls) -> str:
        """Get the name of the class."""
        return cls.__name__

    @property
    def _meta_name(cls) -> str:
        """Get the name of the metaclass."""
        return attr_name(cls.name)

    @property
    def _internal(cls) -> PerClassData[T]:
        """Get the internal data attribute name for the class."""
        if not hasattr(cls, cls._meta_name):
            raise AttributeError(f"Class {cls.name} is missing internal data attribute {cls._meta_name}")
        return getattr(cls, cls._meta_name)

    @property
    def _instance(cls) -> T | None:
        """Get the singleton instance, or None if it does not exist"""
        return cls._internal.instance

    @_instance.setter
    def _instance(cls, value: SelfNone = None) -> None:
        """Set the singleton instance to a new value"""
        cls._internal.instance = value

    @property
    def _lock(cls) -> Lock:
        """Get the lock for the class."""
        return cls._internal.lock

    @abstractmethod
    def init(cls) -> T:
        """Initialize the singleton instance."""

    @abstractmethod
    def get_instance(cls) -> T:
        """Get the singleton instance."""

    @abstractmethod
    def has_instance(cls) -> bool:
        """Check if instance exists."""

    @abstractmethod
    def reset_instance(cls) -> None:
        """Reset the singleton for re-initialization."""


class SingletonMeta(MetaBase[T]):
    """Metaclass that enforces the singleton pattern."""

    def __call__(cls, *args, **kwargs) -> T:
        """Override the __call__ method to control instance creation."""
        if cls._instance is not None:
            return cls._instance
        if cls._instance is None:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
