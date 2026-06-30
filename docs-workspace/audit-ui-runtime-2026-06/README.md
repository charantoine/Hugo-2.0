# Audit UI runtime — juin 2026

Dossier de preuves et rapport pour l'audit **lisibilité front admin/superadmin** (mode `tester`).

| Fichier | Contenu |
|---------|---------|
| [`AUDIT_ADMIN_UI_RUNTIME.md`](AUDIT_ADMIN_UI_RUNTIME.md) | Rapport complet (tableau par page, top 10, synthèse) |
| [`screenshots/`](screenshots/) | 15 captures avant UX + [`manifest.json`](screenshots/manifest.json) |
| [`screenshots-post-ux/`](screenshots-post-ux/) | 15 captures après ajustements UX |
| [`VERIF_SUFFIXE_MK1_MK2_2026-06-26.md`](../VERIF_SUFFIXE_MK1_MK2_2026-06-26.md) | Vérification exhaustive absence dérive UX mk1/mk2 |
| [`../DOC_RUNTIME_UPDATE_2026-06.md`](../DOC_RUNTIME_UPDATE_2026-06.md) | Synthèse croisée doc A1–A4 ↔ runtime |
| [`QA_POST_UX_2026-06-23.md`](QA_POST_UX_2026-06-23.md) | QA runtime après ajustements UX front |

**Reproduction :**

```bash
cd hugo-hugolucia/frontend_1.8
# Prérequis : front sur :5173 (tester), back local sur :8000, VITE_API_URL=/api
node scripts/audit_admin_ui_capture.mjs
```
