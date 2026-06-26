-- TAK database base setup.
-- Extensions and grants are handled by pg_init/03_tak.sh at postgres startup.
-- SchemaManager (called after this) handles the full schema.
-- This file is intentionally minimal.

SET client_min_messages TO WARNING;

-- Ensure extensions exist (idempotent — pg_init may have already created them)
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;
