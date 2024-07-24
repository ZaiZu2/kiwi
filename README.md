# KIWI interview task

# Requirements:

# Frontend
Interface for querying the endpoint is implemented using a Jinja2 template

# API
Application uses fully async FastAPI - as a bonus, it provides automatic API documentation.

# Persistance:
Application uses Postgres DB. ISO codes and country names are stored in 2 tables, connected with a
many-to-one relationship, where each country name references a proper ISO code. This is our source
of truth.

# Tests:

# Caching

# Docker

# CI/CD