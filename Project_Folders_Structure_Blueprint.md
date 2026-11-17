# Project Folders Structure Blueprint

Last updated: 2026-11-17

## Overview

This repository contains one Python 3.10 streaming application, built around
Kafka and PyFlink, plus Docker Compose definitions for Hadoop, Hive, Kafka,
PostgreSQL, and Flink. Redis and an exchange-rate API client are also present
as integrations.

The source components are not yet assembled into a complete executable stream
job: `main.py` is a placeholder. The Mermaid flow in `README.md` documents the
intended flow across the existing components, not a fully running deployment.
There is no Spark, Bronze/Silver/Gold, PyDeequ, or branch-and-merge workflow in
the current repository.

Python imports are rooted at `src.` from the repository root. The supported
Python range is declared in `pyproject.toml`.

## Directory Tree

```text
.
├── config/                           # Hadoop and Hive XML configuration
├── docker/
│   ├── flink/                        # Flink Compose, base image, entrypoint
│   ├── hadoop/                       # Hadoop Compose definition
│   ├── hive/                         # Hive Compose definition and base image
│   ├── kafka/                        # Kafka Compose definition
│   └── postgres/
│       ├── init/                     # PostgreSQL initialization SQL
│       └── docker-compose.postgres.yaml
├── src/
│   ├── application/
│   │   ├── bootstrap/
│   │   │   └── init_schema.py        # Schema setup
│   │   └── transform/
│   │       ├── cleaned_transaction.py
│   │       └── helpers/
│   │           └── normalization.py
│   ├── common/                       # Shared keys, names, tags, and formats
│   ├── config/
│   │   ├── config.yaml
│   │   └── settings.py
│   ├── contracts/                    # Raw, cleaned, score, and side-event models
│   │   ├── cleaned_events.py
│   │   ├── raw_events.py
│   │   ├── score_events.py
│   │   └── side_events.py
│   ├── integrations/
│   │   ├── api/
│   │   │   └── exchange_rate.py
│   │   └── redis/                    # Redis client and sliding-window access
│   ├── models/
│   │   ├── settings/                 # Pydantic application settings models
│   │   ├── endpoint.py
│   │   ├── enums.py
│   │   ├── score.py
│   │   └── threshold.py
│   ├── rules/                        # Fraud rule components and output tags
│   ├── udf/                          # Flink user-defined functions
│   └── utils/                        # Flink and Hive utilities
├── tests/
│   ├── integrations/
│   │   └── exchange_rate/
│   │       └── test_exchange_rate.py
│   ├── test_normalization.py
│   └── test_registry.py
├── main.py                           # Placeholder entry point
├── Project_Folders_Structure_Blueprint.md
├── README.md
├── pyproject.toml                    # Dependencies and tool configuration
├── .python-version                   # Local Python version selector
├── start-all.sh                      # Start infrastructure in dependency order
├── stop-all.sh                       # Stop stacks and remove Compose volumes
└── uv.lock                           # Resolved Python dependencies
```

Local-only or generated files such as `.venv/`, `.pytest_cache/`, `.ruff_cache/`,
`__pycache__/`, and `.env` are not application source. Git does not preserve
empty directories; describe a package here only when it exists in the project
or has a clear place in the active design.

## Directory Responsibilities

| Path | Responsibility | Place new files here |
|---|---|---|
| `config/` | Hadoop and Hive XML settings mounted into service containers | Service XML |
| `docker/<service>/` | Compose and image assets owned by a service | Service-specific Docker files |
| `docker/postgres/init/` | App PostgreSQL schema and initial data | PostgreSQL initialization SQL |
| `src/application/bootstrap/` | Set up application schema resources | Bootstrap and schema setup |
| `src/application/transform/` | Convert and enrich transaction records | Named stream transformations |
| `src/application/transform/helpers/` | Small transformation-specific helpers | Normalization and similar helpers |
| `src/common/` | Constants and shared formatting/key conventions | Cross-package constants |
| `src/config/` | Load YAML/environment settings | Settings loader and application YAML |
| `src/contracts/` | Validate input, cleaned, output, and side-event shapes | Pydantic event contracts |
| `src/integrations/api/` | Encapsulate external API access | API clients and response handling |
| `src/integrations/redis/` | Encapsulate Redis access and window helpers | Redis client and integration behavior |
| `src/models/` | Shared domain, endpoint, threshold, and score values | Cross-stage domain models |
| `src/models/settings/` | Validate configuration sections | Pydantic settings models |
| `src/rules/` | Configure and evaluate fraud rules; define fraud output tags | Rule implementations and shared rule behavior |
| `src/udf/` | Adapt reusable logic to Flink UDF interfaces | Flink UDFs |
| `src/utils/` | Flink/Hive support utilities | Cross-cutting runtime helpers |
| `tests/` | Automated behavior and contract checks | `test_*.py` files |
| `tests/integrations/exchange_rate/` | Exchange-rate client behavior | API success/error tests |

