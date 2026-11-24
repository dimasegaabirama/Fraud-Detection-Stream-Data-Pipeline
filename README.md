# Fraud Detection Streaming Pipeline

A real-time fraud detection streaming pipeline built with **Apache Kafka and PyFlink** to evaluate financial transactions through parallel fraud detection rules, stateful stream processing, and risk-based decision making.

The pipeline processes incoming transaction events, performs cleaning and deduplication, validates records against predefined conditions, and evaluates valid transactions using multiple fraud detection rules. Individual rule scores are aggregated to determine the appropriate action: **BLOCK, OTP, or ALLOW**.

The architecture uses Redis for blacklist and reference data, Hive with Apache Iceberg for analytical storage, and Kafka for transaction ingestion and fraud alert messaging.

> **Development Status:** The project is under active development. Individual components, contracts, configurations, and integrations are being assembled, but the complete streaming orchestration is not yet wired into `main.py`. The architecture below represents the intended pipeline design, not a fully operational end-to-end implementation.

## Architecture Overview


## Pipeline Workflow

### 1. Transaction Ingestion

Transaction events are produced by upstream applications and published to the Kafka `transactions` topic.

Kafka acts as the entry point for incoming financial transaction events, allowing the streaming application to consume transactions continuously.

### 2. Cleaning & Deduplication

Incoming records are consumed from Kafka and processed before fraud evaluation.

This stage is responsible for:

- Cleaning transaction fields.
- Normalizing transaction attributes.
- Removing duplicate transaction records.
- Preparing consistent transaction data for validation.

Duplicate records are separated from valid records and routed to the appropriate side output.

### 3. Record Validation

Every transaction passes through an initial validation stage before entering the fraud detection engine.

The validation process checks:

- **Duplicate Check:** Identifies previously processed transactions.
- **Schema Validation:** Ensures incoming records follow the expected transaction contract.
- **Blacklist Lookup:** Checks transaction attributes against Redis blacklist data, such as `user_id` and `ip_address`.

Invalid, duplicate, and blacklisted records are routed to side outputs instead of continuing through the normal scoring flow.

### 4. Stateful Processing

Valid transactions are partitioned using `user_id` as the key.

This ensures that transactions belonging to the same user are consistently processed by the same keyed operator.

A shared window state maintains transaction information for each user, allowing multiple fraud detection rules to access relevant transaction history.

The intended design uses shared user-level state to support parallel rule evaluation.

### 5. Parallel Fraud Rules

The fraud detection engine evaluates transactions using multiple independent rules.

Each rule calculates its own risk score based on transaction behavior and historical information.

| Rule       | Description                                                                 |
| ---------- | --------------------------------------------------------------------------- |
| Velocity   | Detects unusually frequent transactions within a defined time window.       |
| Device     | Identifies suspicious device usage and device-related transaction patterns. |
| IP Address | Detects suspicious IP addresses and unusual IP-related activity.            |
| Speed      | Identifies unusual transaction speed or frequency patterns.                 |
| Amount     | Detects unusual transaction amounts based on configured thresholds.         |

Each rule returns an individual risk score. These scores are then passed to the scoring aggregation stage.

### 6. Score Aggregation

Individual fraud rule scores are combined into a single risk score for each transaction.

The aggregated score represents the overall risk associated with the transaction and becomes the input for the decision-making process.

### 7. Decision & Action

The decision engine compares the aggregated risk score against configured thresholds to determine the appropriate transaction action.

| Action | Description                                                              |
| ------ | ------------------------------------------------------------------------ |
| BLOCK  | Declines the transaction and adds relevant information to the blacklist. |
| OTP    | Requires additional verification through a one-time password.            |
| ALLOW  | Approves the transaction.                                                |

The resulting fraud evaluation is published to the Kafka `fraud_alerts` topic.

### 8. Storage & Messaging

The pipeline integrates three primary infrastructure components.

**Redis**

- Stores blacklist information, including `user_id` and `ip_address`.
- Caches exchange-rate reference data.
- Supports transaction sliding-window and state-related operations.

**Hive + Apache Iceberg**

- Stores fraud evaluation records in the `fact_fraud_evaluation` table.
- Uses the Iceberg table format for analytical storage.
- Loads evaluation data from the Kafka `fraud_alerts` topic.

**Kafka Broker**

- `transactions`: Incoming transaction events.
- `fraud_alerts`: Fraud evaluation results, including BLOCK, OTP, and ALLOW decisions.

## Current Capabilities

The repository currently contains the following components:

- PyFlink-oriented transaction processing components and Kafka endpoint configuration.
- Pydantic contracts for raw transactions, normalized transactions, fraud evaluation records, fraud alerts, duplicate events, and invalid events.
- Transaction normalization for decimal amounts, coordinates, timestamps, and categorical values.
- A keyed deduplication component with a five-minute event-time TTL.
- Configurable fraud detection rules for amount, device, IP address, speed, and velocity.
- Configurable thresholds, risk levels, and score factors.
- Score aggregation and action threshold configurations.
- Redis integrations for exchange-rate caching and transaction sliding-window data.
- Hive and Kafka sink definitions.
- Docker Compose infrastructure for Hadoop, Hive, Kafka, PostgreSQL, and Flink.

**Implementation Note:** The intended architecture uses user-keyed shared state for fraud rule evaluation. However, individual rule window configurations currently exist independently. Their integration into the shared state and complete streaming execution still require implementation and testing.

## Transaction Contract

The raw Kafka transaction is validated against `src/contracts/raw_events.py`.

