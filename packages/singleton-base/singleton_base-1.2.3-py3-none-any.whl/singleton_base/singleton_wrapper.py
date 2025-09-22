"""Singleton Base Class to make any other class a singleton with proper type hinting."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from functools import partial
from threading import Lock
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class _SingletonBase(Generic[T], metaclass=ABCMeta):
    """Abstract base for singleton wrapper patterns."""

    __slots__: tuple = ("_args", "_constructor", "_factory", "_instance", "_kwargs", "_lock")

    def __init__(self, constructor: type[T], /, *args: Any, **kwargs: Any) -> None:
        self._constructor: type[T] = constructor
        self._instance = None
        self._args: tuple[Any, ...] = args
        self._kwargs: dict[str, Any] = kwargs
        self._lock = Lock()
        self._factory: partial[T] | type[T] = self._gen_factory()

    def _gen_factory(self) -> partial[T] | type[T]:
        """Factory method to create the singleton instance."""
        if self._args or self._kwargs:
            return partial(self._constructor, *self._args, **self._kwargs)
        return self._constructor

    @abstractmethod
    def init(self) -> T:
        """Initialize the singleton instance."""

    @abstractmethod
    def get(self) -> T:
        """Get the singleton instance."""

    @abstractmethod
    def get_instance(self) -> T:
        """Return the singleton instance, creating it if it does not exist."""

    @abstractmethod
    def has_instance(self) -> bool:
        """Return ``True`` if the singleton instance has been initialized."""

    @abstractmethod
    def reset_instance(self) -> None:
        """Reset the singleton instance to allow re-initialization."""


class SingletonWrap(_SingletonBase[T]):
    """A thread-safe singleton wrapper for any class."""

    _slots__: tuple = ("_args", "_constructor", "_factory", "_kwargs", "_lock", "_instance")

    def init(self) -> T:
        """The singleton instance, created on first access."""
        try:
            self._instance = self._factory()
            return self._instance
        except Exception as e:
            self._instance = None  # Clean up partially created instance
            raise RuntimeError(f"Failed to create singleton instance of {self._constructor.__name__}") from e

    def get(self) -> T:
        """Get the singleton instance if it exists, otherwise create it."""
        if self._instance is not None:
            return self._instance
        with self._lock:
            if self._instance is not None:
                return self._instance
            return self.init()

    def get_instance(self) -> T:
        """Return the singleton instance, creating it if it does not exist."""
        return self.get()

    def has_instance(self) -> bool:
        """Return ``True`` if the singleton instance has been initialized."""
        return self._instance is not None

    def reset_instance(self) -> None:
        """Reset the singleton instance to allow re-initialization."""
        with self._lock:
            if self.has_instance():
                self._instance = None
