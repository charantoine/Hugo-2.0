-- RLS app role for local / CI tests (cluster 10 — C9-OPS-01)
-- Run as superuser (postgres). Target DB: hugo_poc_test (pytest) or hugo_poc (dev).
-- Usage:
--   psql -U postgres -d hugo_poc_test -f scripts/setup_rls_app_role.sql

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hugo_app_tenant_test') THEN
    CREATE ROLE hugo_app_tenant_test LOGIN PASSWORD 'hugo_rls_test_only'
      NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE;
  END IF;
END
$$;

GRANT CONNECT ON DATABASE hugo_poc_test TO hugo_app_tenant_test;
GRANT USAGE ON SCHEMA public TO hugo_app_tenant_test;

-- Tables must exist (run Django migrate on target DB first), then:
--   psql -U postgres -d hugo_poc_test -c "GRANT SELECT ON TABLE hugo_session, hugo_message, trace, evidence, export_run, learner_state TO hugo_app_tenant_test;"
--   psql -U postgres -d hugo_poc_test -c "GRANT hugo_app_tenant_test TO postgres;"

GRANT hugo_app_tenant_test TO postgres;
