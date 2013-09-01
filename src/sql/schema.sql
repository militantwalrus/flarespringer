
DROP DATABASE IF EXISTS flarespringer;
CREATE DATABASE flarespringer;
\c flarespringer;


-- what script to run, how often
CREATE TABLE checks (
  id SERIAL NOT NULL PRIMARY KEY,
  name VARCHAR(128) NOT NULL UNIQUE,
  script VARCHAR(128) NOT NULL,
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

CREATE INDEX checks_name ON checks (name);
CREATE INDEX checks_created ON checks (created);

-- how to interpret results.results
CREATE TABLE rules (
  id SERIAL NOT NULL PRIMARY KEY,
  lookback INTEGER NOT NULL,
  name VARCHAR(128) NOT NULL UNIQUE,
  rule TEXT,
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

-- machine/host/VM roles e.g. 'www' or 'db' or 'amqp'
CREATE TABLE roles (
  id SERIAL NOT NULL PRIMARY KEY,
  name VARCHAR(128) NOT NULL UNIQUE,
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

CREATE TABLE role_check_map (
  role_id INTEGER NOT NULL,
  check_id INTEGER NOT NULL,
  frequency INTEGER NOT NULL
);

CREATE INDEX role_check_map_idx_role ON role_check_map (role_id);
CREATE INDEX role_check_map_idx_check ON role_check_map (check_id);

-- mapping of checks to their interpreting rules
CREATE TABLE rule_check_map (
  rule_id INTEGER NOT NULL,
  check_id INTEGER NOT NULL
);

CREATE INDEX rule_check_map_idx_rule ON rule_check_map (rule_id);
CREATE INDEX rule_check_map_idx_check ON rule_check_map (check_id);

-- store json array of nagios-compatible (0, 1, 2) for a given check
-- the length of that array is governed by
CREATE TABLE results (
  id SERIAL NOT NULL PRIMARY KEY,
  check_id INTEGER NOT NULL,
  results TEXT NOT NULL,
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

CREATE INDEX results_check_id_idx ON results (check_id);

-- info about hosts who should also run checks from 'outside' the target host to be checked
CREATE TABLE helper_hosts (
  id SERIAL NOT NULL PRIMARY KEY,
  hostname VARCHAR(128),
  check_user VARCHAR(64),
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

-- flarespringer central system users
CREATE TABLE users (
  id SERIAL NOT NULL PRIMARY KEY,
  username VARCHAR(64) NOT NULL,
  password VARCHAR(128) NOT NULL,
  first_name VARCHAR(64) NOT NULL,
  last_name VARCHAR(64) NOT NULL,
  created TIMESTAMP NOT NULL,
  modified TIMESTAMP NOT NULL,
  modified_by INTEGER NOT NULL
);

CREATE UNIQUE INDEX username_idx ON users (username);

DROP ROLE IF EXISTS flarespringer;
CREATE ROLE flarespringer
  LOGIN
  PASSWORD 'j3rrysgun';

GRANT SELECT, INSERT, UPDATE, DELETE ON checks TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON rules TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON roles TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON role_check_map TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON rule_check_map TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON results TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON helper_hosts TO flarespringer;
GRANT SELECT, INSERT, UPDATE, DELETE ON users TO flarespringer;

GRANT USAGE, SELECT ON SEQUENCE checks_id_seq TO flarespringer;
GRANT USAGE, SELECT ON SEQUENCE rules_id_seq TO flarespringer;
GRANT USAGE, SELECT ON SEQUENCE roles_id_seq TO flarespringer;
GRANT USAGE, SELECT ON SEQUENCE results_id_seq TO flarespringer;
GRANT USAGE, SELECT ON SEQUENCE helper_hosts_id_seq TO flarespringer;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO flarespringer;

-- CREATE THE DEFAULT ADMIN USER

INSERT INTO users (
  username,
  password,
  first_name,
  last_name,
  created,
  modified,
  modified_by
) VALUES (
  'admin',
  -- '49592ff622d042d7aed54312c1c31acf051c30c9edccc5bf89cd8e63d7cebdf3',   -- sp@nnish 1nqu1s1t10n
  '49592ff622d042d7aed543129c49b9d085ed9b1b1173cd49c6f7d57e459eddad', -- foobar
  'admin',
  'admin',
  now(),
  now(),
  0
);

UPDATE USERS set modified_by = (SELECT id FROM users);


