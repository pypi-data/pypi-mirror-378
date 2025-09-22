# ruff: noqa: PLC0415


class TestImports:
    """Test class for checking imports of singleton base classes."""

    def test_imports(self):
        """Test that the singleton base class can be imported correctly"""
        from singleton_base import SingletonBase as ImportedBase
        from singleton_base.singleton_base import SingletonBase as DirectBase

        assert ImportedBase is DirectBase, "Both import paths should reference the same class"
