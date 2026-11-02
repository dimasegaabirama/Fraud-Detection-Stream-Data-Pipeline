# Project Folders Structure Blueprint

Last updated: 2026-11-02

## Overview

This is a Python 3.10 streaming application using PyFlink, Kafka, Hadoop, Hive,
and PostgreSQL. The repository is organized primarily by technical layer:
configuration, models, rules, transformations, and infrastructure adapters.
It is one application with several Docker Compose service definitions, not a
monorepo or a set of independently deployed application microservices.

The Python package currently uses `src.*` imports from the repository root.
`main.py` is a placeholder, and the modules under `src/` are not yet assembled
into a complete executable streaming job. Keep that status clear until the job
orchestration is implemented and covered by an integration test.

## Directory Tree

Generated and local folders are listed separately below so source structure
remains easy to scan while still documenting the complete workspace.

```text
.
├── config/                         # Hadoop and Hive XML configuration
├── docker/
│   ├── flink/                      # Flink Compose, image, and entrypoint
│   ├── hadoop/                     # Hadoop Compose definition
│   ├── hive/                       # Hive Compose definition and image
│   ├── kafka/                      # Kafka Compose definition
│   └── postgres/
│       ├── init/                   # PostgreSQL schema and seed SQL
│       └── docker-compose.postgres.yaml
├── skills/                         # Repository-local workflow skills
│   ├── folder-structure/SKILL.md
│   └── refactor/SKILL.md
├── src/
│   ├── application/                # Application composition and startup
│   │   ├── bootstrap/              # Source/sink construction and registries
│   │   └── transform/              # Stream transformations and helpers
│   │       └── helpers/            # Timestamp, window, and normalization helpers
│   ├── config/                     # Settings models and application YAML
│   ├── integrations/               # External service adapters
│   │   └── exchange_rate/          # Exchange-rate API client (empty scaffold)
│   ├── models/
│   │   ├── normalized/             # Canonical transaction representation
│   │   ├── sink/                   # Output record models
│   │   └── source/                 # Input record models
│   ├── rules/                     # Fraud rule evaluation
│   ├── udf/                       # Flink user-defined functions
│   └── utils/                     # Flink, Kafka, Hive, and schema utilities
├── tests/                          # Pytest tests
│   └── integrations/
│       └── exchange_rate/           # Exchange-rate integration tests (empty scaffold)
├── main.py                         # Current placeholder entry point
├── Project_Folders_Structure_Blueprint.md
├── pyproject.toml                  # Dependencies and tool configuration
├── .python-version                 # Local Python version selector
├── README.md                       # Setup and project overview
├── start-all.sh                    # Start infrastructure in dependency order
├── stop-all.sh                     # Stop infrastructure without removing data
└── uv.lock                         # Resolved Python dependencies
```

### Generated and Empty Directories

The following paths are generated or local workspace artifacts. They are
ignored by Git and should not receive application source files:

| Path | Purpose / status |
| --- | --- |
| `.venv/` | Local Python virtual environment managed from `pyproject.toml` and `uv.lock` |
| `.pytest_cache/` | Pytest cache |
| `.ruff_cache/` | Ruff cache |
| `__pycache__/` | Python bytecode caches at the repository root, under `src/`, and under `tests/` |
| `src/integrations/exchange_rate/` | Empty scaffold; provider and API contract are not selected yet |
| `tests/integrations/exchange_rate/` | Empty scaffold for future integration tests |

Git does not preserve empty directories. These scaffolds exist in the local
workspace and will appear in version control after files are added; never move
source code into a cache directory.

## Directory Responsibilities

| Path | Responsibility | Place new files here |
| --- | --- | --- |
| `config/` | Hadoop/Hive client XML consumed by services | Service XML only |
| `docker/<service>/` | Compose and image assets owned by one service | Service-specific Docker files |
| `docker/postgres/init/` | First-run database schema and seed data | PostgreSQL initialization SQL |
| `src/application/bootstrap/` | Convert endpoint settings and registries into Flink connectors | Source/sink initialization and registrations |
| `src/config/` | Parse YAML/environment settings and validate their shape | Settings models and application configuration |
| `src/models/source/` | Validate input event records | Incoming record models |
| `src/models/normalized/` | Represent canonical records shared between stages | Normalized domain records |
| `src/models/sink/` | Define records emitted by pipeline sinks | Output record models |
| `src/models/` | Shared enums, endpoints, thresholds, and score policy | Cross-stage value models only |
| `src/rules/` | Apply fraud scoring logic | Rule implementations and common rule behavior |
| `src/application/transform/` | Convert or enrich records in the stream | Named pipeline transformations |
| `src/application/transform/helpers/` | Small transformation-only helpers | Timestamp, window, normalization helpers |
| `src/integrations/exchange_rate/` | Isolate exchange-rate provider HTTP/API details | Client, response parsing, provider-specific errors |
| `src/udf/` | Flink runtime function adapters | Reusable Flink UDFs |
| `src/utils/` | Integration and schema utilities | Cross-cutting infrastructure utilities |
| `tests/` | Automated behavior and contract checks | `test_*.py` files mirroring package areas |
| `tests/integrations/exchange_rate/` | Tests for the exchange-rate integration | Client response and error behavior tests |
| `skills/` | Local workflow instructions | Skill folders containing `SKILL.md` |

