import nox

VERSIONS = ["3.9", "3.10", "3.11", "3.12", "3.13"]


@nox.session(venv_backend="uv", tags=["lint"])
def ruff_check(session: nox.Session) -> None:
    """Run ruff linting and formatting checks (CI-friendly, no changes)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "check",
        ".",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--check",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["lint", "fix"])
def ruff_fix(session: nox.Session) -> None:
    """Run ruff linting and formatting with auto-fix (development)."""
    session.install("ruff")
    session.run(
        "ruff",
        "check",
        ".",
        "--fix",
        "--config",
        "config/ruff.toml",
    )
    session.run(
        "ruff",
        "format",
        ".",
        "--config",
        "config/ruff.toml",
    )


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright(session: nox.Session) -> None:
    """Run static type checks with default config."""
    session.install("-e", ".")
    session.install("pyright")
    session.run("pyright")


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright_legacy(session: nox.Session) -> None:
    """Run type checks for Python 3.9 compatibility on legacy implementation."""
    session.install("-e", ".")
    session.install("pyright")
    session.run("pyright", "-p", "config/pyrightconfig-legacy.json")


@nox.session(venv_backend="uv", tags=["typecheck"])
def pyright_modern(session: nox.Session) -> None:
    """Run type checks for Python 3.11+ features on modern implementation."""
    session.install("-e", ".")
    session.install("pyright")
    session.run("pyright", "-p", "config/pyrightconfig-modern.json")


@nox.session(python=VERSIONS, venv_backend="uv")
def test_all_tests(session: nox.Session) -> None:
    session.install("-e", ".")
    session.install("pytest")
    session.run("pytest")
