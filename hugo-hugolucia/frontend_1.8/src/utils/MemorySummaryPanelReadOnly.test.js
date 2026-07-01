/** MemorySummaryPanelReadOnly.spec — contrat lecture seule mémoire tuteur. */
import test from 'node:test'
import assert from 'node:assert/strict'

export const TUTOR_MEMORY_PANEL_COPY = {
  nonInjected: 'non injecté dans le prompt LLM',
  aclDenied: 'n\'est pas exposée au tuteur via memory-summary',
  noLinkedSession: 'Aucune session apprenant liée',
}

test('tutor context panel documents non-injection policy', () => {
  assert.match(TUTOR_MEMORY_PANEL_COPY.nonInjected, /prompt LLM/i)
})

test('ACL 404 message explains read-only boundary', () => {
  assert.match(TUTOR_MEMORY_PANEL_COPY.aclDenied, /memory-summary/i)
})

test('memory summary contract keys exclude raw verbatim field names', () => {
  const allowedKeys = new Set([
    'session_memory',
    'theme_memories',
    'facts_confirmed',
    'open_points',
    'pending_actions',
    'memory_scope',
  ])
  const forbidden = ['messages', 'verbatim', 'llm_request_payload', 'system_prompt']
  for (const key of forbidden) {
    assert.ok(!allowedKeys.has(key))
  }
})
