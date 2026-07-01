/** Affichage lecture seule des métadonnées TrainerKnowledgeItem (sans logique métier). */

export function summarizeDecisionRationale(item) {
  const rationale = item?.meta?.decision_rationale
  if (!rationale || typeof rationale !== 'object') return null

  const envisionedDecision = String(rationale.envisioned_decision || '').trim()
  if (!envisionedDecision) return null

  return {
    envisionedDecision,
    reasons: String(rationale.reasons || '').trim(),
    risks: String(rationale.risks || '').trim(),
    status: String(rationale.status || 'draft').trim(),
    isDraft: String(rationale.status || 'draft').trim() === 'draft',
  }
}
