const STORAGE_KEY = 'claude-ai-factory-worker-chat-v1'

const ROOM_DEFINITIONS = [
  {
    id: 'research-hub',
    name: 'Research Hub',
    workers: [
      { id: 'trend-scout', name: 'Trend Scout', role: 'Finds trend signals', baseStatus: 'ready' },
      { id: 'niche-scorer', name: 'Niche/Topic Scorer', role: 'Ranks demand vs competition', baseStatus: 'ready' },
      { id: 'performance-analyst', name: 'Performance Analyst', role: 'Summarizes what outperforms', baseStatus: 'ready' },
      { id: 'briefing-writer', name: 'Briefing Writer', role: 'Creates action briefs', baseStatus: 'ready' }
    ]
  },
  {
    id: 'etsy-pod',
    name: 'Etsy Print-on-Demand',
    workers: [
      { id: 'niche-picker', name: 'Niche Picker', role: 'Chooses audience + theme', baseStatus: 'working' },
      { id: 'design-generator', name: 'Design Generator', role: 'Produces sellable designs', baseStatus: 'working' },
      { id: 'copywriter', name: 'Listing Copywriter', role: 'Writes title/tags/description', baseStatus: 'ready' },
      { id: 'publisher', name: 'Publisher', role: 'Syncs listing to Etsy', baseStatus: 'ready' }
    ]
  },
  {
    id: 'youtube-shorts',
    name: 'YouTube Shorts Automation',
    workers: [
      { id: 'topic-picker', name: 'Topic Picker', role: 'Selects topic within pillar', baseStatus: 'working' },
      { id: 'script-writer', name: 'Script Writer', role: 'Writes 30-60s hooks/scripts', baseStatus: 'ready' },
      { id: 'video-assembler', name: 'Video Assembler', role: 'Builds 9:16 shorts', baseStatus: 'ready' },
      { id: 'performance-tracker', name: 'Performance Tracker', role: 'Logs retention + engagement', baseStatus: 'ready' }
    ]
  }
]

function workerConversationKey(roomId, workerId) {
  return `${roomId}:${workerId}`
}

