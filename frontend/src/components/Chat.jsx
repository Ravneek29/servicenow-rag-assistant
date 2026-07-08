import { useEffect, useRef, useState } from 'react'
import Message from './Message.jsx'
import { askQuestion } from '../api.js'

const SUGGESTIONS = [
  'How is incident priority calculated?',
  'What is the difference between a normal and a standard change?',
  'How does the IRE prevent duplicate CIs?',
  'When does a resolved incident auto-close?',
]

export default function Chat({ hasDocuments }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const ask = async (question) => {
    const trimmed = question.trim()
    if (!trimmed || loading) return
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: trimmed }])
    setLoading(true)
    try {
      const res = await askQuestion(trimmed)
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: res.answer, sources: res.sources },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', text: `Something went wrong: ${err.message}`, isError: true },
      ])
    }
    setLoading(false)
  }

  return (
    <main className="chat">
      <div className="chat-scroll">
        {messages.length === 0 && (
          <div className="chat-empty">
            <h2>Ask anything about your ServiceNow documentation</h2>
            <p>
              {hasDocuments
                ? 'Your knowledge base is ready. Try one of these:'
                : 'Upload documentation (or load the sample docs) to get started, then try:'}
            </p>
            <div className="suggestions">
              {SUGGESTIONS.map((s) => (
                <button key={s} className="suggestion" onClick={() => ask(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}

        {loading && (
          <div className="message message--assistant">
            <div className="bubble bubble--thinking">
              Retrieving documentation and generating answer…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form
        className="chat-input"
        onSubmit={(e) => { e.preventDefault(); ask(input) }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="e.g. What approvals does an emergency change need?"
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          Ask
        </button>
      </form>
    </main>
  )
}
