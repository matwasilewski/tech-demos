# MongoDB Beanie Test Repository

A minimal guide for running the examples that accompany this repo.

## Quick Start

### 1. Start MongoDB (Docker)
```bash
docker-compose up -d
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Run the examples

Run a full cycle (create sample data, then search):
```bash
python hello.py
```

Create sample data only:
```bash
python hello.py --create-only
```

Search existing data only:
```bash
python hello.py --search-only --pmc-id PMC10300813
```

Custom connection parameters:
```bash
python hello.py --host localhost --port 27019 --database evidence-db-test
```

### Direct MongoDB connection test
```bash
python mongo_connection.py
```

