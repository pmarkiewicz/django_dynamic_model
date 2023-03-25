-- all changes to database to work correctly with project
-- username is api
-- database is api

CREATE USER api WITH PASSWORD 'xxxxxxx';

ALTER ROLE api SET client_encoding TO 'utf8';

ALTER ROLE api SET default_transaction_isolation TO 'read committed';

ALTER ROLE api SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE api TO api;

-- this one is required to create tables
GRANT ALL ON SCHEMA public TO api;