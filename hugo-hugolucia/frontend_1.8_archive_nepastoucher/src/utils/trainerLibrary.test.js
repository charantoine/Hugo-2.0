import test from 'node:test'
import assert from 'node:assert/strict'

import {
  approxDocumentSize,
  buildCreateDocumentPayload,
  buildDocumentMeta,
  buildPatchDocumentMetaPayload,
  isDocumentLinked,
  mergeDocumentMeta,
  normalizeDocumentsList,
  normalizeLibraryItems,
} from './trainerLibrary.js'

test('buildDocumentMeta applies defaults', () => {
  assert.deepEqual(buildDocumentMeta(), {
    conversation_role: 'reference_course',
    pedagogical_intent: 'explanation',
    visibility: 'learner_citable',
  })
})

test('mergeDocumentMeta preserves existing keys', () => {
  const merged = mergeDocumentMeta(
    { conversation_role: 'support', trainer_priority: 'high' },
    { conversation_role: 'reference_course' },
  )
  assert.equal(merged.conversation_role, 'reference_course')
  assert.equal(merged.trainer_priority, 'high')
})

test('normalizeDocumentsList handles array and paginated shapes', () => {
  assert.deepEqual(normalizeDocumentsList([{ id: '1' }]), [{ id: '1' }])
  assert.deepEqual(normalizeDocumentsList({ results: [{ id: '2' }] }), [{ id: '2' }])
})

test('normalizeLibraryItems extracts items array', () => {
  assert.deepEqual(normalizeLibraryItems({ items: [{ id: 'gd1' }] }), [{ id: 'gd1' }])
  assert.deepEqual(normalizeLibraryItems({}), [])
})

test('isDocumentLinked detects active group link', () => {
  const items = [
    { document_id: 'a', status: 'ACTIVE' },
    { document_id: 'b', status: 'INACTIVE' },
  ]
  assert.equal(isDocumentLinked(items, 'a'), true)
  assert.equal(isDocumentLinked(items, 'b'), false)
})

test('approxDocumentSize formats char counts', () => {
  assert.equal(approxDocumentSize(0), '—')
  assert.equal(approxDocumentSize(500), '500 car.')
  assert.equal(approxDocumentSize(2500), '3 ko (texte)')
})

test('buildCreateDocumentPayload includes meta contract fields', () => {
  const payload = buildCreateDocumentPayload({
    title: 'Poly C15',
    sourceText: 'procedure tableau electrique',
    meta: buildDocumentMeta({ conversationRole: 'reference_course' }),
  })
  assert.equal(payload.title, 'Poly C15')
  assert.equal(payload.meta.conversation_role, 'reference_course')
  assert.match(payload.source_text, /procedure/)
})

test('buildPatchDocumentMetaPayload merges for inline edit', () => {
  const existing = { conversation_role: 'support', pedagogical_intent: 'explanation' }
  const payload = buildPatchDocumentMetaPayload(existing, { conversation_role: 'reference_course' })
  assert.deepEqual(payload.meta, {
    conversation_role: 'reference_course',
    pedagogical_intent: 'explanation',
  })
})

/**
 * Component-level scenarios (Given/When/Then) — migrables en Playwright si besoin.
 *
 * TRAINER-LIB-01 — Liste bibliothèque
 * Given: GET /groups/{id}/library/ renvoie 2 items ACTIVE
 * When: ProdTrainerLibraryView monte avec groupId
 * Then: 2 entrées visibles dans « Bibliothèque active du groupe »
 *
 * TRAINER-LIB-02 — Création texte
 * Given: formateur sur /app/trainer/library?groupId=…
 * When: titre + texte + meta reference_course, clic « Créer et indexer »
 * Then: POST /documents/ avec meta.conversation_role, puis POST index, puis lien groupe
 *
 * TRAINER-LIB-03 — Édition inline rôle
 * Given: document listé avec meta.support
 * When: select conversation_role → reference_course
 * Then: PATCH /documents/{id}/ avec meta fusionné
 */