Optional account and merchant fields may be null.

| Field                   | Expected Value   | Description                                    |
| ----------------------- | ---------------- | ---------------------------------------------- |
| `event_id`              | string           | Event identifier                               |
| `transaction_id`        | string           | Transaction identifier used for deduplication  |
| `user_id`               | string           | User identifier                                |
| `amount`                | positive decimal | Transaction amount                             |
| `currency`              | string           | Currency code; normalized to uppercase         |
| `segment`               | string           | User segment; normalized to lowercase          |
| `transaction_type`      | string           | Transaction type; normalized to lowercase      |
| `direction`             | string           | Transaction direction; normalized to lowercase |
| `sender_account`        | string or null   | Sender account                                 |
| `receiver_account`      | string or null   | Receiver account                               |
| `merchant_id`           | string or null   | Merchant identifier                            |
| `ip_address`            | string           | Client IP address                              |
| `device_id`             | string           | Device identifier                              |
| `device_type`           | string           | Device type; normalized to lowercase           |
| `latitude`, `longitude` | numeric          | Transaction coordinates                        |
| `status`                | string           | Transaction status; normalized to lowercase    |
| `event_timestamp`       | string           | Event-time timestamp                           |

The cleaned transaction contract and fraud output contracts are defined in:

- `src/contracts/cleaned_events.py`
- `src/contracts/score_events.py`

## Fraud Scoring & Configuration

Application defaults and fraud rule thresholds are maintained in `src/config/config.yaml`.

Pydantic settings models are defined in `src/models/settings/`.

The configuration supports:

- Fraud rules based on transaction behavior.
- Thresholds and optional score factors.
- User segments.
- Transaction directions.
- Transaction types.
- Rule-specific aggregation and time windows.

Current rule windows are configured individually. For example:

- Amount: 24-hour window.
- Device: 1-hour window.
- Velocity: 1-minute window.

The aggregate score policy currently defines the following action thresholds:

| Action | Score Threshold |
| ------ | --------------: |
| OTP    |              50 |
| Review |             100 |
| Block  |             150 |

Keep environment-specific credentials and overrides in `.env`, which is ignored by Git. Never commit secrets to the repository.

The exchange-rate client is implemented in `src/integrations/api/exchange_rate.py` and uses Redis as a cache.

Redis sliding-window helpers are located in `src/integrations/redis/`.

## Project Structure

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
├── src/
│   ├── application/
│   │   ├── bootstrap/              # Schema/bootstrap setup
│   │   └── transform/              # Transaction transformations and helpers
│   ├── common/                     # Shared names, keys, tags, and formats
│   ├── config/                     # Settings loader and application YAML
│   ├── contracts/                  # Raw, cleaned, scored, and side-event models
│   ├── integrations/
│   │   ├── api/                    # Exchange-rate API client
│   │   └── redis/                  # Redis client and sliding-window helpers
│   ├── models/                     # Domain, endpoint, score, and settings models
│   ├── rules/                      # Fraud rule evaluation components
│   ├── udf/                        # Flink user-defined functions
│   └── utils/                      # Flink and Hive helpers
├── tests/                          # Unit and integration tests
├── main.py                         # Placeholder entry point
├── Project_Folders_Structure_Blueprint.md
├── pyproject.toml                  # Dependencies and tool configuration
├── start-all.sh                    # Start Docker Compose stacks
├── stop-all.sh                     # Stop stacks and remove Compose volumes
└── uv.lock                         # Resolved Python dependencies
```

See [Project_Folders_Structure_Blueprint.md](Project_Folders_Structure_Blueprint.md) for directory responsibilities and extension guidance.

## Getting Started

### Prerequisites

- Python 3.10 (required by `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/)
- Docker with Docker Compose v2
- Bash-compatible shell (Git Bash or WSL on Windows)

### Install Python Dependencies

```bash
uv sync --group dev
```

### Configure & Start Infrastructure

Create a local `.env` containing the environment variables required by the Docker Compose files. Do not commit this file.

```bash
bash start-all.sh
```

The script starts Hadoop, Hive, Kafka, PostgreSQL, and Flink, and creates the external `hadoop_net` Docker network if it does not exist.

Hive's metastore PostgreSQL uses host port `5432`, while the separate application PostgreSQL container uses host port `5433`.

> **Data Warning:** `stop-all.sh` runs Compose with `down -v`. This removes Compose-managed volumes, including persisted service data.

### Application Entry Point

```bash
uv run python main.py
```

`main.py` is currently a placeholder and does not start the complete streaming pipeline.

### Run Tests & Lint

```bash
uv run pytest
uv run ruff check .
```

## Roadmap

- [x] Integrate Kafka source with the PyFlink streaming application.
- [x] Complete transaction cleaning, normalization, and deduplication.
- [x] Implement schema, duplicate, and Redis blacklist validation.
- [x] Configure side outputs for duplicate, dead-letter, and blacklisted records.
- [ ] Implement keyed state partitioning using `user_id`.
- [ ] Integrate shared user-level window state for parallel fraud rules.
- [ ] Complete velocity, device, IP address, speed, and amount rule evaluation.
- [ ] Integrate individual rule scores into the aggregation engine.
- [ ] Implement risk-based decision making for BLOCK, OTP, and ALLOW.
- [ ] Connect Kafka fraud alert output to the Hive Iceberg sink.
- [ ] Add end-to-end tests for the complete streaming pipeline.
- [ ] Finalize and validate state and window behavior for each fraud rule.
- [ ] Integrate base currency normalization into the transaction processing flow.

## License

TODO
