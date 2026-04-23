import React, { useRef, useState } from 'react'

export default function UploadForm({ onReport, onError, onLoading }) {
  const fileInputRef = useRef(null)
  const [fileName, setFileName] = useState('')

  async function handleFile(file) {
    if (!file) return
    setFileName(file.name)
    onError(null)
    onLoading(true)
    const formData = new FormData()
    formData.append('file', file)
    try {
      const res = await fetch('/api/analyze', { method: 'POST', body: formData })
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}))
        throw new Error(detail.detail || `Server returned ${res.status}`)
      }
      const data = await res.json()
      onReport(data)
    } catch (e) {
      onError(e.message || 'Upload failed')
      onReport(null)
    } finally {
      onLoading(false)
    }
  }

  return (
    <div className="upload-card">
      <input
        ref={fileInputRef}
        type="file"
        accept=".xlsx,.xlsm,.csv,.tsv"
        style={{ display: 'none' }}
        onChange={(e) => handleFile(e.target.files?.[0])}
      />
      <button onClick={() => fileInputRef.current?.click()}>
        Choose Jira extract (.xlsx / .csv)
      </button>
      <a className="button-like secondary" href="/api/sample">
        Download sample file
      </a>
      {fileName && <span className="muted">Loaded: {fileName}</span>}
    </div>
  )
}
