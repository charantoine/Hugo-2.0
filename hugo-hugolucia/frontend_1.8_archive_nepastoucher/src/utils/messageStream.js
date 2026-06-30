export function parseSseEventBlock(block) {
  const lines = String(block || '').split('\n')
  let event = 'message'
  const dataLines = []

  for (const rawLine of lines) {
    const line = String(rawLine || '').trimEnd()
    if (!line) continue
    if (line.startsWith(':')) continue
    if (line.startsWith('event:')) {
      event = line.slice(6).trim() || 'message'
      continue
    }
    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trim())
    }
  }

  const rawData = dataLines.join('\n')
  if (!rawData) return null

  try {
    return { event, data: JSON.parse(rawData) }
  } catch {
    return { event, data: { text: rawData } }
  }
}

export function consumeSseBuffer(buffer) {
  const source = String(buffer || '')
  const chunks = source.split('\n\n')
  const remainder = chunks.pop() || ''
  const events = chunks
    .map(parseSseEventBlock)
    .filter(Boolean)
  return { events, remainder }
}
