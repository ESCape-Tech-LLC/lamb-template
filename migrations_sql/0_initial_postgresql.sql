-- PostgreSQL
\c postgres
DROP DATABASE IF EXISTS {{project_name}};
DROP ROLE IF EXISTS {{project_name}}_user;


CREATE ROLE {{project_name}}_user WITH LOGIN PASSWORD '{% for s in "x"|rjust:"20" %}{{secret_key|make_list|random}}{%endfor%}'
    INHERIT
    CONNECTION LIMIT -1
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;


CREATE DATABASE {{project_name}}
    WITH OWNER = {{project_name}}_user
    ENCODING = 'UTF8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1
    LC_COLLATE ='en_US.UTF-8'
    LC_CTYPE ='en_US.UTF-8'
    TEMPLATE template0;

\c {{project_name}}
CREATE EXTENSION pgcrypto;