Avoid generic catch-all folders such as `src/functions/`. Add an orchestration
package only when a real job composition module exists; do not keep empty
folders as placeholders because Git does not preserve them.

## File Placement and Naming

- Python modules and folders use `snake_case`; classes use `PascalCase`.
- Keep Pydantic configuration models beside `settings.py` in `src/config/`.
- Keep checked-in, non-secret defaults in `src/config/config.yaml`; put local
  credentials and environment overrides in `.env`.
- Keep service-specific XML in root `config/`, separate from application YAML.
- Put external API clients under `src/integrations/<integration_name>/`; keep
  provider credentials in environment variables rather than source or YAML.
- Keep tests for an external client under the matching path in
  `tests/integrations/`.
- Keep source, normalized, and sink transaction types in their respective
  subpackages under `src/models/`.
- Put tests under `tests/` and name them `test_<behavior>.py`.
- Keep one Docker Compose file and its Docker assets inside the owning service
  directory under `docker/`.
- Use explicit imports rooted at `src.` consistently. Do not mix `models.*`
  imports with `src.models.*` imports.

## Dependency Flow

The intended direction is:

```text
config + models -> rules -> application/transform -> runtime
                                      ^
                                      |
                           application/bootstrap
```

Shared models should not import transforms, utilities, or bootstrap code.
Configuration should describe behavior and endpoints without constructing
runtime connectors. Bootstrap can depend on settings, endpoint/data models, and
infrastructure utilities. Keep infrastructure-specific calls out of rule
evaluation wherever possible.

The current code is only partially aligned with this direction. In particular,
`src/application/bootstrap/init_schema.py` currently builds connectors and Hive
tables, while `src/application/transform/` contains transformation entry
points. Treat this flow as the target boundary for future incremental
refactors, not a claim that the full pipeline is already wired.

## Navigation and Development

- Start with `README.md` for setup and infrastructure commands.
- Read `src/config/settings.py` and `src/config/config.yaml` to understand
  settings and defaults.
- Read `src/application/bootstrap/registry.py` for configured source/sink model mappings.
- Read `src/models/` for the event shapes and shared domain values.
- Read `src/rules/` for scoring and `src/application/transform/` for stream mappings.
- Use `start-all.sh` and `stop-all.sh` for the local service stack (Git Bash or
  WSL on Windows).
- Run `uv sync --group dev` to install dependencies, `uv run pytest` for tests,
  and `uv run ruff check .` for linting.

At the time of this update, the repository contains 39 Python files: 36 under
`src/`, one root entry point, and two tests. There are five service Compose
files. The test suite covers endpoint registration and transaction
normalization from both mappings and PyFlink rows; add focused unit tests before
changing scoring or transformation behavior.

## Extension Templates

### Add a Source or Sink

1. Define the record model under `src/models/source/` or `src/models/sink/`.
2. Register the model by endpoint name in `src/application/bootstrap/registry.py`.
3. Add or update the endpoint in `src/config/config.yaml` and its Pydantic
   validation in `src/config/` if the endpoint shape changes.
4. Add a test that verifies configured endpoint names resolve to model classes.

### Add a Transformation or Rule

1. Put stream mapping and Flink process adapters in
  `src/application/transform/`; put fraud scoring policy in `src/rules/`.
2. Reuse shared event types from `src/models/` rather than duplicating schemas.
3. Keep window, timestamp, and normalization helpers in
  `src/application/transform/helpers/` only when they are transformation concerns.
4. Add behavior tests before changing observable scores or output records.

### Add an Exchange-Rate Provider

The `src/integrations/exchange_rate/` and
`tests/integrations/exchange_rate/` directories are scaffolding only; no provider
or API contract has been selected yet. Once selected, put provider-specific
HTTP calls and response parsing in the integration package, expose a small
provider-neutral method to the application, and test success/error responses
under the matching test directory. Keep URL and credential configuration in
`src/config/` and environment variables, not in the client implementation.

## Structure Enforcement and Maintenance

- Pytest and Ruff are configured in `pyproject.toml`; keep new tests and modules
  within those conventions.
- `uv.lock` records the resolved dependency set. Review it when dependencies
  change; do not hand-edit it.
- Generated caches (`__pycache__/`, `.ruff_cache/`, `.pytest_cache/`) and local
  secrets (`.env`) are ignored and should not be committed.
- When adding or moving a module, update its imports, tests, and this blueprint
  in the same change. Prefer one small move at a time and run focused tests.
- Revisit this document whenever a package boundary, entry point, or test
  strategy changes.