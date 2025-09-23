# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.2] - 2025-09-22

### Fixed

- **FastAPI Data Injection**: Fixed critical `UnboundLocalError` in FastAPI router handlers
  - Fixed `create_handler` function to properly accept model data as parameter for FastAPI dependency injection
  - Fixed `update_handler` function to handle both path parameters and request body data correctly
  - Added `request_model` field to `RouteDefinition` class to specify request body models for FastAPI
  - Updated `FastAPIAdapter.add_route()` to create proper wrapper functions for POST/PUT/PATCH requests
  - Fixed type annotations for handler function parameters (`Optional[T]` and `Optional[Dict[str, Any]]`)

### Changed

- **Router System**: Enhanced FastAPI integration with proper request body handling
  - POST routes now properly accept model data through FastAPI's dependency injection
  - PATCH routes now handle both path parameters (`pk`) and request body data
  - Added support for `request_model` in route definitions to specify request body types

### Technical Details

- Fixed `UnboundLocalError: cannot access local variable 'item' where it is not associated with a value`
- Resolved FastAPI route handler parameter mismatch issues
- Updated `RouteDefinition` class to include `request_model` parameter
- Enhanced `FastAPIAdapter` to create proper wrapper functions for different HTTP methods
- Fixed type safety issues with optional parameters in handler functions

## [1.0.1] - 2025-09-09

### Fixed

- **Package Import Issues**: Fixed critical import errors that prevented the package from being used after installation
  - Restructured package directory from `src/` to `src/py_hexagonal_arch/` for proper Python package structure
  - Fixed all relative imports throughout the codebase using proper dot notation (e.g., `from ..ports.repository import`)
  - Corrected import statements in controllers, models, schemas, and all adapter modules
  - Fixed metadata import issue in `schemas/user.py` by using `BaseSchema.metadata`
  - Updated package configuration in `pyproject.toml` to use correct version attribute path
  - Added missing `BaseSchema` import to main `__init__.py`

### Changed

- **Package Structure**: Moved all modules to proper `py_hexagonal_arch/` subdirectory structure
- **Import System**: All internal imports now use relative imports for better package isolation

### Technical Details

- Fixed `ModuleNotFoundError: No module named 'py_hexagonal_arch'` error
- Resolved `ModuleNotFoundError: No module named 'ports'` and similar import errors
- Package now installs and imports correctly with all components accessible
- All imports verified working: `from py_hexagonal_arch import BaseSchema, BaseController, CustomModel, etc.`

## [1.0.0] - 2025-09-09

### Added

- **Initial Release**: Complete hexagonal architecture framework
- **Multi-Framework Support**: FastAPI, Flask, and Tornado adapters
- **Multi-Database Support**: PostgreSQL, MariaDB/MySQL, SQL Server, Oracle
- **Multi-Cache Support**: Redis, MemCache, and In-Memory caching
- **Multi-Messaging Support**: Kafka, RabbitMQ, AWS Kinesis, GCP Pub/Sub
- **Repository Pattern**: Generic CRUD operations with filtering and relations
- **Router System**: Web framework abstraction with consistent API
- **Cache System**: Multi-backend caching with TTL support
- **Event System**: Multi-backend event messaging with pub/sub patterns
- **Type Safety**: Full type hints support with Pydantic models
- **Configuration Management**: Environment-based configuration system
- **Comprehensive Documentation**: Detailed README files for each component
- **Examples**: Complete working examples for all supported frameworks

### Features

- **Hexagonal Architecture**: Clean separation of concerns with ports and adapters
- **Async/Await Support**: Full asynchronous programming support
- **Connection Pooling**: Database connection pool management
- **Error Handling**: Robust error handling with HTTP exceptions
- **Filtering System**: Advanced filtering with multiple operators
- **Relation Loading**: Eager loading support for database relations
- **Transaction Support**: Database transaction management
- **Custom Adapters**: Easy extension with custom adapter registration
- **Environment Configuration**: Automatic configuration from environment variables
- **Development Tools**: Pre-commit hooks, linting, and testing setup

### Documentation

- **Main README**: Project overview and quick start guide
- **Router Documentation**: [`src/adapters/routers/README.md`](src/adapters/routers/README.md)
- **Cache Documentation**: [`src/adapters/caches/README.md`](src/adapters/caches/README.md)
- **Event Documentation**: [`src/adapters/events/README.md`](src/adapters/events/README.md)
- **Repository Documentation**: [`src/adapters/repositories/README.md`](src/adapters/repositories/README.md)
- **Examples**: Complete working examples in [`examples/`](examples/) directory

### Dependencies

- **Core**: Pydantic, FastAPI, SQLAlchemy, AsyncPG
- **Optional Web Frameworks**: Flask, Tornado
- **Optional Databases**: aiomysql, aioodbc, cx_oracle_async
- **Optional Cache**: Redis, aiomcache
- **Optional Messaging**: aiokafka, aio-pika, aioboto3, google-cloud-pubsub

### Package Structure

```bash
py-hexagonal-arch/
├── src/
│   ├── adapters/          # Adapter implementations
│   │   ├── routers/       # Web framework adapters
│   │   ├── repositories/  # Database adapters
│   │   ├── caches/        # Cache adapters
│   │   └── events/        # Event messaging adapters
│   ├── ports/             # Port interfaces
│   ├── controllers/       # Base controllers
│   ├── models/            # Domain models
│   ├── schemas/           # Data schemas
│   └── config/            # Configuration management
├── examples/              # Working examples
└── docs/                  # Documentation
```

### Installation

```bash
# Basic installation
pip install py-hexagonal-arch

# With specific extras
pip install py-hexagonal-arch[redis,kafka]

# Full installation
pip install py-hexagonal-arch[all]
```

### Supported Python Versions

- Python 3.8+
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### License

MIT License - see [LICENSE](LICENSE) for details.

---

## [Unreleased]

### Planned Features

- **NoRest Support**: SOAP, GraphQL adapter for web frameworks
- **NoSQL Support**: MongoDB, Neo4j adapters
- **Testing Utilities**: Test and fixtures

### Roadmap

- **v1.1.0**: Initial Project

---

For migration guides and detailed upgrade instructions, see the [Migration Guide](docs/MIGRATION.md).
