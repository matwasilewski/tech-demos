# MongoDB Beanie Test Repository

This repository contains test code to showcase and demonstrate potential issues with **Beanie**, the MongoDB ODM (Object Document Mapper) library for Python.

## Overview

The project demonstrates:
- **Beanie document models** with parent-child relationships using `Link` fields
- **Async MongoDB operations** using Motor and Beanie
- **Document linking and fetching** which may exhibit specific behaviors or issues
- **CLI interface** for easy testing and exploration

## Structure

- **`document.py`** - Beanie document models (`Article`, `Author`, `Tag`)
- **`mongo_connection.py`** - MongoDB connection management and Beanie operations
- **`hello.py`** - CLI script for running tests from command line
- **`docker-compose.yml`** - MongoDB container setup

## Document Models

### Article (Parent Document)
- Contains title, content, PMC ID
- Links to multiple `Author` and `Tag` documents
- Includes metadata like publish date, view count

### Author & Tag (Child Documents)  
- Separate collections linked via Beanie `Link` fields
- Authors have name, email, affiliation
- Tags have name, color, description

## Usage

### Start MongoDB
```bash
docker-compose up -d
```

### Install Dependencies
```bash
uv sync
```

### Run Tests

**Full test (create data + search + demonstrate issues):**
```bash
python hello.py
```

**Create sample data only:**
```bash
python hello.py --create-only
```

**Search existing data only:**
```bash
python hello.py --search-only --pmc-id PMC10300813
```

**Custom connection settings:**
```bash
python hello.py --host localhost --port 27019 --database evidence-db-test
```

### Direct MongoDB Connection Testing
```bash
python mongo_connection.py
```

## Potential Issues Being Demonstrated

The code is structured to potentially showcase common Beanie issues:

1. **Link fetching behavior** - How `fetch_all_links()` works with nested documents
2. **Serialization issues** - JSON serialization of linked documents  
3. **Performance considerations** - Multiple link fetches and database queries
4. **Aggregation complexity** - Working with linked documents in queries

## MongoDB Connection

- **Host:** localhost
- **Port:** 27019 (matches docker-compose.yml)
- **Database:** evidence-db-test
- **Credentials:** root/root

The connection settings have been corrected from the original script which used port 27018.