DROP SCHEMA public CASCADE;

CREATE SCHEMA public AUTHORIZATION postgres;

GRANT ALL ON SCHEMA public TO postgres;
COMMENT ON SCHEMA public IS 'standard public schema';
