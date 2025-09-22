# SplashStand Project Context

## Project Overview

SplashStand is a mobile-first modular micro-CMS (Content Management System) built with Python. The project uses a modern tech stack including Flask, SQLAlchemy, Redis, and various Google Cloud services. It's designed to be simple, safe, serverless, and schema-based.

The project appears to have evolved over time, with both older Flask-based components (in the `whiskey` directory) and newer components using modern Python frameworks like Starlette, HTMX, Jinja, HTTPX, SQLAdmin, SQLModel, and Pydantic.

## Key Technologies

- **Core Framework**: Python 3.13+
- **Web Framework**: Flask (legacy) and FastBlocks (modern)
- **Database**: SQLAlchemy with SQLModel
- **Frontend**: HTMX, Jinja2 templates
- **Authentication**: Firebase Admin, Flask-Security
- **Caching**: Redis
- **Cloud Services**: Google Cloud Platform (Cloud Run, Cloud SQL, Cloud Storage)
- **Deployment**: Docker, Google Cloud Build
- **Package Management**: uv, PDM
- **Code Quality**: Black, Ruff, Pyright, Crackerjack

## Project Structure

```
splashstand/
├── splashstand/           # Main source code
│   ├── whiskey/          # Legacy Flask-based CMS
│   ├── adapters/         # Component adapters (admin, analytics, app, auth, etc.)
│   ├── actions/          # Business logic actions
│   ├── bin/              # Command-line utilities
│   ├── functions/        # Cloud functions
│   ├── public/           # Static files
│   └── cli.py           # Command-line interface
├── tests/                # Test files
├── docs/                 # Documentation
└── ...
```

## Building and Running

### Development Setup

1. Install dependencies with `uv`:

   ```bash
   uv sync
   ```

1. Run the development server:

   ```bash
   python -m splashstand
   ```

### CLI Commands

The project provides a CLI with several useful commands:

- `startproject` - Create a new project
- `upgradeproject` - Upgrade an existing project
- `checkversions` - Check dependency versions

Additional commands are available through the `cli.py` module:

- `deploy` - Build and deploy the application
- `create` - Create a new application
- `reset` - Reset debug settings
- `add_custom_domain` - Add a custom domain to Cloud Run

### Deployment

Deployment is handled through Google Cloud Run:

1. Build the Docker image
1. Deploy to Cloud Run with appropriate settings
1. Configure domain mappings
1. Set up Cloud Scheduler for keep-warm tasks

## Development Conventions

### Code Style

The project follows strict code quality standards:

- Formatting with Black
- Linting with Ruff
- Type checking with Pyright
- Code style enforcement with Crackerjack

### Testing

Tests are written using pytest with the following configuration:

- Async support with pytest-asyncio
- Coverage reporting
- Benchmark testing capabilities

### Package Management

The project uses uv for fast package management and PDM for project metadata management. Dependencies are specified in `pyproject.toml`.

### Configuration

Configuration is managed through YAML files and environment variables. The project uses a component-based architecture with adapters for different services.

## Key Components

1. **Whiskey** - Legacy Flask-based CMS implementation
1. **FastBlocks** - Modern web framework based on Starlette
1. **ACB** - Adapter Component Bus for dependency injection
1. **Adapters** - Pluggable components for various services (mail, auth, analytics, etc.)

## Important Files

- `pyproject.toml` - Project metadata and dependencies
- `splashstand/cli.py` - Main CLI interface
- `splashstand/main.py` - Application entry point
- `splashstand/whiskey/main.py` - Legacy Flask application
- `splashstand/bin/startproject.py` - Project creation utility

## Development Workflow

1. Create a new project using `startproject`
1. Configure settings in YAML files
1. Develop features using the component adapter pattern
1. Test with pytest
1. Deploy using the built-in deployment commands

## Version Information

The project has multiple version indicators:

- `VERSION` file: 1.1.0
- `splashstand/whiskey/_version.py`: 1.2.1
- `pyproject.toml`: 3.0.6

This suggests the project is in active development with different components at different version levels.
