import { test } from '@playwright/test'

/**
 * LOT 5–7, 9, 11 — scaffold : prérequis données / mots de passe manquants pour démo melec.
 * Exécuter avec smoke-fixtures + bootstrap quand disponibles.
 */
const SKIP_REASON =
  'Scaffold — nécessite mots de passe apprenant/tuteur démo ou SMOKE_RUN_TENANT=1 pour associations et synthèse complète'

test.describe('LOT 5 — Associations tuteur/apprenant', () => {
  test.skip(true, SKIP_REASON)
  test('L5-tutor sees only linked learners', async () => {})
})

test.describe('LOT 6 — Profils conversationnels', () => {
  test.skip(true, 'Utiliser e2e/admin_learner_profiles.spec.ts avec SMOKE_RUN_TENANT=1')
  test('L6-profile assign persists on group', async () => {})
})

test.describe('LOT 7 — Référentiel / bibliothèque', () => {
  test.skip(true, SKIP_REASON)
  test('L7-RNCP38878 attached and library visible', async () => {})
})

test.describe('LOT 9 — Synthèse / évaluation / trace', () => {
  test.skip(true, 'Nécessite session en état synthesis_eligible — voir cluster16 fixtures')
  test('L9-request-synthesis wired', async () => {})
})

test.describe('LOT 11 — Formateur', () => {
  test.skip(true, 'Couvert partiellement par test_smoke_trainer.spec.ts')
  test('L11-trainer knowledge route', async () => {})
})
