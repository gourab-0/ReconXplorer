# Database Migrations – ReconXplorer

This project uses Alembic for database schema migrations.

## Initial Setup
- SQLAlchemy models are defined in `app/models/`
- Alembic tracks schema changes using revision files

## Workflow for Schema Changes

1. Modify or add SQLAlchemy models
2. Generate migration:
   alembic revision --autogenerate -m "describe_change"
3. Apply migration:
   alembic upgrade head

## Rules
- Never modify the database manually
- Never use Base.metadata.create_all() after initial setup
- All schema changes must go through Alembic

## Status
- Database schema is fully synchronized with models
- Migration history is clean and linear
