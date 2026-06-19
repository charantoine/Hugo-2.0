-- Cluster 11 — Audit RLS prod minimal (template)
-- À exécuter sur l'instance Postgres PROD avec un rôle applicatif réel (NON superuser).
-- Ne pas committer de mots de passe. Adapter noms rôle/DB.

-- 1) Vérifier RLS activé
SELECT c.relname AS table_name, c.relrowsecurity AS rls_enabled, c.relforcerowsecurity AS force_rls
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'public'
  AND c.relname IN ('hugo_session', 'trace', 'evidence', 'export_run')
ORDER BY c.relname;

-- 2) Lister policies tenant
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
FROM pg_policies
WHERE tablename IN ('hugo_session', 'trace', 'evidence', 'export_run')
ORDER BY tablename, policyname;

-- 3) Scénario cross-tenant (remplacer UUID org A / org B / session org B)
-- Se connecter en tant que ROLE_APPLICATIF (pas postgres superuser) :
--   SET app.organisation_id = '<ORG_A_UUID>';
--   SELECT count(*) FROM hugo_session WHERE organisation_id = '<ORG_B_UUID>';
-- Attendu : 0 lignes visibles malgré filtre explicite absent côté policy.

-- 4) Vérifier que le rôle prod n'est pas superuser / bypass
SELECT rolname, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user;
