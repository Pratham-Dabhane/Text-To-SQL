CREATE ROLE text_to_sql_reader LOGIN PASSWORD 'reader_dev_password';
GRANT CONNECT ON DATABASE text_to_sql_learning TO text_to_sql_reader;

\connect text_to_sql_learning

\i /workspace-db/schema.sql
\i /workspace-db/seed.sql

GRANT USAGE ON SCHEMA public TO text_to_sql_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO text_to_sql_reader;
