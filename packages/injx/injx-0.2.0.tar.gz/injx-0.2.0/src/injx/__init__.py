"""Injx - Type-safe dependency injection for modern Python.

Status: Alpha - APIs will change. Not recommended for production use.

Highlights:
- Immutable tokens with pre-computed hashes (O(1) lookups)
- ContextVar-based scoping for async and thread safety
- `@inject` decorator (FastAPI-inspired) and lightweight markers
- Scala-style "given" instances for ergonomic overrides
- Zero runtime dependencies

Quick start:
    from injx import Container, Token, Scope

    container = Container()
    DB = Token[Database]("database")
    container.register(DB, create_database, scope=Scope.SINGLETON)

    db = container.get(DB)
    # ... use db ...
"""

# Version from package metadata (single source of truth: pyproject.toml)
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("injx")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"

# Package metadata
__org__ = "QriusGlobal"
__author__ = "Qrius Global"
__email__ = "mishal@qrius.global"
__repo__ = "https://github.com/QriusGlobal/injx"
__docs__ = "https://qriusglobal.github.io/injx/"
from injx.container import Container
from injx.contextual import ContextualContainer, RequestScope, SessionScope
from injx.dependencies import Dependencies

# Compatibility imports - these will be deprecated
from injx.exceptions import (
    AsyncCleanupRequiredError,
    CircularDependencyError,
    InjxError,
    ResolutionError,
)
from injx.injection import Depends, Given, Inject, inject
from injx.metaclasses import Injectable
from injx.protocols.container import ContainerProtocol
from injx.tokens import Scope, Token, TokenFactory

__all__ = [
    # Core classes
    "Container",
    "Dependencies",
    "Token",
    "TokenFactory",
    "Scope",
    # Injection
    "inject",
    "Inject",
    "Given",
    "Depends",
    # Protocols
    "ContainerProtocol",
    # Scoping
    "ContextualContainer",
    "RequestScope",
    "SessionScope",
    # Compatibility
    "Injectable",
    # Exceptions
    "InjxError",
    "ResolutionError",
    "CircularDependencyError",
    "AsyncCleanupRequiredError",
    # Deprecated (will be removed in v2.0.0)
    "get_default_container",
    "set_default_container",
    # Metadata
    "__version__",
    "__author__",
    "__docs__",
    "__email__",
    "__org__",
    "__repo__",
]


# Compatibility functions with deprecation warnings
def get_default_container() -> Container:
    """Deprecated: Use Container.get_active() instead.

    Will be removed in v2.0.0.
    """
    import warnings

    warnings.warn(
        "get_default_container() is deprecated and will be removed in v2.0.0. "
        "Use Container.get_active() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    return Container.get_active()


def set_default_container(container: Container | None) -> None:
    """Deprecated: Use Container.set_active() instead.

    Will be removed in v2.0.0.
    """
    import warnings

    warnings.warn(
        "set_default_container() is deprecated and will be removed in v2.0.0. "
        "Use Container.set_active() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    Container.set_active(container)
