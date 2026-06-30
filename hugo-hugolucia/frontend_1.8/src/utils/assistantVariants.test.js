import test from 'node:test'
import assert from 'node:assert/strict'

import {
  extractNumberedQuestions,
  getAssistantAvailableVariants,
  getAssistantDefaultVariant,
  resolveAssistantContent,
} from './assistantVariants.js'

test('resolveAssistantContent prefers selected long variant', () => {
  const message = {
    role: 'ASSISTANT',
    content: '1. Version courte ?',
    assistant_display_variants: {
      short: '1. Version courte ?',
      long: 'Introduction\n1. Version longue ?\n2. Autre question ?',
      default_variant: 'short',
      available_variants: ['short', 'long'],
    },
  }

  assert.equal(resolveAssistantContent(message, 'long'), 'Introduction\n1. Version longue ?\n2. Autre question ?')
})

test('resolveAssistantContent falls back to content when variants are absent', () => {
  const message = {
    role: 'ASSISTANT',
    content: 'Message historique',
  }

  assert.equal(resolveAssistantContent(message), 'Message historique')
  assert.deepEqual(getAssistantAvailableVariants(message), [])
  assert.equal(getAssistantDefaultVariant(message), 'short')
})

test('extractNumberedQuestions parses displayed numbered questions', () => {
  const text = "C'est un choc.\n1. Que s'est-il passe ?\n2. Qu'as-tu verifie ?"

  assert.deepEqual(extractNumberedQuestions(text), [
    { index: 1, question: "Que s'est-il passe ?" },
    { index: 2, question: "Qu'as-tu verifie ?" },
  ])
})
