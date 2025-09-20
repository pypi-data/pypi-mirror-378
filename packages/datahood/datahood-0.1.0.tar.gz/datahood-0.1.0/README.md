# Datahood

A friendly toolkit and CLI to transfer and stream data between databases using async pipelines, plus automatic schema inference that generates **TypedDict** and **Pydantic** models from your existing documents.

This tool was born from repeatedly writing throwaway scripts to move data from point A to point B across various client projects. Instead of reinventing the wheel every time, I extracted this into a reusable solution. If it saves you from writing ad-hoc data transfer scripts, it has fulfilled its purpose!

---

## 🎯 What It Does

**Datahood** solves two common data engineering problems:

1. **Data Transfer** - Move data between MongoDB collections and BSON files with streaming performance
2. **Schema Discovery** - Automatically generate Python type definitions from your existing documents

Perfect for:

-   Moving production data slices to staging/development environments
-   Creating typed models from legacy collections for safer refactoring
-   Auditing document structure before migrations
-   Quick data exports and imports with compression support

---

## 🚀 Quick Start

```bash
# Get help
dh --help
dh transfer --help
dh schema --help

# Transfer data
dh transfer mongo-to-bson output.bson --source-uri mongodb://localhost --source-collection users
dh transfer bson-to-mongo data.bson --dest-uri mongodb://localhost --dest-collection users

# Generate Python types
dh schema from-mongo --uri mongodb://localhost --collection users --to-pydantic -o models.py
dh schema from-bson data.bson --to-typeddict -o models.py
```

## 📦 Installation

```bash
uv add datahood  # or pip install datahood
```

## 👷 Data Transfer

> TIP: Add `--dry-run` to any command to preview without moving data

### MongoDB → BSON

```bash
dh transfer mongo-to-bson output.bson \
  --source-uri "mongodb://user:pass@localhost:27017/?authSource=admin" \
  --source-database mydb \
  --source-collection users
```

### BSON → MongoDB

```bash
dh transfer bson-to-mongo data.bson \
  --dest-uri "mongodb://user:pass@localhost:27017/?authSource=admin" \
  --dest-database mydb \
  --dest-collection users
```

### MongoDB → MongoDB

```bash
dh transfer mongo-to-mongo \
  --source-uri "mongodb://source:27017" \
  --source-database src_db --source-collection users \
  --dest-uri "mongodb://dest:27017" \
  --dest-database dest_db --dest-collection users_copy
```

## 🧬 Schema Generation

### From MongoDB

```bash
# Generate Pydantic models
dh schema from-mongo --uri mongodb://localhost --collection users --to-pydantic -o models.py

# Generate TypedDict (default)
dh schema from-mongo --uri mongodb://localhost --collection users -o models.py
```

### From BSON Files

```bash
# Generate Pydantic models
dh schema from-bson data.bson --to-pydantic -o models.py

# Generate TypedDict
dh schema from-bson data.bson --to-typeddict -o models.py
```

**Smart Features:**

-   Automatically handles nested objects and creates separate types
-   Detects optional fields and union types
-   Generates clean, production-ready code

## 🧪 Development

```bash
make format lint type-check test    # Quality checks
make test-mongo-up                  # Start test MongoDB
RUN_INTEGRATION=1 pytest tests/integration
make test-mongo-down               # Clean up
```

## 🤝 Contributing

1. Fork & create feature branch
2. Add changes with tests
3. Run: `make format lint type-check test`
4. Submit PR

Version bumps: `make bump-version PART=patch|minor|major`

## 📬 Support

**Issues**: https://github.com/ericmiguel/datahood/issues

Happy data moving! ✨
