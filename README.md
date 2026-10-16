# Fraud Detection Stream Data Pipeline

A rule-based fraud detection pipeline for streaming transaction data. Transactions are aggregated in **5-minute windows** per user, evaluated against configurable rules by **segment** and **direction**, and turned into a fraud score.

> **Note:** parts marked `TODO` are placeholders. Adjust them to match the actual implementation.

## Features

- Stream processing of transaction events with 5-minute event-time windows
- Rule engine with three severity levels per rule: `low`, `medium`, `high`, each with its own threshold and score
- Rules split by **segment** (`BUSINESS`, `RETAIL`, `INDIVIDUAL`) and **direction** (`DEBIT`, `CREDIT`)
- Multiple rule types evaluated from the same window aggregation (amount, device, IP, velocity, receiver)
- PostgreSQL as storage, initialized automatically through Docker Compose
- Sample seed data (200 rows) including injected anomalies for testing

## Architecture

```
Transactions (TODO: Kafka / files)
        |
        v
Stream processing  (TODO: Flink / Spark)
  - event-time + watermark
  - 5-minute window per user_id + direction
  - metrics: SUM(amount), COUNT(DISTINCT device_id),
             COUNT(DISTINCT ip_address), COUNT(*), ...
        |
        v
Rule engine (segment x direction)
  - compare each metric with low / medium / high threshold
  - produce score per rule
        |
        v
Fraud score / alerts  ->  PostgreSQL  (TODO: alert sink)
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
