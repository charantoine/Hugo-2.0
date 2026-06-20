/**
 * Admin navigation — learner conversation modes (metier labels).
 * Posture codes must match backend ConversationPosture.
 */
import { LEARNER_POSTURES } from './conversationPostures'

export const LEARNER_MODE_SLUGS = ['diagnostic', 'reflective_afest', 'knowledge_review']

/** Static orchestrator params mirrored from hugo_back/domain/tutor_profiles.py (read-only Phase 1). */
export const ORCHESTRATOR_STATIC_PARAMS = {
  diagnostic: {
    max_branches: 3,
    synthesis_requires: 'orange_or_green',
    evaluation_requires: 'green',
    green_requires_transfer: false,
  },
  reflective_afest: {
    max_branches: 3,
    synthesis_requires: 'orange_or_green',
    evaluation_requires: 'green',
    green_requires_transfer: true,
  },
  knowledge_review: {
    max_branches: 1,
    synthesis_requires: 'orange_or_green',
    evaluation_requires: 'green',
    green_requires_transfer: false,
  },
}

export const ADMIN_CONVERSATION_SECTIONS = [
  {
    id: 'learner',
    title: 'Conversation apprenant',
    items: [
      {
        path: '/admin/conversation/learner/profiles',
        label: 'Profils conversationnels',
        description: 'Profil global apprenant : diag, réflexif, bûchage et évaluation finale.',
      },
      ...LEARNER_POSTURES.map((p) => ({
        path: `/admin/conversation/learner/${p.code}`,
        label: p.code === 'knowledge_review' ? 'Buchage (legacy)' : `${p.label} (legacy)`,
        description: `${p.description} — édition par posture (mode expert).`,
      })),
      {
        path: '/admin/conversation/learner/closing',
        label: 'Clôture évaluation (legacy)',
        description: 'Profils d’évaluation, politique org et paramètres de clôture.',
      },
    ],
  },
  {
    id: 'tutor',
    title: 'Conversation tuteur',
    items: [
      {
        path: '/admin/conversation/tutor',
        label: 'Orchestrateur tuteur',
        description: 'Paramètres d’accompagnement et liens vers l’espace tuteur prod.',
      },
    ],
  },
  {
    id: 'trainer',
    title: 'Conversation formateur',
    items: [
      {
        path: '/admin/conversation/trainer',
        label: 'Orchestrateur formateur',
        description: 'Préparation du matériau pédagogique et base de connaissances.',
      },
    ],
  },
]

export const LEGACY_ADMIN_ROUTES = [
  { path: '/tutor-prompts', label: 'Prompts apprenant (legacy 1.6)' },
  { path: '/conduct-profiles', label: 'Profils de conduite apprenant (legacy)' },
]

export function learnerModeMeta(postureCode) {
  const posture = LEARNER_POSTURES.find((p) => p.code === postureCode)
  if (!posture) return null
  const buchageLabel = postureCode === 'knowledge_review' ? 'Buchage' : posture.label
  return {
    ...posture,
    adminLabel: buchageLabel,
    staticParams: ORCHESTRATOR_STATIC_PARAMS[postureCode] || null,
  }
}

export function isValidLearnerPostureCode(code) {
  return LEARNER_MODE_SLUGS.includes(String(code || ''))
}
