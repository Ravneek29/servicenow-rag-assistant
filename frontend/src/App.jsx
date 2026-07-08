import { useCallback, useEffect, useState } from 'react'
import Sidebar from './components/Sidebar.jsx'
import Chat from './components/Chat.jsx'
import { listDocuments } from './api.js'

export default function App() {
  const [documents, setDocuments] = useState([])
  const [docsError, setDocsError] = useState(null)

  const refreshDocuments = useCallback(async () => {
    try {
      const data = await listDocuments()
      setDocuments(data.documents)
      setDocsError(null)
    } catch (err) {
      setDocsError(err.message)
    }
  }, [])

  useEffect(() => {
    refreshDocuments()
  }, [refreshDocuments])

  return (
    <div className="app">
      <Sidebar
        documents={documents}
        error={docsError}
        onChanged={refreshDocuments}
      />
      <Chat hasDocuments={documents.length > 0} />
    </div>
  )
}
