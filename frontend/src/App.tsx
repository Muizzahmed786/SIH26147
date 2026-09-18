import { useState, useRef } from 'react'
import Plot from 'react-plotly.js'
import styles from './App.module.css'

interface AnalysisData {
  waveform: { i: number[], q: number[] | null }
  spectrum: { freqs: number[], magnitudes_db: number[] }
  psd: { freqs: number[], psd_db: number[] }
  waterfall: { freqs: number[], times: number[], spectrogram_db: number[][] }
  constellation: { i: number[], q: number[] }
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [data, setData] = useState<AnalysisData | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0])
    }
  }

  const handleUpload = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setData(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      
      // If it's an IQ file, we need metadata. For now, hardcode it for the QPSK test
      if (file.name.endsWith('.iq')) {
        formData.append('metadata', JSON.stringify({
          sample_rate: 1000000,
          dtype: 'complex64'
        }))
      }

      // Upload file
      const uploadRes = await fetch('http://localhost:8000/api/v1/files', {
        method: 'POST',
        body: formData
      })
      if (!uploadRes.ok) throw new Error('Upload failed')
      const uploadData = await uploadRes.json()
      const recordId = uploadData.record.id

      // Start analysis
      const startRes = await fetch('http://localhost:8000/api/v1/analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ record_id: recordId })
      })
      if (!startRes.ok) throw new Error('Analysis start failed')

      // Poll for results
      let completed = false
      let analysisData = null
      while (!completed) {
        await new Promise(r => setTimeout(r, 1000)) // wait 1s
        const pollRes = await fetch(`http://localhost:8000/api/v1/analysis/${recordId}`)
        if (!pollRes.ok) throw new Error('Polling failed')
        const pollData = await pollRes.json()
        if (pollData.status === 'completed') {
          completed = true
          analysisData = pollData.results
        }
      }

      setData(analysisData)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <h1>SIH26147 Signal Analyst</h1>
      </header>

      <section className={styles.uploadSection}>
        <input type="file" onChange={handleFileChange} accept=".wav,.iq" />
        <button className={styles.button} onClick={handleUpload} disabled={!file || loading} style={{ marginLeft: '1rem' }}>
          {loading ? 'Processing...' : 'Analyze'}
        </button>
        {error && <p style={{ color: '#ef4444' }}>{error}</p>}
      </section>

      {data && (
        <div className={styles.grid}>
          <div className={styles.card}>
            <h3>Waveform (I/Q)</h3>
            <div className={styles.chartContainer}>
              <Plot
                data={[
                  { x: Array.from({length: data.waveform.i.length}, (_, i) => i), y: data.waveform.i, type: 'scatter', mode: 'lines', name: 'I', line: { color: '#38bdf8' } },
                  ...(data.waveform.q ? [{ x: Array.from({length: data.waveform.q.length}, (_, i) => i), y: data.waveform.q, type: 'scatter' as const, mode: 'lines' as const, name: 'Q', line: { color: '#f43f5e' } }] : [])
                ]}
                layout={{ autosize: true, margin: { l: 40, r: 20, t: 20, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#94a3b8' } }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          <div className={styles.card}>
            <h3>Spectrum (FFT)</h3>
            <div className={styles.chartContainer}>
              <Plot
                data={[{ x: data.spectrum.freqs, y: data.spectrum.magnitudes_db, type: 'scatter', mode: 'lines', line: { color: '#a855f7' } }]}
                layout={{ autosize: true, margin: { l: 40, r: 20, t: 20, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#94a3b8' } }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          <div className={styles.card}>
            <h3>Waterfall / Spectrogram</h3>
            <div className={styles.chartContainer}>
              <Plot
                data={[{ x: data.waterfall.freqs, y: data.waterfall.times, z: data.waterfall.spectrogram_db, type: 'heatmap', colorscale: 'Viridis' }]}
                layout={{ autosize: true, margin: { l: 40, r: 20, t: 20, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#94a3b8' } }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>

          <div className={styles.card}>
            <h3>Constellation</h3>
            <div className={styles.chartContainer}>
              <Plot
                data={[{ x: data.constellation.i, y: data.constellation.q, type: 'scatter', mode: 'markers', marker: { size: 3, color: '#10b981', opacity: 0.6 } }]}
                layout={{ autosize: true, margin: { l: 40, r: 20, t: 20, b: 40 }, paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', font: { color: '#94a3b8' }, xaxis: { range: [-1.5, 1.5] }, yaxis: { range: [-1.5, 1.5], scaleanchor: 'x' } }}
                useResizeHandler={true}
                style={{ width: '100%', height: '100%' }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default App
