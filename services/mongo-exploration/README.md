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

---

Default MongoDB settings (see `docker-compose.yml`):
- **Host:** localhost
- **Port:** 27019
- **Database:** evidence-db-test
- **Credentials:** root/root

---

## Tutorial – Beanie Inheritance Deep-Dive

### 1. Front-matter (YAML example)
```yaml
title: "When Document Inheritance Meets MongoDB: Debugging Beanie’s Polymorphic Fetches"
date: 2024-07-31
tags: ["MongoDB", "Beanie", "Python", "ODM", "Polymorphism"]
description: "Lessons learned when a single base document spawns subclasses and your find() starts returning surprises."
readingTime: 8  # minutes
```

### 2. Executive TL;DR
- Beanie stores each subclass in its own collection by default → polymorphic queries need extra care.
- The base-class `.find_all()` returns only documents from the *base* collection unless you opt into single-collection inheritance.
- Two escape hatches: a) `inheritance="single"` in the Settings class, b) manual union queries across collections.
- Fully-working demo lives in `/services/mongo-exploration`.

### 3. Problem Statement
> “Why does my generic `Document.find_all()` return **1** record when I clearly inserted **5** (including 2 `SystematicReview`s & 2 `ClinicalTrial`s)?”

### 4. Minimal Repro Setup
1. Docker Compose snippet spinning up Mongo 6.x on port 27019.
2. `pyproject.toml` listing Beanie, Motor & Pydantic.
3. Sample code from this repo.

### 5. Modelling the Hierarchy in Beanie
```python
# document.py
class Document(BeanieDocument):
    ...

class SystematicReview(Document):
    ...

class ClinicalTrial(Document):
    ...
```
Default collection names become `document`, `systematicreview`, `clinicaltrial`.

### 6. Seeding the Database
Excerpt from `MongoDBManager.create_sample_data()`:
```python
for doc in [generic_doc, sr_vaccines, sr_supplements, ct_drug_a, ct_surgery_b]:
    await doc.insert()
```
Five inserts confirmed in the terminal.

### 7. The Retrieval Puzzle
1. Subclass works:
```python
trials = await ClinicalTrial.find_all().to_list()
print(len(trials))  # 2
```
2. Base class disappoints:
```python
docs = await Document.find_all().to_list()
print(len(docs))  # 1
```

### 8. Under the Hood – What Beanie Does with Inheritance
- Each concrete subclass → its own Mongo collection.
- The base class is unaware of sibling collections.
- No built-in “union all collections” unless you enable single-collection inheritance.
- Single-collection mode adds a discriminator field `_cls` automatically.

### 9. Fix #1 – Single Collection with Discriminator
```python
class Root(Document):
    class Settings:
        name = "documents"      # single collection name
        inheritance = "single"  # enable discriminator
```
`Root.find_all()` now returns **5** documents. Caveat: a mixed collection may need compound indexes for performance.

### 10. Fix #2 – Manual “Union” Query
```python
docs = (
    await Document.find_all().to_list() +
    await SystematicReview.find_all().to_list() +
    await ClinicalTrial.find_all().to_list()
)
```
Useful when you want separate collections for TTL or sharding.

### 11. Fix #3 – Aggregation Pipeline (Advanced)
Use Mongo’s `$unionWith` in a raw Motor aggregation when you need server-side filtering/sorting across collections.

### 12. Trade-offs & Recommendations
| Strategy                    | Pros                                 | Cons                                                  | Best When                              |
|-----------------------------|--------------------------------------|-------------------------------------------------------|----------------------------------------|
| Single collection           | Polymorphic query is trivial         | Larger documents, discriminator column               | 90 % of CRUD apps                      |
| Multi-collection + union    | Separate indexes & TTL per type      | Client merges, extra round-trips                      | Large/heterogeneous subclasses         |
| Aggregation `$unionWith`    | Server-side filter/sort/aggregate    | Requires raw pipeline, loses Beanie syntactic sugar   | Complex analytics queries              |

### 13. Closing Thoughts
“Inheritance” in document databases is a design choice, not a free bonus. Beanie makes either path explicit—choose early to avoid painful migrations later.

### 14. Further Reading
- Official Beanie guide on inheritance.
- Mongo `$unionWith` documentation.
- Pydantic v2 roadmap.

### 15. Comments / Call to Action
Found an error or have an idea? **PRs welcome!**
