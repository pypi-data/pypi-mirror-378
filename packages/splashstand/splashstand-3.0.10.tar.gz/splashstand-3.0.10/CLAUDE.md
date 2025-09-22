# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SplashStand is a Python 3.13+ web application framework built on top of FastBlocks and ACB (Asynchronous Component Base). It provides "simple, safe, serverless, schema" development with a focus on modern web development patterns including HTMX, Jinja templating, and cloud-native deployment.

## Development Commands

### Essential Commands
- **Development server**: `uv run fastblocks dev` (from CLI integration)
- **Production server**: `uv run fastblocks run` (from CLI integration)
- **Install dependencies**: `uv sync`
- **Run tests**: `uv run pytest`
- **Type checking**: `uv run pyright` or `uv run zuban check --config-file mypy.ini ./splashstand`
- **Linting**: `uv run ruff check` and `uv run ruff format`
- **Security scan**: `uv run bandit -c pyproject.toml -r -ll splashstand/`
- **Dead code detection**: `skylos splashstand --exclude tests`
- **Dependency validation**: `uv run creosote`

### Pre-commit Hooks
The project uses comprehensive pre-commit hooks. Key stages:
- **pre-push/manual**: Type checking (pyright, zuban), security (bandit), complexity analysis (complexipy), dead code detection (skylos), refactoring suggestions (refurb)
- **standard**: Formatting (ruff), linting, spell checking (codespell), YAML/TOML validation

### Custom CLI Commands
SplashStand provides additional CLI commands via `splashstand/cli.py`:
- `get_revisions` - List Cloud Run service revisions
- `clean_revisions` - Clean up old revisions
- `clean_builds` - Clean up build artifacts
- `reset` - Reset application state
- `create` - Create new deployment
- `add_custom_domain` - Configure custom domain
- `build_revision` - Build and deploy revision

## Architecture Overview

### Core Structure
- **`splashstand/main.py`**: Application entry point using FastBlocks framework
- **`splashstand/cli.py`**: Extended CLI commands for deployment and management
- **`splashstand/adapters/`**: Modular adapter system for different services:
  - `admin/` - Administrative interfaces
  - `analytics/` - Google Analytics integration
  - `app/` - Core application logic
  - `auth/` - Firebase authentication
  - `captcha/` - reCAPTCHA integration
  - `mail/`, `messaging/`, `marketing/`, `social/` - Communication services
  - `pwa/` - Progressive Web App features
  - `schemas/` - Data validation schemas

### Framework Dependencies
- **FastBlocks**: Primary web framework providing admin, monitoring, and sitemap features
- **ACB**: Asynchronous Component Base providing cache, DNS, monitoring, requests, secrets, SMTP, SQL, and storage adapters
- **Core Libraries**: Starlette, HTMX, Jinja2, SQLModel, Pydantic, httpx

### Configuration Management
- Uses `acb.depends.depends` for dependency injection and configuration
- Application configuration loaded via `depends.get()` pattern
- Logging configured through ACB framework

### Optional Features
- **Analytics**: Google Analytics Admin and Data APIs (`analytics` extra)
- **Captcha**: Google reCAPTCHA Enterprise (`captcha` extra)
- **Auth**: Firebase Admin SDK (`auth` extra)

## Development Environment

### Package Management
- Uses `uv` for dependency management and virtual environment handling
- Lock file: `uv.lock`
- Development dependencies in `dependency-groups.dev`

### Quality Assurance
- **Type Checking**: Strict mode with pyright and mypy (zuban)
- **Code Quality**: Ruff for linting/formatting, refurb for refactoring suggestions
- **Security**: Bandit for security analysis, gitleaks for secrets detection
- **Complexity**: Maximum complexity of 15 (complexipy)
- **Coverage**: pytest with coverage reporting

### Project Structure Patterns
- Adapter pattern for external service integrations
- CLI extension pattern for operational commands
- Configuration-driven dependency injection
- Async-first architecture throughout

## Testing

- Test files follow pytest conventions: `test_*.py` or `*_test.py`
- Tests located in individual project directories under `projects/`
- Coverage configuration excludes test files and focuses on `splashstand/` source
- Async test support enabled with `asyncio_mode = "auto"`

## Deployment

SplashStand is designed for serverless deployment, particularly Google Cloud Run, with built-in commands for:
- Revision management and cleanup
- Custom domain configuration
- Build and deployment automation
- Application state management