Do not add model subpackages such as `source/`, `normalized/`, or `sink/` until
the code needs and contains those boundaries. Likewise, add orchestration
packages only alongside real job composition modules.

## File Placement and Naming

- Use `snake_case` for Python modules and folders, and `PascalCase` for classes.
- Keep Pydantic settings models under `src/models/settings/` and their loader in
  `src/config/settings.py`.
- Keep non-secret defaults in `src/config/config.yaml`; store local credentials
  and overrides in `.env`.
- Keep Hadoop/Hive service XML in the repository-level `config/` directory.
- Keep external service access behind `src/integrations/` adapters.
- Keep raw/cleaned/output event schemas under `src/contracts/`.
- Place tests under `tests/` and name them `test_<behavior>.py`.
- Keep each Docker Compose file and its service-owned assets under
  `docker/<service>/`.
- Use `src.`-rooted imports consistently; do not mix `src.models.*` with
  `models.*`.

## Dependency Flow

The intended dependency direction is:

```text
config + contracts + models
             |
             v
 integrations + rules
             |
             v
 application/transform + application/bootstrap
             |
             v
       Flink runtime
             |
             v
       Kafka / Hive
```

Contracts and domain models should not depend on runtime adapters. Configuration
should describe settings and endpoints rather than constructing live
connectors. Keep infrastructure-specific calls in integrations, utilities, or
bootstrap code rather than in rule logic.

The current implementation is partial: transaction normalization and
deduplication components, settings, contracts, rules, and infrastructure
helpers exist, but `main.py` does not assemble them into the full runtime job.
Keep documentation explicit about this status until end-to-end wiring and tests
are in place.

## Navigation and Development

- Start with `README.md` for the project summary, intended pipeline flow, and
  infrastructure commands.
- Read `src/config/settings.py`, `src/config/config.yaml`, and
  `src/models/settings/` for configuration behavior.
- Read `src/contracts/` for the raw and output event shapes.
- Read `src/application/transform/` for normalization and deduplication.
- Read `src/rules/` and `src/models/score.py` for rule and scoring components.
- Read `src/integrations/` for Redis and external API access.
- Use `start-all.sh` and `stop-all.sh` to manage the local Docker stack (Git
  Bash or WSL on Windows). Note that `stop-all.sh` removes Compose volumes.
- Run `uv sync --group dev` to install dependencies, `uv run pytest` for tests,
  and `uv run ruff check .` for linting.

## Extension Guidance

### Add or change a transaction contract

1. Update the relevant model in `src/contracts/`.
2. Update normalization or transformations under `src/application/transform/`
   if the field needs conversion.
3. Add focused tests under `tests/` for valid and invalid inputs.

### Add or change a fraud rule

1. Define or update its configuration model in `src/models/settings/` and
   defaults in `src/config/config.yaml`.
2. Implement the scoring behavior under `src/rules/`.
3. Update aggregation/output contracts if the emitted result changes.
4. Add tests for threshold boundaries, factors, and score aggregation.

### Add an integration

1. Encapsulate API or service-specific behavior under
   `src/integrations/<integration>/`.
2. Keep credentials in environment variables rather than source or checked-in
   YAML.
3. Add integration tests under the corresponding `tests/integrations/` path.

## Structure Maintenance

- Pytest and Ruff are configured in `pyproject.toml`; follow those conventions.
- Update this blueprint when package boundaries or the application entry point
  change.
- Keep generated caches and local secrets out of source control.
- `stop-all.sh` currently invokes Docker Compose with `down -v`; assume service
  volumes and their data will be removed when using it.
