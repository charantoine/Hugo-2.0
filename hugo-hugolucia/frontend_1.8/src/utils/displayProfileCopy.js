import { normalizeDisplayProfile } from './displayProfilePresets.js'

export const DISPLAY_PROFILE_COPY = {
  youth: {
    sessionIntro:
      'Hugo vous aide à avancer pas à pas : racontez votre scène, demandez une synthèse au bon moment, préparez une trace utile.',
    conversationTitle: 'Votre conversation',
    conversationLead: 'Décrivez ce que vous vivez, ce que vous avez testé, ou ce qui vous bloque.',
    questSectionLead: 'Ce que vous devez faire maintenant',
    questPanelNote: 'Objectif affiché tel quel depuis Hugo, sans calcul côté interface.',
    tracesSectionLead: 'Ce qui est déjà prêt à réutiliser ou à partager.',
  },
  adult: {
    sessionIntro:
      'Hugo vous accompagne sur une progression lisible : échangez sur votre situation, sollicitez une synthèse quand c’est pertinent, préparez une trace exploitable.',
    conversationTitle: 'Conversation',
    conversationLead: 'Décrivez un fait, une action testée ou un point de blocage.',
    questSectionLead: 'Objectif en cours',
    questPanelNote: 'Affiché tel quel depuis le contrat `/ui-state`, sans heuristique locale.',
    tracesSectionLead: 'Traces, preuves et éléments déjà réutilisables dans votre parcours.',
  },
  professional: {
    sessionIntro:
      'Hugo vous aide à suivre une progression structurée, demander une synthèse au bon moment et préparer une trace utile sans exposition technique.',
    conversationTitle: 'Conversation',
    conversationLead: 'Décrivez un moment concret, une difficulté rencontrée ou une action à analyser.',
    questSectionLead: 'Objectif actif',
    questPanelNote: 'Affiché tel quel depuis le contrat `/ui-state`, sans heuristique locale.',
    tracesSectionLead: 'Ce panneau rassemble ce qui est déjà réutilisable, partageable et visible comme progression utile.',
  },
}

export function getDisplayProfileCopy(profile) {
  const normalized = normalizeDisplayProfile(profile)
  return DISPLAY_PROFILE_COPY[normalized] || DISPLAY_PROFILE_COPY.professional
}
