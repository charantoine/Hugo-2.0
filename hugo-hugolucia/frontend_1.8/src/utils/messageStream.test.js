import test from 'node:test'
import assert from 'node:assert/strict'

import { consumeSseBuffer, parseSseEventBlock } from './messageStream.js'

test('parseSseEventBlock parses SSE event with JSON payload', () => {
  const event = parseSseEventBlock('event: chunk\ndata: {"text":"Bonjour"}')

  assert.deepEqual(event, {
    event: 'chunk',
    data: { text: 'Bonjour' },
  })
})

test('consumeSseBuffer returns parsed events and keeps trailing remainder', () => {
  const { events, remainder } = consumeSseBuffer(
    'event: chunk\ndata: {"text":"Bon"}\n\nevent: chunk\ndata: {"text":"jour"}\n\nevent: do',
  )

  assert.deepEqual(events, [
    { event: 'chunk', data: { text: 'Bon' } },
    { event: 'chunk', data: { text: 'jour' } },
  ])
  assert.equal(remainder, 'event: do')
})