function createThread(index) {
  return {
    id: `thread-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    title: `Thread ${index}`,
    messages: []
  }
}

function defaultConversations() {
  const conversations = {}

  for (const room of ROOM_DEFINITIONS) {
    for (const worker of room.workers) {
      const key = workerConversationKey(room.id, worker.id)
      const initialThread = createThread(1)
      conversations[key] = {
        unreadCount: 0,
        pendingRequest: false,
        threads: [initialThread],
        activeThreadId: initialThread.id
      }
    }
  }

  return conversations
}

function createInitialState() {
  return {
    rooms: ROOM_DEFINITIONS,
    activeRoomId: ROOM_DEFINITIONS[0].id,
    activeWorkerId: ROOM_DEFINITIONS[0].workers[0].id,
    conversations: defaultConversations()
  }
}

function normalizeLoadedState(loadedState) {
  const defaultState = createInitialState()

  if (!loadedState || typeof loadedState !== 'object') {
    return defaultState
  }

  const normalized = {
    ...defaultState,
    ...loadedState,
    rooms: ROOM_DEFINITIONS,
    conversations: defaultConversations()
  }

  for (const room of ROOM_DEFINITIONS) {
    for (const worker of room.workers) {
      const key = workerConversationKey(room.id, worker.id)
      const loadedConversation = loadedState?.conversations?.[key]

      if (!loadedConversation || !Array.isArray(loadedConversation.threads) || loadedConversation.threads.length === 0) {
        continue
      }

      normalized.conversations[key] = {
        unreadCount: Number.isFinite(loadedConversation.unreadCount) ? loadedConversation.unreadCount : 0,
        pendingRequest: Boolean(loadedConversation.pendingRequest),
        threads: loadedConversation.threads.map((thread, index) => ({
          id: thread?.id || createThread(index + 1).id,
          title: thread?.title || `Thread ${index + 1}`,
          messages: Array.isArray(thread?.messages) ? thread.messages : []
        })),
        activeThreadId: loadedConversation.activeThreadId
      }

      const currentConversation = normalized.conversations[key]
      const threadExists = currentConversation.threads.some((thread) => thread.id === currentConversation.activeThreadId)
      if (!threadExists) {
        currentConversation.activeThreadId = currentConversation.threads[0].id
      }
    }
  }

  return normalized
}

function getRoom(state, roomId) {
  return state.rooms.find((room) => room.id === roomId)
}

function getWorker(room, workerId) {
  return room?.workers.find((worker) => worker.id === workerId)
}

function getConversation(state, roomId, workerId) {
  return state.conversations[workerConversationKey(roomId, workerId)]
}

function getActiveConversation(state) {
  return getConversation(state, state.activeRoomId, state.activeWorkerId)
}

function getActiveThread(state) {
  const conversation = getActiveConversation(state)
  return conversation.threads.find((thread) => thread.id === conversation.activeThreadId)
}

function persistState(storage, state) {
  storage?.setItem(
    STORAGE_KEY,
    JSON.stringify({
      activeRoomId: state.activeRoomId,
      activeWorkerId: state.activeWorkerId,
      conversations: state.conversations
    })
  )
}

function statusLabel(worker, conversation) {
  if (conversation.pendingRequest) return 'waiting for input'
  return worker.baseStatus
}

function addMessage(state, roomId, workerId, sender, text, requiresResponse = false) {
  const room = getRoom(state, roomId)
  const worker = getWorker(room, workerId)
  const conversation = getConversation(state, roomId, workerId)
  const activeThread = conversation.threads.find((thread) => thread.id === conversation.activeThreadId)

  activeThread.messages.push({
    id: `msg-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`,
    sender,
    text,
    contextRole: worker.role,
    requiresResponse,
    resolved: !requiresResponse,
    createdAt: new Date().toISOString()
  })

  if (sender === 'worker' && requiresResponse) {
    conversation.pendingRequest = true

    if (state.activeRoomId !== roomId || state.activeWorkerId !== workerId) {
      conversation.unreadCount += 1
    }
  }
}

function renderApp(root, state, storage) {
  const room = getRoom(state, state.activeRoomId)
  const worker = getWorker(room, state.activeWorkerId)
  const activeConversation = getActiveConversation(state)
  const activeThread = getActiveThread(state)

  const roomButtons = state.rooms
    .map(
      (roomOption) => `
      <button class="room-tab ${roomOption.id === state.activeRoomId ? 'active' : ''}" data-action="select-room" data-room-id="${roomOption.id}">
        ${roomOption.name}
      </button>`
    )
    .join('')

  const workerRows = room.workers
    .map((roomWorker) => {
      const conversation = getConversation(state, room.id, roomWorker.id)
      return `
        <tr>
          <td><strong>${roomWorker.name}</strong><br><small>${roomWorker.role}</small></td>
          <td><span class="status">${statusLabel(roomWorker, conversation)}</span></td>
          <td>
            ${conversation.unreadCount > 0 ? `<span class="unread">${conversation.unreadCount} unread</span>` : '<span class="clear">0 unread</span>'}
            ${conversation.pendingRequest ? '<span class="pending">needs reply</span>' : ''}
          </td>
          <td class="actions">
            <button data-action="interact" data-worker-id="${roomWorker.id}">Interact</button>
            <button data-action="worker-ask" data-worker-id="${roomWorker.id}">Worker asks</button>
          </td>
        </tr>
      `
    })
    .join('')

  const threadOptions = activeConversation.threads
    .map(
      (thread) =>
        `<option value="${thread.id}" ${thread.id === activeConversation.activeThreadId ? 'selected' : ''}>${thread.title}</option>`
    )
    .join('')

  const messages = activeThread.messages
    .map(
      (message) => `
      <article class="message ${message.sender}">
        <header>${message.sender === 'manager' ? 'You' : worker.name} • ${message.contextRole}</header>
        <p>${message.text}</p>
        ${message.requiresResponse && !message.resolved ? '<small class="pending">Awaiting your response</small>' : ''}
      </article>`
    )
    .join('')

  root.innerHTML = `
    <main class="layout">
      <section class="left-panel">
        <h1>Claude AI Factory Worker Chat</h1>
        <p class="sub">Click <strong>Interact</strong> to open a worker thread in the selected room.</p>

        <div class="room-tabs">${roomButtons}</div>

        <table>
          <thead>
            <tr>
              <th>Worker</th>
              <th>Status</th>
              <th>Notifications</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${workerRows}
          </tbody>
        </table>
      </section>

      <section class="chat-panel">
        <h2>${room.name} • ${worker.name}</h2>
        <p class="sub">Role context: ${worker.role}</p>

        <div class="thread-controls">
          <label>
            Continue thread:
            <select data-action="select-thread">${threadOptions}</select>
          </label>
          <button data-action="new-thread">Start new thread</button>
          <button data-action="resolve-request" ${activeConversation.pendingRequest ? '' : 'disabled'}>Mark request resolved</button>
        </div>

        <section class="messages" aria-live="polite">
          ${messages || '<p class="empty">No messages yet. Send an idea to get started.</p>'}
        </section>

        <form data-action="send-manager" class="composer">
          <label for="manager-message">Send instruction/idea</label>
          <textarea id="manager-message" name="message" required placeholder="Give this worker a task or idea"></textarea>
          <button type="submit">Send to worker</button>
        </form>

        <form data-action="send-worker" class="composer worker-form">
          <label for="worker-message">Worker update/question</label>
          <textarea id="worker-message" name="message" required placeholder="Simulate worker-generated idea or question"></textarea>
          <label class="checkbox"><input type="checkbox" name="needsResponse" checked /> Worker needs your reply</label>
          <button type="submit">Record worker message</button>
        </form>
      </section>
    </main>
  `

  root.querySelectorAll('[data-action="select-room"]').forEach((button) => {
    button.addEventListener('click', () => {
      state.activeRoomId = button.dataset.roomId
      state.activeWorkerId = getRoom(state, state.activeRoomId).workers[0].id

      const nextConversation = getActiveConversation(state)
      nextConversation.unreadCount = 0
      persistState(storage, state)
      renderApp(root, state, storage)
    })
  })

  root.querySelectorAll('[data-action="interact"]').forEach((button) => {
    button.addEventListener('click', () => {
      state.activeWorkerId = button.dataset.workerId
      const targetConversation = getActiveConversation(state)
      targetConversation.unreadCount = 0
      persistState(storage, state)
      renderApp(root, state, storage)
    })
  })

  root.querySelectorAll('[data-action="worker-ask"]').forEach((button) => {
    button.addEventListener('click', () => {
      const targetWorkerId = button.dataset.workerId
      addMessage(
        state,
        state.activeRoomId,
        targetWorkerId,
        'worker',
        'I generated a new idea and need your approval before proceeding.',
        true
      )
      persistState(storage, state)
      renderApp(root, state, storage)
    })
  })

  root.querySelector('[data-action="new-thread"]').addEventListener('click', () => {
    const conversation = getActiveConversation(state)
    const thread = createThread(conversation.threads.length + 1)
    conversation.threads.unshift(thread)
    conversation.activeThreadId = thread.id
    persistState(storage, state)
    renderApp(root, state, storage)
  })

  root.querySelector('[data-action="resolve-request"]').addEventListener('click', () => {
    const conversation = getActiveConversation(state)
    const thread = getActiveThread(state)

    conversation.pendingRequest = false
    thread.messages = thread.messages.map((message) => {
      if (message.sender === 'worker' && message.requiresResponse) {
        return { ...message, resolved: true }
      }
      return message
    })

    persistState(storage, state)
    renderApp(root, state, storage)
  })

  root.querySelector('[data-action="select-thread"]').addEventListener('change', (event) => {
    const conversation = getActiveConversation(state)
    conversation.activeThreadId = event.target.value
    persistState(storage, state)
    renderApp(root, state, storage)
  })

  root.querySelector('[data-action="send-manager"]').addEventListener('submit', (event) => {
    event.preventDefault()
    const form = event.currentTarget
    const message = form.message.value.trim()
    if (!message) return

    addMessage(state, state.activeRoomId, state.activeWorkerId, 'manager', message)
    form.reset()
    persistState(storage, state)
    renderApp(root, state, storage)
  })

  root.querySelector('[data-action="send-worker"]').addEventListener('submit', (event) => {
    event.preventDefault()
    const form = event.currentTarget
    const message = form.message.value.trim()
    if (!message) return

    addMessage(
      state,
      state.activeRoomId,
      state.activeWorkerId,
      'worker',
      message,
      form.needsResponse.checked
    )

    form.reset()
    form.needsResponse.checked = true
    persistState(storage, state)
    renderApp(root, state, storage)
  })
}

export function createChatApp(rootElement, { storage = window.localStorage } = {}) {
  const loadedState = storage?.getItem(STORAGE_KEY)
  const parsed = loadedState ? JSON.parse(loadedState) : null
  const state = normalizeLoadedState(parsed)

  const activeConversation = getActiveConversation(state)
  activeConversation.unreadCount = 0
  persistState(storage, state)
  renderApp(rootElement, state, storage)

  return {
    getState: () => state,
    storageKey: STORAGE_KEY
  }
}
