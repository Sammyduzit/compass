import { useState, useRef, useEffect } from 'react'
import type { SummaryData, RulesData, DeveloperProfile } from '../types'
import './ChatPanel.css'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  summary: SummaryData
  rules: RulesData
  developerProfile: DeveloperProfile | null
  onProfileSet: (profile: DeveloperProfile) => void
}

export default function ChatPanel({ summary, developerProfile, onProfileSet }: Props) {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const awaitingName = !developerProfile
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  function handleSend() {
    const text = input.trim()
    if (!text) return

    if (awaitingName) {
      onProfileSet({ name: text })
      setMessages([
        { role: 'user', content: text },
        {
          role: 'assistant',
          content: `Good to meet you, ${text}. I have everything Compass found about ${summary.repo_name} — ask me anything.`,
        },
      ])
      setInput('')
      return
    }

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    // API call wired here once FastAPI layer (#59) lands
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="chat-panel">
      <div className="chat-panel__header">
        <span>Ask Compass</span>
        <code className="chat-panel__repo">{summary.repo_name}</code>
      </div>

      <div className="chat-panel__messages">
        {messages.length === 0 && (
          <div className="chat-panel__welcome">
            <p>{awaitingName ? "What's your name?" : `Ask me anything about ${summary.repo_name}.`}</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`chat-message chat-message--${msg.role}`}>
            {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-panel__input-area">
        <textarea
          className="chat-panel__input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={awaitingName ? 'Your name...' : 'Ask a question...'}
          rows={1}
        />
        <button className="chat-panel__send" onClick={handleSend} disabled={!input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}
