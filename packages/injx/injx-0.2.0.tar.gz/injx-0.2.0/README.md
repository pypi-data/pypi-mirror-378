# Injx - Type-Safe Dependency Injection

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![Type Checked](https://img.shields.io/badge/type--checked-basedpyright-blue.svg)](https://github.com/DetachHead/basedpyright)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Docs](https://img.shields.io/badge/docs-mkdocs--material-informational)](https://qriusglobal.github.io/injx/)

> **Status: Alpha** — Ready for early adoption in SDK libraries and greenfield projects. APIs may change. Not recommended for production use without thorough testing.

## Project Status

[![PyPI Version](https://img.shields.io/pypi/v/injx.svg?logo=pypi&label=PyPI)](https://pypi.org/project/injx/)
[![Python Versions](https://img.shields.io/pypi/pyversions/injx.svg?logo=python&logoColor=white)](https://pypi.org/project/injx/)
[![Tests & Linting](https://github.com/QriusGlobal/injx/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/QriusGlobal/injx/actions/workflows/ci.yml)
[![Docs Build](https://github.com/QriusGlobal/injx/actions/workflows/docs.yml/badge.svg?branch=main)](https://github.com/QriusGlobal/injx/actions/workflows/docs.yml)
[![codecov](https://codecov.io/gh/QriusGlobal/injx/branch/main/graph/badge.svg)](https://codecov.io/gh/QriusGlobal/injx)
[![License: Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Typing: strict](https://img.shields.io/badge/typing-strict-blue?logo=python)](#)
[![Linting: Ruff](https://img.shields.io/badge/linting-ruff-46a2f1?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-46a2f1?logo=ruff&logoColor=white)](https://docs.astral.sh/ruff/formatter/)

Type-safe dependency injection container for Python 3.13+.

## Features

- Thread-safe and async-safe resolution using ContextVar isolation
- O(1) token lookups with pre-computed hashes
- O(1) circular dependency detection using set-based tracking
- Automatic resource cleanup in LIFO order
- Protocol-based type safety with static type checking
- Metaclass auto-registration for declarative patterns
- Zero external dependencies
- PEP 561 compliant with py.typed marker
- Memory-efficient singleton management

## Architecture

### Pure Python Implementation
Injx uses pure Python without C extensions:
- No platform-specific compilation requirements
- Standard Python debugging tools work without modification
- No segmentation faults from C extension issues
- Consistent behavior across all Python environments

### Async Handling
Explicit `get()` and `aget()` methods for synchronous and asynchronous resolution:
- Synchronous `get()` raises `AsyncCleanupRequiredError` for async providers
- Asynchronous `aget()` properly awaits async providers
- No implicit async mode switching
- Clear separation of sync and async code paths

### Token System
Strongly-typed `Token[T]` instances as container keys:
- Type information preserved at runtime
- Pre-computed hashes for O(1) lookups
- No string-based token resolution
- Tokens are immutable and hashable

### Registration Model
Explicit provider registration without auto-discovery:
- All dependencies must be explicitly registered
- No module scanning or import hooks
- No decorator-based auto-registration
- Registration happens at container initialization

## Documentation

Full docs: https://qriusglobal.github.io/injx/

## Quick Start

```bash
# Install with UV (recommended)
uv add injx

# Or with pip
pip install injx
```

### Basic Usage (Recommended Pattern)

```python
from typing import Protocol
from injx import Container, Token, Scope, inject

# Define interfaces
class Logger(Protocol):
    def info(self, message: str) -> None: ...

class Database(Protocol):
    def query(self, sql: str) -> list[dict[str, str]]: ...

# Implementations
class ConsoleLogger:
    def info(self, message: str) -> None:
        print(f"INFO: {message}")

class PostgreSQLDatabase:
    def query(self, sql: str) -> list[dict[str, str]]:
        # Implementation here
        return [{"result": "data"}]

# Create container and tokens
container = Container()
LOGGER = Token[Logger]("logger", scope=Scope.SINGLETON)
DATABASE = Token[Database]("database", scope=Scope.SINGLETON)

# Register providers
container.register(LOGGER, ConsoleLogger)
container.register(DATABASE, PostgreSQLDatabase)

# Use with @inject decorator (recommended)
@inject
def process_users(logger: Logger, db: Database) -> None:
    """Dependencies injected automatically via type annotations."""
    logger.info("Processing users")
    users = db.query("SELECT * FROM users")
    logger.info(f"Found {len(users)} users")

# Call without arguments - dependencies auto-resolved
process_users()

# Manual resolution also available
logger = container.get(LOGGER)
db = container.get(DATABASE)
```

### Async Support

```python
import asyncio
from typing import Protocol
from injx import Container, Token, Scope, inject

class AsyncDatabase(Protocol):
    async def connect(self) -> None: ...
    async def query(self, sql: str) -> list[dict[str, str]]: ...
    async def aclose(self) -> None: ...

class PostgreSQLAsyncDatabase:
    async def connect(self) -> None:
        print("Connecting to database...")
    
    async def query(self, sql: str) -> list[dict[str, str]]:
        return [{"id": "1", "name": "Alice"}]
    
    async def aclose(self) -> None:
        print("Closing database connection...")

# Setup
container = Container()
ASYNC_DB = Token[AsyncDatabase]("async_db", scope=Scope.SINGLETON)

async def create_db() -> AsyncDatabase:
    db = PostgreSQLAsyncDatabase()
    await db.connect()
    return db

container.register(ASYNC_DB, create_db)

# Async injection
@inject
async def process_users_async(db: AsyncDatabase) -> None:
    users = await db.query("SELECT * FROM users")
    print(f"Processed {len(users)} users")

# Usage
async def main() -> None:
    await process_users_async()
    await container.aclose()  # Proper cleanup

asyncio.run(main())
```

## Type Safety & Static Analysis

injx provides full static type checking support:

### PEP 561 Compliance

injx includes a `py.typed` marker file and provides complete type information:

```bash
# Works with all type checkers
mypy your_code.py
basedpyright your_code.py
pyright your_code.py
```

### Type-Safe Registration

```python
from typing import Protocol
from injx import Container, Token, Scope

class UserService(Protocol):
    def get_user(self, id: int) -> dict[str, str]: ...

class DatabaseUserService:
    def get_user(self, id: int) -> dict[str, str]:
        return {"id": str(id), "name": "User"}

container = Container()
USER_SERVICE = Token[UserService]("user_service", scope=Scope.SINGLETON)

# Type-safe registration - mypy/basedpyright will verify compatibility
container.register(USER_SERVICE, DatabaseUserService)  # ✅ OK

# This would fail type checking:
# container.register(USER_SERVICE, str)  # ❌ Type error
```

### Protocol-Based Injection

```python
from typing import Protocol, runtime_checkable
from injx import Container, Token, inject

@runtime_checkable
class EmailService(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> bool: ...

class SMTPEmailService:
    def send_email(self, to: str, subject: str, body: str) -> bool:
        print(f"Sending email to {to}: {subject}")
        return True

# Registration with runtime protocol validation
container = Container()
EMAIL_SERVICE = Token[EmailService]("email", scope=Scope.SINGLETON)
container.register(EMAIL_SERVICE, SMTPEmailService)

# Type-safe injection
@inject
def send_welcome_email(email_service: EmailService, user_email: str) -> None:
    """email_service parameter is automatically injected."""
    email_service.send_email(
        to=user_email,
        subject="Welcome!",
        body="Thanks for joining us."
    )

# Usage - only provide non-injected arguments
send_welcome_email(user_email="user@example.com")
```

## Injection Patterns Guide

### Plain Type Annotations with @inject

```python
from injx import inject

@inject  # Uses default container
def business_logic(logger: Logger, db: Database, user_id: int) -> None:
    """Dependencies are automatically resolved based on type annotations."""
    logger.info(f"Processing user {user_id}")
    db.query("SELECT * FROM users WHERE id = ?", user_id)

# Call with regular parameters only
business_logic(user_id=123)
```

### Inject[T] Markers for Custom Providers

```python
from typing import Annotated
from injx import inject, Inject

@inject
def advanced_handler(
    # Regular injection
    logger: Logger,
    
    # With custom provider
    cache: Annotated[Cache, Inject(lambda: MockCache())],
    
    # Regular parameter
    request_id: str
) -> None:
    logger.info(f"Handling request {request_id}")
    cache.set("last_request", request_id)
```

### Anti-Patterns

```python
# Incorrect: Using Inject[T] as type annotation with None default
def bad_handler(logger: Inject[Logger] = None) -> None:
    # Type checkers cannot infer the actual type
    pass

# Incorrect: Using Inject[T] without custom provider
def confusing_handler(logger: Inject[Logger]) -> None:
    # Use plain Logger annotation instead
    pass

# Correct: Plain type annotation
@inject
def good_handler(logger: Logger) -> None:
    logger.info("Resolved from container")

# Correct: Override in tests
@inject  
def handler(logger: Logger) -> None:
    logger.info("Logger injected from container")

# Test override:
container.override(LOGGER, MockLogger())
```

## Core Features

### 1. Contextual Scoping

```python
from injx import Container, ContextualContainer, Token, Scope

# Contextual container supports request/session scopes
container = Container()  # Inherits from ContextualContainer

USER_TOKEN = Token[User]("current_user", scope=Scope.REQUEST)
SESSION_TOKEN = Token[Session]("session", scope=Scope.SESSION)

def get_current_user() -> User:
    return User(id=123, name="Alice")

def get_session() -> Session:
    return Session(id="sess_456", user_id=123)

container.register(USER_TOKEN, get_current_user)
container.register(SESSION_TOKEN, get_session)

# Request scope - each request gets isolated dependencies
with container.request_scope():
    user1 = container.get(USER_TOKEN)
    user2 = container.get(USER_TOKEN)
    assert user1 is user2  # Same instance within request scope

with container.request_scope():
    user3 = container.get(USER_TOKEN)
    assert user1 is not user3  # Different instance in new scope

# Session scope - longer-lived than request
with container.session_scope():
    with container.request_scope():
        session = container.get(SESSION_TOKEN)
        # Session persists across multiple requests
```

### 2. TokenFactory for Convenient Creation

```python
from injx import Container, TokenFactory, Scope

container = Container()
# TokenFactory provides convenient methods
factory = container.tokens  # Built-in factory

# Convenient creation methods
LOGGER = factory.singleton("logger", Logger)
CACHE = factory.request("cache", CacheService) 
CONFIG = factory.session("config", Configuration)
TEMP_FILE = factory.transient("temp_file", TempFile)

# With qualifiers for multiple instances
PRIMARY_DB = factory.qualified("primary", Database, Scope.SINGLETON)
SECONDARY_DB = factory.qualified("secondary", Database, Scope.SINGLETON)

# Register providers
container.register(PRIMARY_DB, lambda: PostgreSQLDatabase("primary"))
container.register(SECONDARY_DB, lambda: PostgreSQLDatabase("secondary"))
```

### 3. Default Container Support

```python
from injx import get_default_container, set_default_container, inject

# Set up global default container
default_container = Container()
set_default_container(default_container)

# Register global services
LOGGER = Token[Logger]("logger", scope=Scope.SINGLETON)
default_container.register(LOGGER, ConsoleLogger)

# @inject uses default container when none specified
@inject
def handler(logger: Logger) -> None:
    logger.info("Using default container")

# Anywhere in your app
current_container = get_default_container()
```

### 4. Resource Cleanup with Context Managers

```python
import asyncio
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator
from injx import Container, Token, Scope

# Sync context manager
@contextmanager 
def database_connection() -> Generator[Database, None, None]:
    print("Opening database connection")
    db = PostgreSQLDatabase()
    try:
        yield db
    finally:
        print("Closing database connection")
        db.close()

# Async context manager
@asynccontextmanager
async def async_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    print("Creating HTTP client")
    client = httpx.AsyncClient()
    try:
        yield client
    finally:
        print("Closing HTTP client")
        await client.aclose()

# Register context managers
container = Container()
DB_TOKEN = Token[Database]("database", scope=Scope.SINGLETON)
HTTP_TOKEN = Token[httpx.AsyncClient]("http_client", scope=Scope.SINGLETON)

container.register_context_sync(DB_TOKEN, database_connection)
container.register_context_async(HTTP_TOKEN, async_http_client)

# Automatic cleanup
async def main() -> None:
    # Resources created on first access
    db = container.get(DB_TOKEN)
    client = await container.aget(HTTP_TOKEN)
    
    # Proper cleanup in LIFO order
    await container.aclose()

asyncio.run(main())
```

### 5. Given Instances (Scala-Style)

```python
from injx import Container, Given, inject

class UserService:
    def __init__(self, db: Database):
        self.db = db

# Scala-inspired given instances
container = Container()

# Register "given" providers
container.given(Database, lambda: PostgreSQLDatabase())
container.given(Logger, lambda: ConsoleLogger())

@inject
def process_request(
    user_service: Given[UserService],  # Resolved from given instances
    request_id: str
) -> None:
    # user_service automatically constructed with given Database
    pass
```

## Advanced Patterns

### Async-Safe Singleton Initialization

```python
import asyncio
from injx import Container, Token, Scope

# Thread-safe async singleton creation
async def create_expensive_service() -> ExpensiveService:
    print("Creating expensive service...")
    await asyncio.sleep(0.1)  # Simulate expensive initialization
    return ExpensiveService()

container = Container()
SERVICE_TOKEN = Token[ExpensiveService]("expensive", scope=Scope.SINGLETON)
container.register(SERVICE_TOKEN, create_expensive_service)

async def concurrent_access() -> None:
    # Multiple concurrent accesses - only one instance created
    tasks = [container.aget(SERVICE_TOKEN) for _ in range(100)]
    services = await asyncio.gather(*tasks)
    
    # All references point to the same instance
    assert all(s is services[0] for s in services)
    print(f"All {len(services)} references are identical")

asyncio.run(concurrent_access())
```

### Circular Dependency Detection

```python
from injx import Container, Token, CircularDependencyError

class ServiceA:
    def __init__(self, service_b: 'ServiceB'):
        self.service_b = service_b

class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a

container = Container()
SERVICE_A = Token[ServiceA]("service_a")
SERVICE_B = Token[ServiceB]("service_b")

# This creates a circular dependency
container.register(SERVICE_A, lambda: ServiceA(container.get(SERVICE_B)))
container.register(SERVICE_B, lambda: ServiceB(container.get(SERVICE_A)))

try:
    container.get(SERVICE_A)
except CircularDependencyError as e:
    print(f"Circular dependency detected: {e}")
    # Output: Cannot resolve token 'service_a':
    #   Resolution chain: service_a -> service_b -> service_a
    #   Cause: Circular dependency detected
```

### Type-Safe Override System

```python
from unittest.mock import Mock
from injx import Container, Token

# Production setup
container = Container()
EMAIL_SERVICE = Token[EmailService]("email", scope=Scope.SINGLETON)
container.register(EMAIL_SERVICE, SMTPEmailService)

# Type-safe testing with overrides
def test_email_functionality() -> None:
    # Create type-safe mock
    mock_email = Mock(spec=EmailService)
    mock_email.send_email.return_value = True
    
    # Override for testing - type checked!
    container.override(EMAIL_SERVICE, mock_email)
    
    @inject
    def send_notification(email_service: EmailService) -> bool:
        return email_service.send_email("test@example.com", "Test", "Body")
    
    # Test uses mock
    result = send_notification()
    assert result is True
    mock_email.send_email.assert_called_once()
    
    # Cleanup override
    container.clear_overrides()
```

## Framework Integration

### FastAPI Integration

```python
from typing import Annotated
from fastapi import FastAPI, Depends
from injx import Container, Token, Scope, inject

# Setup DI container
app = FastAPI()
container = Container()

# Register services
USER_SERVICE = Token[UserService]("user_service", scope=Scope.SINGLETON)
EMAIL_SERVICE = Token[EmailService]("email_service", scope=Scope.SINGLETON)

container.register(USER_SERVICE, lambda: DatabaseUserService())
container.register(EMAIL_SERVICE, lambda: SMTPEmailService())

# FastAPI dependency provider
def get_container() -> Container:
    return container

# Option 1: FastAPI-style dependencies
@app.post("/users")
async def create_user(
    user_data: UserCreateRequest,
    user_service: Annotated[UserService, Depends(lambda: container.get(USER_SERVICE))],
    email_service: Annotated[EmailService, Depends(lambda: container.get(EMAIL_SERVICE))]
) -> UserResponse:
    user = user_service.create_user(user_data)
    email_service.send_email(user.email, "Welcome!", "Welcome to our service")
    return UserResponse.from_user(user)

# Option 2: injx @inject decorator (cleaner)
@app.post("/users-v2")
@inject(container=container)
async def create_user_v2(
    user_data: UserCreateRequest,
    user_service: UserService,  # Auto-injected
    email_service: EmailService  # Auto-injected
) -> UserResponse:
    user = user_service.create_user(user_data)
    email_service.send_email(user.email, "Welcome!", "Welcome to our service")
    return UserResponse.from_user(user)

# Request-scoped dependencies
@app.middleware("http")
async def setup_request_scope(request, call_next):
    async with container.async_request_scope():
        response = await call_next(request)
    return response

# Startup/shutdown
@app.on_event("startup")
async def startup():
    # Initialize resources
    pass

@app.on_event("shutdown") 
async def shutdown():
    await container.aclose()
```

### Django Integration

```python
# settings.py
from injx import Container, Token, Scope, set_default_container

# Global container setup
DI_CONTAINER = Container()
set_default_container(DI_CONTAINER)

# Register services
USER_SERVICE = Token[UserService]("user_service", scope=Scope.SINGLETON)
EMAIL_SERVICE = Token[EmailService]("email_service", scope=Scope.SINGLETON)

DI_CONTAINER.register(USER_SERVICE, lambda: DjangoUserService())
DI_CONTAINER.register(EMAIL_SERVICE, lambda: DjangoEmailService())

# views.py
from django.http import JsonResponse
from injx import inject

@inject  # Uses default container
def create_user_view(
    request,
    user_service: UserService,  # Auto-injected
    email_service: EmailService  # Auto-injected
) -> JsonResponse:
    if request.method == 'POST':
        user_data = json.loads(request.body)
        user = user_service.create_user(user_data)
        email_service.send_welcome_email(user.email)
        return JsonResponse({"user_id": user.id})
    
    return JsonResponse({"error": "Method not allowed"}, status=405)
```

### CLI Applications with Click

```python
import click
from injx import Container, Token, Scope, inject

# Setup container
container = Container()
CONFIG_SERVICE = Token[ConfigService]("config", scope=Scope.SINGLETON)
LOGGER = Token[Logger]("logger", scope=Scope.SINGLETON)

container.register(CONFIG_SERVICE, lambda: FileConfigService("config.yml"))
container.register(LOGGER, lambda: ConsoleLogger())

@click.group()
@click.pass_context
def cli(ctx):
    """CLI application with dependency injection."""
    ctx.obj = container

@cli.command()
@click.argument('name')
@click.pass_context
@inject  # Can access container via click context
def greet(ctx, name: str, logger: Logger) -> None:
    """Greet a user with proper logging."""
    logger.info(f"Greeting user: {name}")
    click.echo(f"Hello, {name}!")

@cli.command()
@click.pass_context
@inject
def status(ctx, config: ConfigService, logger: Logger) -> None:
    """Show application status."""
    logger.info("Checking application status")
    version = config.get("version", "unknown")
    click.echo(f"Application version: {version}")

if __name__ == "__main__":
    cli()
```

## Testing Patterns

### Unit Testing with Dependency Overrides

```python
import pytest
from unittest.mock import Mock, MagicMock
from injx import Container, Token, Scope

class TestUserService:
    def setup_method(self):
        """Setup for each test method."""
        self.container = Container()
        
        # Register production dependencies
        self.db_token = Token[Database]("database", scope=Scope.SINGLETON)
        self.email_token = Token[EmailService]("email", scope=Scope.SINGLETON)
        self.user_service_token = Token[UserService]("user_service")
        
        self.container.register(self.db_token, PostgreSQLDatabase)
        self.container.register(self.email_token, SMTPEmailService)
        self.container.register(
            self.user_service_token,
            lambda: UserService(
                db=self.container.get(self.db_token),
                email=self.container.get(self.email_token)
            )
        )
    
    def test_create_user_success(self):
        """Test successful user creation with mocked dependencies."""
        # Create type-safe mocks
        mock_db = Mock(spec=Database)
        mock_email = Mock(spec=EmailService)
        
        mock_db.create_user.return_value = User(id=1, email="test@example.com")
        mock_email.send_welcome_email.return_value = True
        
        # Override dependencies for this test
        self.container.override(self.db_token, mock_db)
        self.container.override(self.email_token, mock_email)
        
        # Get service with mocked dependencies
        user_service = self.container.get(self.user_service_token)
        
        # Test
        user = user_service.create_user("test@example.com")
        
        # Verify
        assert user.id == 1
        mock_db.create_user.assert_called_once_with("test@example.com")
        mock_email.send_welcome_email.assert_called_once_with("test@example.com")
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.container.clear_overrides()

### Async Testing

```python
import asyncio
import pytest
from unittest.mock import AsyncMock
from injx import Container, Token, Scope

@pytest.mark.asyncio
async def test_async_user_service():
    """Test async service with async mocked dependencies."""
    container = Container()
    
    # Setup tokens
    async_db_token = Token[AsyncDatabase]("async_db", scope=Scope.SINGLETON)
    async_email_token = Token[AsyncEmailService]("async_email", scope=Scope.SINGLETON)
    
    # Create async mocks
    mock_async_db = AsyncMock(spec=AsyncDatabase)
    mock_async_email = AsyncMock(spec=AsyncEmailService)
    
    mock_async_db.create_user.return_value = User(id=1, email="test@example.com")
    mock_async_email.send_welcome_email.return_value = True
    
    # Override with mocks
    container.override(async_db_token, mock_async_db)
    container.override(async_email_token, mock_async_email)
    
    # Test with @inject decorator
    @inject(container=container)
    async def create_user_workflow(
        email: str,
        db: AsyncDatabase,
        email_service: AsyncEmailService
    ) -> User:
        user = await db.create_user(email)
        await email_service.send_welcome_email(email)
        return user
    
    # Execute test
    user = await create_user_workflow("test@example.com")
    
    # Verify
    assert user.id == 1
    mock_async_db.create_user.assert_called_once_with("test@example.com")
    mock_async_email.send_welcome_email.assert_called_once_with("test@example.com")

### Request-Scoped Testing

```python
def test_request_scoped_dependencies():
    """Test request-scoped dependency isolation."""
    container = Container()
    request_service_token = Token[RequestService]("request_service", scope=Scope.REQUEST)
    
    container.register(request_service_token, lambda: RequestService())
    
    # Request 1
    with container.request_scope():
        service1a = container.get(request_service_token) 
        service1b = container.get(request_service_token)
        assert service1a is service1b  # Same instance within scope
    
    # Request 2
    with container.request_scope():
        service2 = container.get(request_service_token)
        assert service1a is not service2  # Different instance in new scope
```

## Performance Optimizations

### Performance Characteristics

- Token lookups: O(1) with pre-computed hashes
- Cycle detection: O(1) using set-based tracking  
- Memory overhead: ~500 bytes per registered service
- Singleton access: Constant time after initial creation
- Transient scope: No caching, new instance per resolution

### O(1) Token Lookups

```python
from injx import Container, Token, TokenFactory

# Tokens use pre-computed hashes for O(1) lookups
container = Container()
factory = TokenFactory()

# Create many tokens - lookups remain constant time
tokens = [
    factory.singleton(f"service_{i}", type(f"Service{i}", (), {}))
    for i in range(1000)
]

# Register all services
for i, token in enumerate(tokens):
    container.register(token, lambda i=i: f"Service instance {i}")

# Resolution time is O(1) regardless of container size
service_500 = container.get(tokens[500])  # Same speed as tokens[0]
```

### Cached Injection Metadata

```python
from injx import inject

# Function signature analysis is cached automatically
@inject  # Analysis cached on first call
def expensive_handler(
    service1: Service1,
    service2: Service2,
    service3: Service3,
    regular_param: str
) -> None:
    pass

# Subsequent calls use cached metadata - no re-analysis
expensive_handler(regular_param="test")  # Fast
expensive_handler(regular_param="test2") # Fast
```

### Memory-Efficient Resource Management

```python
from weakref import WeakValueDictionary
from injx import Container, Token, Scope

# Transient dependencies use weak references for automatic cleanup
container = Container()

# These don't prevent garbage collection
TEMP_TOKEN = Token[TempService]("temp", scope=Scope.TRANSIENT)
container.register(TEMP_TOKEN, lambda: TempService())

temp_service = container.get(TEMP_TOKEN)
# When temp_service goes out of scope, it can be garbage collected
# Container doesn't hold strong references to transient instances
```

## Error Handling and Debugging

### Detailed Error Messages

```python
from injx import Container, Token, ResolutionError

container = Container()
SERVICE_A = Token[ServiceA]("service_a")
SERVICE_B = Token[ServiceB]("missing_service")

# Register only SERVICE_A, not SERVICE_B
container.register(SERVICE_A, lambda: ServiceA(container.get(SERVICE_B)))

try:
    container.get(SERVICE_A)
except ResolutionError as e:
    print(f"Resolution error: {e}")
    # Output:
    # Cannot resolve token 'missing_service':
    #   Resolution chain: service_a -> missing_service
    #   Cause: No provider registered for token 'missing_service'
    
    # Access structured error data
    print(f"Failed token: {e.token.name}")
    print(f"Resolution chain: {[t.name for t in e.chain]}")
    print(f"Root cause: {e.cause}")
```

### Debug Mode

```python
import logging
from injx import Container, Token

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("injx")

container = Container()
SERVICE_TOKEN = Token[DebugService]("debug_service", scope=Scope.SINGLETON)

container.register(SERVICE_TOKEN, lambda: DebugService())

# Resolution steps are logged in debug mode
service = container.get(SERVICE_TOKEN)
```

## Migration Guides

### From dependency-injector

```python
# Before (dependency-injector)
from dependency_injector import containers, providers

class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    database = providers.Singleton(
        Database,
        host=config.database.host,
        port=config.database.port
    )
    
    user_service = providers.Factory(
        UserService,
        db=database
    )

# After (injx)
from injx import Container, Token, Scope

container = Container()

# Define tokens
DATABASE = Token[Database]("database", scope=Scope.SINGLETON)
USER_SERVICE = Token[UserService]("user_service", scope=Scope.TRANSIENT)

# Register providers
container.register(
    DATABASE, 
    lambda: Database(
        host=config.get("database.host"),
        port=config.get("database.port")
    )
)

container.register(
    USER_SERVICE,
    lambda: UserService(db=container.get(DATABASE))
)
```

### From injector

```python
# Before (injector)
from injector import Injector, inject, singleton

injector = Injector()
injector.binder.bind(Database, to=PostgreSQLDatabase, scope=singleton)

@inject
def user_handler(db: Database) -> None:
    pass

# After (injx) 
from injx import Container, Token, Scope, inject

container = Container()
DATABASE = Token[Database]("database", scope=Scope.SINGLETON)
container.register(DATABASE, PostgreSQLDatabase)

@inject(container=container)  # or set as default container
def user_handler(db: Database) -> None:
    pass
```

## Development Setup

```bash
# Clone repository
git clone https://github.com/qriusglobal/injx.git
cd injx

# Install with development dependencies
uv sync

# Run tests with coverage
uv run pytest --cov=injx --cov-report=html

# Type checking (strict mode)
uvx basedpyright src

# Format and lint
uvx ruff format .
uvx ruff check . --fix

# Run all quality checks
uvx ruff check . && uvx basedpyright src && uv run pytest -q
```

### Running Tests

```bash
# All tests
uv run pytest

# Specific test categories
uv run pytest tests/test_container.py          # Core container tests
uv run pytest tests/test_injection.py         # Injection decorator tests  
uv run pytest tests/test_contextual.py        # Scoping tests
uv run pytest tests/test_async.py             # Async tests
uv run pytest tests/test_performance.py       # Performance benchmarks
uv run pytest tests/integration/              # Integration tests

# With coverage
uv run pytest --cov=injx --cov-report=term-missing
```

## Best Practices

### 1. Token Organization

```python
# tokens.py - Centralize token definitions
from injx import TokenFactory, Token
from typing import Protocol

# Use factory for consistency
factory = TokenFactory()

# Group related tokens
class DatabaseTokens:
    PRIMARY = factory.singleton("primary_db", Database)
    SECONDARY = factory.singleton("secondary_db", Database)
    CACHE = factory.request("cache", CacheService)

class ServiceTokens:
    USER_SERVICE = factory.singleton("user_service", UserService)
    EMAIL_SERVICE = factory.singleton("email_service", EmailService)
    AUTH_SERVICE = factory.request("auth_service", AuthService)

# Use protocols for flexibility
class Tokens:
    LOGGER = factory.singleton("logger", Logger)  # Protocol
    CONFIG = factory.singleton("config", Configuration)  # Concrete
```

### 2. Container Lifecycle Management

```python
# app.py - Application lifecycle
import asyncio
from contextlib import asynccontextmanager
from injx import Container, set_default_container

@asynccontextmanager
async def lifespan():
    """Manage container lifecycle."""
    # Startup
    container = Container()
    await setup_dependencies(container)
    set_default_container(container)
    
    try:
        yield container
    finally:
        # Shutdown - cleanup resources
        await container.aclose()

async def setup_dependencies(container: Container) -> None:
    """Register all application dependencies."""
    # Register database connections
    container.register(DatabaseTokens.PRIMARY, create_primary_db)
    container.register(DatabaseTokens.SECONDARY, create_secondary_db)
    
    # Register services
    container.register(ServiceTokens.USER_SERVICE, create_user_service)
    container.register(ServiceTokens.EMAIL_SERVICE, create_email_service)

async def main():
    async with lifespan() as container:
        # Application code here
        await run_application()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Testing Strategy

```python
# test_base.py - Shared testing infrastructure
import pytest
from injx import Container
from unittest.mock import Mock

class DITestCase:
    """Base class for DI-enabled tests."""
    
    def setup_method(self):
        self.container = Container()
        self.mocks = {}
        
    def mock_service(self, token: Token[T], **kwargs) -> Mock:
        """Create and register a type-safe mock."""
        mock = Mock(spec=token.type_, **kwargs)
        self.container.override(token, mock)
        self.mocks[token.name] = mock
        return mock
        
    def teardown_method(self):
        self.container.clear_overrides()

# test_user_service.py - Concrete test
class TestUserService(DITestCase):
    
    def test_create_user(self):
        # Setup mocks
        mock_db = self.mock_service(DatabaseTokens.PRIMARY)
        mock_email = self.mock_service(ServiceTokens.EMAIL_SERVICE)
        
        mock_db.create_user.return_value = User(id=1, email="test@example.com")
        mock_email.send_welcome_email.return_value = True
        
        # Test
        user_service = self.container.get(ServiceTokens.USER_SERVICE)
        user = user_service.create_user("test@example.com")
        
        # Verify
        assert user.id == 1
        mock_db.create_user.assert_called_once()
        mock_email.send_welcome_email.assert_called_once()
```

## Troubleshooting

### Common Issues

**1. Circular Dependencies**
```python
# Problem: Services depend on each other
# Solution: Use lazy injection or redesign

# Instead of:
class ServiceA:
    def __init__(self, service_b: ServiceB): ...

class ServiceB:
    def __init__(self, service_a: ServiceA): ...

# Do:
class ServiceA:
    def __init__(self, get_service_b: Callable[[], ServiceB]): ...

# Or redesign to avoid circular dependency
```

**2. Type Checker Issues**
```python
# Problem: mypy/basedpyright can't infer types
# Solution: Use explicit type annotations

# Instead of:
@inject
def handler(service):  # Type unknown
    pass

# Do:
@inject  
def handler(service: UserService) -> None:  # Explicit types
    pass
```

**3. Async/Sync Mixing**
```python
# Problem: Using async resources in sync context
# Solution: Use appropriate container methods

# Instead of:
async def create_service():
    return AsyncService()

container.register(TOKEN, create_service)
service = container.get(TOKEN)  # ❌ Error: async provider in sync context

# Do:
service = await container.aget(TOKEN)  # ✅ Correct async usage
```

**4. Resource Leaks**
```python
# Problem: Resources not properly cleaned up
# Solution: Use context managers or proper cleanup

# Instead of:
def create_connection():
    return DatabaseConnection()  # May leak

# Do:
@contextmanager
def database_connection():
    conn = DatabaseConnection()
    try:
        yield conn
    finally:
        conn.close()

container.register_context_sync(DB_TOKEN, database_connection)
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all quality checks pass (`uvx ruff check . && uvx basedpyright src && uv run pytest`)
5. Submit a pull request

### Code Standards

- **Type safety**: All code must pass `basedpyright --strict`
- **Testing**: Maintain 90%+ test coverage
- **Documentation**: Update README for user-facing changes
- **Formatting**: Use `ruff format` (88 character lines)
- **Performance**: Maintain O(1) lookup guarantees

## Development Methodology

### AI-Assisted Development

This project has been developed with the assistance of AI Large Language Models (LLMs) following a **SPEC-driven development approach**. We believe in transparency about our development practices and the tools that help us deliver high-quality software.

#### Our Approach

- **Specification-First Design**: Every feature begins with clear, detailed specifications that define expected behavior, edge cases, and acceptance criteria
- **AI Pair Programming**: LLMs assist in code generation, review, and optimization while maintaining human oversight and decision-making
- **Test-Driven Validation**: All AI-generated code is validated through comprehensive test suites and human review
- **Iterative Refinement**: Continuous improvement through AI-assisted code analysis and refactoring suggestions

#### Benefits of AI-Assisted Development

- **Accelerated Development**: Faster implementation of well-defined features
- **Consistent Code Quality**: Adherence to established patterns and best practices
- **Enhanced Documentation**: Comprehensive docstrings and inline documentation
- **Reduced Boilerplate**: Efficient generation of repetitive code structures

#### Human Oversight

While AI tools significantly enhance our development workflow, all architectural decisions, API design choices, and critical implementation details are reviewed and approved by human developers. The AI serves as a powerful assistant, not a replacement for human expertise and judgment.

## License

injx is licensed under the **Apache License 2.0**.

This is a permissive open source license that allows you to use injx in both open source and proprietary projects. The Apache 2.0 license provides:

- **Freedom to use commercially**: Use injx in your commercial products without restrictions
- **Patent protection**: Explicit patent grant protects you from patent claims
- **Simple attribution**: Just include the license and copyright notice
- **Compatible with most licenses**: Works well with MIT, BSD, and other permissive licenses

See [LICENSE](LICENSE) for the full license text.

Copyright 2025 Qrius Global - Licensed under Apache License 2.0

