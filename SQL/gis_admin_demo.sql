--a demo of the roles and permissions assignment for a GIS db done in my past experiences. 


CREATE SCHEMA gis_raw; 
CREATE SCHEMA gis_core;
CREATE SCHEMA gis_reference;
CREATE SCHEMA gis_analysis;
CREATE SCHEMA gis_staging;
CREATE SCHEMA gis_admin;

REVOKE CONNECT ON DATABASE your_database_name FROM PUBLIC; -- do not allow public role to access database

--create gis editor role
CREATE ROLE gis_editor 
LOGIN 
PASSWORD 'gis_editor_pass';
GRANT CONNECT ON DATABASE gis_team_demo TO gis_editor;
-- Allow SELECT, INSERT, UPDATE, DELETE on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA gis_raw
TO gis_editor;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA gis_core
TO gis_editor;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA gis_reference
TO gis_editor;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA gis_analysis
TO gis_editor;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA gis_staging
TO gis_editor;

GRANT SELECT, INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA prod
TO gis_editor;
-- GIS editor role endline



-- Create the role gis_admin
CREATE ROLE gis_admin
    LOGIN
    PASSWORD 'gis_admin_pass';

-- Allow connection to the database for gis_admin
GRANT CONNECT ON DATABASE gis_team_demo TO gis_admin;


-- Grant schema access + full table privileges to gis_admin
DO $$
DECLARE
    schema_name text;
BEGIN
    FOR schema_name IN
        SELECT nspname
        FROM pg_namespace
        WHERE nspname NOT IN (
            'pg_catalog',
            'information_schema'
        )
        AND nspname NOT LIKE 'pg_toast%'
    LOOP

        -- Can access and create objects in the schema
        EXECUTE format(
            'GRANT USAGE, CREATE ON SCHEMA %I TO gis_admin',
            schema_name
        );

        -- Full CRUD/control over existing tables
        EXECUTE format(
            'GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA %I TO gis_admin',
            schema_name
        );

        -- Needed for serial/identity columns
        EXECUTE format(
            'GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA %I TO gis_admin',
            schema_name
        );

        -- Full access to functions
        EXECUTE format(
            'GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA %I TO gis_admin',
            schema_name
        );

    END LOOP;
END
$$;


-- GRANT role_name TO user_name;





--gis viewer creation and permissions
-- Create the read-only role
CREATE ROLE gis_viewer
    LOGIN
    PASSWORD 'gis_viewer_pass';


-- Allow the role to connect to the database
GRANT CONNECT ON DATABASE gis_team_demo TO gis_viewer;


-- Allow access to the prod schema
GRANT USAGE ON SCHEMA prod TO gis_viewer;


-- Read-only access to all existing tables
GRANT SELECT
ON ALL TABLES IN SCHEMA prod
TO gis_viewer;


-- Automatically grant SELECT on future tables
ALTER DEFAULT PRIVILEGES
IN SCHEMA prod
GRANT SELECT ON TABLES TO gis_viewer;

