# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python library that provides a thread-safe, type-friendly singleton base class. The library supports Python 3.9-3.13 with version-adaptive implementations.

## Development Commands

**Testing:**
```bash
nox -s test_all_tests    # Run tests across Python 3.9-3.13
pytest                   # Run tests in current environment
```

**Linting:**
```bash
nox -s ruff_check      # Run ruff linting and formatting checks
nox -s ruff_fix        # Run ruff with auto-fix
nox -s pyright         # Run type checking
nox -t lint            # Run all linting checks
nox -t typecheck       # Run all type checking
```

**Installation:**
```bash
pip install -e '.[dev]'   # Install in development mode with dev dependencies
```

## Code Architecture

**Core Components:**
- `src/singleton_base/__init__.py`: Main package entry point
- `src/singleton_base/singleton_base.py`: Unified singleton implementation
- `src/singleton_base/_common.py`: Version-adaptive type definitions

**Key Design Patterns:**
- Thread-safe singleton creation using locks
- Version-adaptive type definitions in `_common.py`
- Class methods for instance management: `get_instance()`, `has_instance()`, `reset_instance()`
- Test-friendly design with `reset_instance()` method

**Testing Strategy:**
- Comprehensive test suite covering thread safety, type hints, and edge cases
- Tests for basic functionality, threading, nested subclassing, and imports
- Cross-version testing via Nox

## Code Style

- Line length: 120 characters
- Uses Ruff for linting and formatting, Pyright for type checking
- Full type hint support with modern typing (list, dict, not List, Dict)
- No external runtime dependencies
