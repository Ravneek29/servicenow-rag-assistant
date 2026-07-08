// In local dev this is empty (Vite proxies /api to the backend); in a
// deployed frontend set VITE_API_URL to the backend's public URL.
const API_BASE = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '')

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options)
  if (!res.ok) {
    let detail = res.statusText
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch { /* non-JSON error body */ }
    throw new Error(detail)
  }
  return res.json()
}

export const listDocuments = () => request('/api/documents')

export const uploadDocument = (file) => {
  const form = new FormData()
  form.append('file', file)
  return request('/api/documents', { method: 'POST', body: form })
}

export const deleteDocument = (name) =>
  request(`/api/documents/${encodeURIComponent(name)}`, { method: 'DELETE' })

export const loadSamples = () =>
  request('/api/documents/load-samples', { method: 'POST' })

export const askQuestion = (question) =>
  request('/api/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
