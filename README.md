# KIWI interview task

# Requirements:

# Frontend:

As the application is built as a RestAPI, FE interface was omitted. For manual testing purposes,
OpenAPI docs can be used under: `localhost:8000/docs` route.

# API

Application uses fully async FastAPI - as a bonus, it provides automatic API documentation. Provides
a full input/output validation using Pydantic. API
exposes 2 endpoints:

- `/countries` - allows for bulk importing of `Country name` to `ISO code` mapping, which will be
  fed into the database and used as a source of truth when filtering output in second endpoint
- `/match_country` - endpoint conforming to requirements - allowing to filter country names based on
  attached country code

# Persistance:

Application uses SQLite3, but is mostly DB-agnostic. ISO codes and country names are stored in 2 tables, connected with a
many-to-one relationship, where each country name references a proper ISO code. This is our source
of truth.

# Logging:

Application logs requests/errors to stdout and files using a rotating file strategy.

# Tests:

# Caching

# Docker

# CI/CD
