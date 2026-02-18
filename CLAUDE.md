# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**odata-query** is a Python library that parses OData v4 query strings and transpiles them to Django ORM queries, SQLAlchemy queries, or raw SQL. It uses SLY (Sly Lex-Yacc) for grammar-based parsing, builds an immutable AST from frozen dataclasses, and applies the Visitor pattern to transform the AST into various backend formats.

## Common Commands

```bash
# Install with all dev extras
poetry install -E testing -E linting -E docs

# Run all tests
pytest

# Run a single test
pytest tests/unit/test_odata_parser.py::test_name

# Run tests excluding slow ones
pytest -m "not slow"

# Run full matrix (multiple Python + Django versions)
tox

# Linting (all at once via tox)
tox -e linting

# Individual lint commands
black --check --diff odata_query tests
isort --check-only odata_query tests
flake8 --show-source odata_query tests
mypy --ignore-missing-imports -p odata_query
vulture odata_query/ --min-confidence 80

# Format code
black odata_query tests
isort odata_query tests
```

## Architecture

### Parsing Pipeline

OData string → `ODataLexer` → tokens → `ODataParser` → AST → Backend Visitor → output

1. **Grammar** (`grammar.py`): SLY-based lexer and parser that tokenize and parse OData filter strings into AST nodes.
2. **AST** (`ast.py`): Frozen dataclasses representing all node types — literals, operators (binary/unary/comparison/boolean), function calls, collections, and lambda expressions. All inherit from `_Node`.
3. **Visitors** (`visitor.py`): `NodeVisitor` (read-only traversal) and `NodeTransformer` (tree rewriting) base classes. Each backend subclasses these.

### Backend Visitors

Each backend lives in its own subpackage with a visitor and a shorthand `apply_odata_query()` entry point:

- **`django/`**: `AstToDjangoQVisitor` → Django Q objects. Entry: `apply_odata_query(queryset, odata_str)`
- **`sqlalchemy/`**: ORM (`AstToSqlAlchemyOrmVisitor`) and Core (`AstToSqlAlchemyCoreVisitor`) visitors. Entry: `apply_odata_query()` / `apply_odata_core()`
- **`sql/`**: `AstToSqlVisitor` base with dialect-specific subclasses (`sqlite.py`, `athena.py`)

### Supporting Modules

- **`typing.py`**: Type inference engine for AST nodes (used for validation)
- **`rewrite.py`**: AST transformations — `AliasRewriter` (field aliasing), `IdentifierStripper` (root identifier removal)
- **`roundtrip.py`**: `AstToODataVisitor` converts AST back to OData string
- **`exceptions.py`**: `ODataException` → `ODataSyntaxError`, `FunctionCallException`, etc.

## Code Style

- **black** formatting, **isort** imports, **flake8** linting
- Max line length: 80 (flake8), 88 (isort/black)
- `grammar.py` has special flake8 ignores (F821, F811) due to SLY's declarative grammar style
- Django test settings: `DJANGO_SETTINGS_MODULE=tests.integration.django.settings`

## Test Structure

- `tests/unit/` — Core parsing, AST, type inference, transformations
- `tests/integration/` — Full pipeline with Django, SQLAlchemy, SQL backends
- `tests/data/` — Test fixtures
- Coverage reporting is enabled by default via `setup.cfg`
