"""Singleton Base Class to make any other class a singleton with proper type hinting."""

from .singleton_base import SingletonBase, SingletonMeta
from .singleton_wrapper import SingletonWrap

__version__ = "1.2.3"

__all__ = ["SingletonBase", "SingletonMeta", "SingletonWrap", "__version__"]
