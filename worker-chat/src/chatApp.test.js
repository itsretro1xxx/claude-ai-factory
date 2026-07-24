// @vitest-environment jsdom
import { beforeEach, describe, expect, test } from 'vitest'
import { fireEvent, getByLabelText, getByRole, getByText, queryByText, within } from '@testing-library/dom'
import { createChatApp } from './chatApp'

class MemoryStorage {
  constructor() {
    this.store = new Map()
  }

  getItem(key) {
    return this.store.has(key) ? this.store.get(key) : null
  }

  setItem(key, value) {
    this.store.set(key, String(value))
  }

  removeItem(key) {
    this.store.delete(key)
  }

  clear() {
    this.store.clear()
  }
}

function mountApp(storage = new MemoryStorage()) {
  document.body.innerHTML = '<div id="app"></div>'
  const root = document.querySelector('#app')
  createChatApp(root, { storage })
  return { root, storage }
}

function openRoom(root, roomName) {
  fireEvent.click(getByRole(root, 'button', { name: roomName }))
}

function openWorkerChat(root, workerName) {
  const workerLabel = getByText(root, workerName)
  const row = workerLabel.closest('tr')
  fireEvent.click(within(row).getByRole('button', { name: 'Interact' }))
}

describe('worker chat app', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  test('opens worker chat when Interact is clicked', () => {
    const { root } = mountApp()

    openRoom(root, 'YouTube Shorts Automation')
    openWorkerChat(root, 'Script Writer')

    expect(getByRole(root, 'heading', { name: /YouTube Shorts Automation • Script Writer/i })).toBeTruthy()
  })

  test('supports sending manager and worker messages', () => {
    const { root } = mountApp()

    const managerInput = getByLabelText(root, 'Send instruction/idea')
    fireEvent.input(managerInput, { target: { value: 'Please generate 3 niche ideas.' } })
    fireEvent.click(getByRole(root, 'button', { name: 'Send to worker' }))

    const workerInput = getByLabelText(root, 'Worker update/question')
    fireEvent.input(workerInput, { target: { value: 'I found 3 options. Which one should I prioritize?' } })
    fireEvent.click(getByRole(root, 'button', { name: 'Record worker message' }))

    expect(getByText(root, 'Please generate 3 niche ideas.')).toBeTruthy()
    expect(getByText(root, 'I found 3 options. Which one should I prioritize?')).toBeTruthy()
    expect(getByText(root, 'Awaiting your response')).toBeTruthy()
  })

  test('loads persisted chat history by room and worker', () => {
    const storage = new MemoryStorage()
    const firstMount = mountApp(storage)

    const managerInput = getByLabelText(firstMount.root, 'Send instruction/idea')
    fireEvent.input(managerInput, { target: { value: 'Track conversions for this week.' } })
    fireEvent.click(getByRole(firstMount.root, 'button', { name: 'Send to worker' }))

    const secondMount = mountApp(storage)
    expect(getByText(secondMount.root, 'Track conversions for this week.')).toBeTruthy()
  })

  test('shows unread worker questions when worker asks outside active chat', () => {
    const { root } = mountApp()

    const activeHeading = getByRole(root, 'heading', { name: /Research Hub • Trend Scout/i })
    expect(activeHeading).toBeTruthy()

    const scorerRow = getByText(root, 'Niche/Topic Scorer').closest('tr')
    fireEvent.click(within(scorerRow).getByRole('button', { name: 'Worker asks' }))

    const updatedScorerRow = getByText(root, 'Niche/Topic Scorer').closest('tr')
    expect(within(updatedScorerRow).getByText('1 unread')).toBeTruthy()
    expect(within(updatedScorerRow).getByText('needs reply')).toBeTruthy()

    openWorkerChat(root, 'Niche/Topic Scorer')
    const resolvedRow = getByText(root, 'Niche/Topic Scorer').closest('tr')
    expect(queryByText(resolvedRow, '1 unread')).toBeNull()
  })
})
