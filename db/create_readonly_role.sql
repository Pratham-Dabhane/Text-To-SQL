-- Run as a PostgreSQL administrator connected to text_to_sql_learning.
-- Set the password interactively with: \password text_to_sql_reader

DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'text_to_sql_reader') THEN
        CREATE ROLE text_to_sql_reader LOGIN;
    END IF;
END
$$;

GRANT CONNECT ON DATABASE text_to_sql_learning TO text_to_sql_reader;
GRANT USAGE ON SCHEMA public TO text_to_sql_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO text_to_sql_reader;
