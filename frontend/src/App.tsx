import { useState } from 'react'
import { askQuestion } from './api/ask'
import Composer from './components/Composer'
import MessageList from './components/MessageList'
import type { ChatMessage } from './types'

function makeId() {
  return crypto.randomUUID()
}

function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [isPending, setIsPending] = useState(false)

  async function handleSubmit(question: string) {
    const assistantId = makeId()
    setMessages((prev) => [
      ...prev,
      { id: makeId(), role: 'user', question },
      { id: assistantId, role: 'assistant', status: 'loading' },
    ])
    setIsPending(true)

    try {
      const { results } = await askQuestion(question)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { id: assistantId, role: 'assistant', status: 'done', results }
            : m,
        ),
      )
    } catch {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantId
            ? { id: assistantId, role: 'assistant', status: 'error' }
            : m,
        ),
      )
    } finally {
      setIsPending(false)
    }
  }

  return (
    <div className="flex h-screen flex-col bg-discord-bg">
      <header className="border-b border-discord-darkest px-4 py-4 sm:px-8">
        <h1 className="text-lg font-semibold text-discord-text">Ask the server</h1>
        <p className="text-sm text-discord-muted">
          Search this Discord server's message history
        </p>
      </header>
      <MessageList messages={messages} />
      <Composer onSubmit={handleSubmit} disabled={isPending} />
    </div>
  )
}

export default App
