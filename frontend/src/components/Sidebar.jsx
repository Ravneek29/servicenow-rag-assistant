import { useRef, useState } from 'react'
import { deleteDocument, loadSamples, uploadDocument } from '../api.js'

export default function Sidebar({ documents, error, onChanged }) {
  const inputRef = useRef(null)
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState(null)
  const [dragOver, setDragOver] = useState(false)

  const handleFiles = async (files) => {
    if (!files?.length) return
    setBusy(true)
    for (const file of files) {
      setStatus(`Indexing ${file.name}…`)
      try {
        const res = await uploadDocument(file)
        setStatus(
          res.warning
            ? `⚠ Indexed ${res.name} (${res.chunks} chunks) — ${res.warning}`
            : `Indexed ${res.name} (${res.chunks} chunks)`,
        )
      } catch (err) {
        setStatus(`Failed: ${err.message}`)
      }
    }
    setBusy(false)
    onChanged()
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    handleFiles([...e.dataTransfer.files])
  }

  const handleLoadSamples = async () => {
    setBusy(true)
    setStatus('Loading sample ServiceNow docs…')
    try {
      const res = await loadSamples()
      setStatus(`Loaded ${res.documents.length} sample docs`)
    } catch (err) {
      setStatus(`Failed: ${err.message}`)
    }
    setBusy(false)
    onChanged()
  }

  const handleDelete = async (name) => {
    try {
      await deleteDocument(name)
      onChanged()
    } catch (err) {
      setStatus(`Failed: ${err.message}`)
    }
  }

  return (
    <aside className="sidebar">
      <header className="sidebar-header">
        <h1>ServiceNow<br />Knowledge Assistant</h1>
        <p className="tagline">RAG · LangChain · ChromaDB · Claude</p>
      </header>

      <div
        className={`dropzone ${dragOver ? 'dropzone--active' : ''}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <span className="dropzone-icon">⇪</span>
        <span>Drop documentation here<br />or click to browse</span>
        <span className="dropzone-hint">PDF · Markdown · HTML · TXT</span>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.md,.txt,.html,.htm"
          hidden
          onChange={(e) => { handleFiles([...e.target.files]); e.target.value = '' }}
        />
      </div>

      <button className="btn-secondary" onClick={handleLoadSamples} disabled={busy}>
        Load sample ServiceNow docs
      </button>

      {status && <p className="status">{status}</p>}
      {error && <p className="status status--error">API error: {error}</p>}

      <h2 className="doc-list-title">Knowledge base ({documents.length})</h2>
      <ul className="doc-list">
        {documents.map((doc) => (
          <li key={doc.name} className="doc-item">
            <div className="doc-meta">
              <span className="doc-name" title={doc.name}>{doc.name}</span>
              <span className="doc-chunks">{doc.chunks} chunks</span>
            </div>
            <button
              className="doc-delete"
              title={`Remove ${doc.name}`}
              onClick={() => handleDelete(doc.name)}
            >
              ✕
            </button>
          </li>
        ))}
        {documents.length === 0 && (
          <li className="doc-empty">No documents indexed yet</li>
        )}
      </ul>
    </aside>
  )
}
