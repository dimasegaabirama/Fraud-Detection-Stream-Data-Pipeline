# Fraud Detection Streaming Pipeline

A real-time fraud detection pipeline built with Apache Kafka and Apache Flink. The system consumes transaction events, converts them into typed streaming records, aggregates behavioral signals over configurable time windows, and evaluates them against rule-based fraud thresholds.

The pipeline is designed to demonstrate the core challenges of streaming fraud detection: event-time processing, configurable rules, multi-dimensional transaction behavior, and reliable sinks for both analytical storage and fraud alerts. Hive is used for table-based transaction storage, while Kafka carries the streaming input and alert output.

## Project Summary

This project processes financial transactions in motion instead of waiting for batch jobs. Each transaction can be evaluated using signals such as transaction amount, device usage, IP activity, transaction velocity, and geographic movement. Rules can be adjusted by segment, direction, transaction type, and severity level without changing the streaming architecture.

## Features

- Stream processing of transaction events with 5-minute event-time windows
- Rule engine with three severity levels per rule: `low`, `medium`, `high`, each with its own threshold and score
- Rules split by **segment** (`BUSINESS`, `RETAIL`, `INDIVIDUAL`) and **direction** (`DEBIT`, `CREDIT`)
- Multiple rule types evaluated from the same window aggregation (amount, device, IP, velocity, receiver)
- PostgreSQL as storage, initialized automatically through Docker Compose
- Sample seed data (200 rows) including injected anomalies for testing

## Architecture

```
Transactions -> Kafka
        |
        v
Apache Flink
        - typed Kafka source and sink
        - event-time window processing
        - configurable aggregation and rule evaluation
        |
        v
Rule engine
        - segment and direction-aware thresholds
        - low, medium, and high severity levels
        - fraud score generation
        |
                                +--> Hive transaction tables
                                |
                                +--> Kafka fraud alerts
```

## Data Schema

| Column | Type (PostgreSQL) | Description |
|---|---|---|
| event_id | VARCHAR(50) | Unique event identifier |
| transaction_id | VARCHAR(50) | Transaction identifier |
| user_id | VARCHAR(50) | User identifier |
| timestamp | TIMESTAMPTZ | Event time |
| amount | NUMERIC(18,2) | Transaction amount |
| currency | CHAR(3) | ISO currency code (IDR, USD, SGD) |
| status | VARCHAR(20) | `SUCCESS`, `FAILED`, `PENDING`, `REVERSED` |
| transaction_type | VARCHAR(20) | `TRANSFER`, `PAYMENT`, `TOP_UP`, `WITHDRAWAL`, `REFUND` |
| direction | VARCHAR(10) | `DEBIT` (money out) or `CREDIT` (money in) |
| sender_account | VARCHAR(20) | Sender account, nullable |
| receiver_account | VARCHAR(20) | Receiver account, nullable |
| merchant_id | VARCHAR(20) | Merchant, nullable |
| ip_address | INET | Client IP |
| device_id | VARCHAR(50) | Device identifier |
| device_type | VARCHAR(20) | `ANDROID`, `IOS`, `WEB` |
| latitude | DOUBLE PRECISION | Location latitude |
| longitude | DOUBLE PRECISION | Location longitude |

## Fraud Rules

Every rule is defined per **segment x direction**, with three severity levels:

```python
self._rule(
    SegmentLevel.RETAIL,
    DirectionLevel.DEBIT,
    low=(4, 15.0),  # (threshold, score)
    medium=(5, 60.0),
    high=(8, 90.0),
)
```

The window (5 minutes) is defined once and shared by all rules. Each rule only differs in the metric it reads from the window:

| Rule | Metric per 5-minute window |
|---|---|
| Amount | `SUM(amount)` |
| Device | `COUNT(DISTINCT device_id)` |
| IP | `COUNT(DISTINCT ip_address)` |
| Velocity | `COUNT(*)` |
| Receiver | `COUNT(DISTINCT receiver_account)` |

Transaction type is intentionally **not** a rule dimension, to keep the number of rules at `rule types x 3 segments x 2 directions`. If needed later, it can be added as a threshold multiplier per type instead of separate rules.

