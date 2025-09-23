# Recurve Libraries

For the unified maintenance of public components of the Recurve platform,
these codes may be used in both Server and Executor (Worker) environments. 

Only Python 3.11+ are supported.

## Components

This code repository consists of the following core components:

### Core
The foundation of the Recurve platform that provides:

- Base classes and interfaces for platform components
- Jinja2 templating engine integration
- Core configuration management
- Common platform abstractions

### Utils
A comprehensive utility library offering:

- Time handling and date manipulation
- Concurrent processing tools
- File system operations and path handling
- String manipulation and text processing
- Logging and error handling utilities
- Data validation helpers

### Connectors
A robust data connectivity layer supporting:
- Database connections (MySQL, PostgreSQL, Redshift, BigQuery, etc.)
- Cloud storage (S3, GCS, Azure Blob Storage)
- Messaging services and APIs
- Custom connector development framework

Note: Run `make update-connector-schema` after updating connector config schemas to regenerate config_schema.py

### Schedulers
Airflow integration components including:

- Custom Airflow operators and sensors
- DAG generation utilities
- Workflow scheduling interfaces
- Task dependency management

### Operators
Task-specific operators for:

- Data extraction and loading
- Data transformation and processing
- Running Python code
- Running SQL code
- Building and running DBT jobs


### Client
A flexible client interface providing:

- Platform API abstractions
- Authentication handling
- Resource management
- Extensible base classes for custom clients
- Connection pooling and retry logic

### Executors

Core job execution engine that:

- Manages job submissions and execution flows
- Orchestrates task execution on infrastructure
- Handles job lifecycle and state management
- Provides infrastructure abstraction layer

## Development Workflow

### Requirements management

We use `uv` to manage Python package dependencies. The workflow is:

1. Update source requirements in `.in` files:
   - [`requirements.in`](./requirements.in) - All dependencies
   - [`requirements/worker.in`](requirements/worker.in) - Worker-specific dependencies
   - [`requirements/dbt.in`](requirements/dbt.in) - DBT-specific dependencies
   - [`requirements-dev.in`](requirements-dev.in) - Development dependencies

2. Compile locked requirements:
   ```bash
   make compile-requirements  # Compiles all requirements files
   ```
   Or compile individual files:
   ```bash
   make compile-worker  # Just worker requirements
   make compile-dbt    # Just DBT requirements
   ```

3. After compiling requirements, update optional dependencies in pyproject.toml:
   ```bash
   make update-optional-deps
   ```

This ensures consistent dependencies across development and production environments.

### Release Process

1. Update version number in [`recurvedata/__version__.py`](recurvedata/__version__.py)
2. Build and publish package:
   ```bash
   make publish
   ```
   This will clean build artifacts, build new package, and publish to Recurve PyPI.

### Available Commands

The following make commands are available:

Build and Publishing:
- `make clean` - Remove build artifacts (dist directory)
- `make build` - Clean and build the package
- `make publish` - Build and publish package to Recurve PyPI

Requirements Management:
- `make upgrade-uv` - Upgrade the uv package installer
- `make compile-worker` - Compile worker-specific requirements
- `make compile-dbt` - Compile DBT-specific requirements
- `make compile-requirements` - Compile all requirements files and sync environment
- `make install-requirements` - Install requirements files

Maintenance Scripts:
- `make update-optional-deps` - Update optional dependencies in pyproject.toml
- `make update-connector-schema` - Update connector configuration schemas
