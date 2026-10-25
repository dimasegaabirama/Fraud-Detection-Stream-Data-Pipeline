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
TODO: replace with the real structure, for example:
.
├── docker-compose.yml
├── init/                  # SQL scripts for PostgreSQL (docker-entrypoint-initdb.d)
├── src/
│   ├── config/            # fraud_rules.py (window size, minimum counts, ...)
│   ├── domain/            # enums: SegmentLevel, DirectionLevel
│   ├── models/            # rule and threshold models
│   └── rules/             # amount_rules.py, device_rules.py, base_rules.py, ...
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.x (TODO: exact version)
- Docker and Docker Compose
- TODO: Flink / Spark / Kafka requirements

### Setup

```bash
git clone https://github.com/dimasegaabirama/Fraud-Detection-Stream-Data-Pipeline.git
cd Fraud-Detection-Stream-Data-Pipeline

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt     # TODO: confirm file exists
```

### Start the database

```bash
docker compose up -d
```

SQL files in `init/` are executed automatically on first start (when the volume is empty). To re-run them:

```bash
docker compose down -v
docker compose up -d
```

### Run the pipeline

```bash
python main.py        # TODO: replace with the real entry point
```

> Run the entry point as a script rather than `python -m src.rules.amount_rules`. Running a module that is also imported by its package `__init__.py` triggers a `RuntimeWarning` because the module is loaded twice.

## Configuration

| Setting | Location | Default |
|---|---|---|
| Window size | `src/config/fraud_rules.py` (`WINDOW_MINUTES`) | 5 |
| Minimum active days | `src/config/fraud_rules.py` (`MIN_ACTIVE_DAYS`) | TODO |
| Minimum transaction count | `src/config/fraud_rules.py` (`MIN_TXN_COUNT`) | TODO |
| Segment thresholds | `src/rules/*_rules.py` | see rule classes |

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