## Project Structure

```
.
├── config/                # Hadoop/Hive XML configuration
├── docker/                # Service-specific Compose files, images, SQL init
├── skills/                # Repository-local workflow guidance
├── src/
│   ├── application/       # Application composition and startup
│   │   ├── bootstrap/     # Source/sink initialization and registries
│   │   └── transform/     # Stream transformations and helpers
│   ├── config/            # Pydantic settings and config.yaml
│   ├── integrations/      # External service clients
│   │   └── exchange_rate/ # Exchange-rate API integration (scaffold)
│   ├── models/            # Source, normalized, sink, and domain models
│   ├── rules/             # Fraud scoring rules
│   ├── udf/               # Flink user-defined functions
│   └── utils/             # Flink, Kafka, Hive, and schema utilities
├── tests/                 # Pytest tests
│   └── integrations/
│       └── exchange_rate/ # Exchange-rate client tests
├── main.py                # Current application entry point
├── Project_Folders_Structure_Blueprint.md
├── pyproject.toml         # Dependencies and tool configuration
├── start-all.sh           # Start services in dependency order
└── stop-all.sh            # Stop services without deleting volumes
```

See [Project_Folders_Structure_Blueprint.md](Project_Folders_Structure_Blueprint.md)
for the complete tree, file-placement rules, dependency flow, and extension guidance.

## Getting Started

### Prerequisites

- Python 3.10 (the supported range is declared in `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/)
- Docker and Docker Compose

### Setup

```bash
git clone https://github.com/dimasegaabirama/Fraud-Detection-Stream-Data-Pipeline.git
cd Fraud-Detection-Stream-Data-Pipeline
uv sync --group dev
```

### Start the services

```bash
bash start-all.sh
```

The service definitions are split under `docker/`; the startup script handles
their dependency order. Use Git Bash or WSL on Windows to run the `.sh` scripts.

### Entry point status

```bash
uv run python main.py
```

`main.py` is currently a placeholder; the bootstrap, source/sink, and
transformation modules are being assembled independently and are not yet wired
into a complete streaming job.

### Start all Docker services

From the repository root, run:

```bash
bash start-all.sh
```

The script starts Hadoop, Hive, Kafka, PostgreSQL, and Flink in dependency order.
Hive exposes its metastore database on host port `5432`; the application
PostgreSQL container exposes port `5433` to avoid a host-port collision.

To stop all services without deleting volumes or the shared Docker network, run:

```bash
bash stop-all.sh
```

## Configuration

Application configuration is loaded by `src/config/settings.py` from
`src/config/config.yaml`, with environment variables and `.env` values taking
precedence. Pydantic models for each section live beside it (`kafka.py`,
`hadoop.py`, `hive.py`, `pipeline.py`, and `rules.py`). Fraud thresholds and
score policy are configured in the YAML file; keep environment-specific
secrets in `.env`, not in the checked-in YAML.

### Aggregate score policy

Each enabled rule contributes a score of `0`, `10`, `50`, or `80`. The scores
are summed across the rules before determining the transaction status:

| Total score | Status |
|---:|---|
| `0-49` | `allow` |
| `50-99` | `otp` |
| `100-149` | `review` |
| `150+` | `block` |

These limits are configured in `src/config/config.yaml` under `score_policy`.
With the current five rules, the maximum possible aggregate score is `400`.

## Sample Data

`seed_transactions.sql` contains 200 sample transactions across 15 users. Rows `EVT00017`, `EVT00038`, `EVT00091`, `EVT00142`, and `EVT00173` are deliberate anomalies (large amount, new device, new IP, different location) to exercise the rules.

## Roadmap

- [ ] Normalize amounts to a single reference currency before comparing with thresholds
- [ ] Sliding window or OVER aggregation to remove window-boundary blind spots
- [ ] Per-transaction-type threshold multipliers
- [ ] Sequence rules (for example `TOP_UP` followed by a large `WITHDRAWAL`)
- [ ] Alert deduplication

## License

TODO
