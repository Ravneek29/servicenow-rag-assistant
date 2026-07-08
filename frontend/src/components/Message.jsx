import { useState } from 'react'

/* Split answer text on [n] citation markers and render them as chips. */
function renderWithCitations(text, sources, onCite) {
  const parts = text.split(/(\[\d+(?:,\s*\d+)*\])/g)
  return parts.map((part, i) => {
    const match = part.match(/^\[([\d,\s]+)\]$/)
    if (!match) return <span key={i}>{part}</span>
    return match[1].split(',').map((num, j) => {
      const id = parseInt(num.trim(), 10)
      const source = sources?.find((s) => s.id === id)
      if (!source) return <span key={`${i}-${j}`}>[{num.trim()}]</span>
      return (
        <button
          key={`${i}-${j}`}
          className="citation-chip"
          title={source.source}
          onClick={() => onCite(id)}
        >
          {id}
        </button>
      )
    })
  })
}

export default function Message({ message }) {
  const [openSource, setOpenSource] = useState(null)
  const { role, text, sources, isError } = message

  if (role === 'user') {
    return (
      <div className="message message--user">
        <div className="bubble bubble--user">{text}</div>
      </div>
    )
  }

  const active = sources?.find((s) => s.id === openSource)

  return (
    <div className="message message--assistant">
      <div className={`bubble ${isError ? 'bubble--error' : ''}`}>
        <div className="answer-text">
          {sources?.length
            ? renderWithCitations(text, sources, (id) =>
                setOpenSource((cur) => (cur === id ? null : id)))
            : text}
        </div>

        {active && (
          <div className="source-preview">
            <div className="source-preview-header">
              <strong>[{active.id}] {active.source}</strong>
              {active.page && <span> · page {active.page}</span>}
              <span> · relevance {active.score}</span>
            </div>
            <p>{active.snippet}…</p>
          </div>
        )}

        {sources?.length > 0 && (
          <div className="sources-row">
            <span className="sources-label">Sources:</span>
            {sources.map((s) => (
              <button
                key={s.id}
                className={`citation-chip ${openSource === s.id ? 'citation-chip--open' : ''}`}
                onClick={() => setOpenSource((cur) => (cur === s.id ? null : s.id))}
              >
                {s.id} · {s.source}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
