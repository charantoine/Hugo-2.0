export function getAssistantDisplayVariants(message) {
  if (!message || message.role !== 'ASSISTANT') return {}
  const payload = message.assistant_display_variants
  return payload && typeof payload === 'object' ? payload : {}
}

export function getAssistantAvailableVariants(message) {
  const variants = getAssistantDisplayVariants(message)
  const available = Array.isArray(variants.available_variants)
    ? variants.available_variants.filter((item) => item === 'short' || item === 'long')
    : []
  if (available.length) return available
  const shortText = String(variants.short || '').trim()
  const longText = String(variants.long || '').trim()
  if (shortText && longText && shortText !== longText) return ['short', 'long']
  if (shortText) return ['short']
  if (longText) return ['long']
  return []
}

export function getAssistantDefaultVariant(message) {
  const variants = getAssistantDisplayVariants(message)
  const available = getAssistantAvailableVariants(message)
  const preferred = String(variants.default_variant || '').trim()
  if (available.includes(preferred)) return preferred
  if (available.includes('short')) return 'short'
  if (available.length) return available[0]
  return 'short'
}

export function resolveAssistantContent(message, selectedVariant = '') {
  if (!message) return ''
  if (message.role !== 'ASSISTANT') return String(message.content || '')
  const beforeGuardrails = String(
    message.llm_response_payload?.assistant_text_before_guardrails || '',
  ).trim()
  if (beforeGuardrails) return beforeGuardrails
  const variants = getAssistantDisplayVariants(message)
  const available = getAssistantAvailableVariants(message)
  const effectiveVariant = available.includes(selectedVariant)
    ? selectedVariant
    : getAssistantDefaultVariant(message)
  const variantContent = String(variants[effectiveVariant] || '').trim()
  if (variantContent) return variantContent
  return String(message.content || '')
}

export function extractNumberedQuestions(text) {
  const content = String(text || '').trim()
  if (!content) return []
  const lines = content.split('\n')
  const parsed = []
  const pattern = /^\s*(\d{1,2})\s*[\.\)\:\-]?\s*(.+?)\s*$/
  for (const line of lines) {
    const match = line.match(pattern)
    if (!match) continue
    const index = Number(match[1])
    if (!index) continue
    let question = match[2].trim()
    while (/^\d+\s*[\.\)\:\-]\s*/.test(question)) {
      question = question.replace(/^\d+\s*[\.\)\:\-]\s*/, '').trim()
    }
    if (!question) continue
    parsed.push({ index, question })
  }
  return parsed.sort((a, b) => a.index - b.index)
}
