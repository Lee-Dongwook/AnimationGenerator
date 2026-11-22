import { useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

const supportedTypes = ['image/png', 'image/jpeg', 'image/webp']

type GenerationResult = {
  video_url: string
}

function App() {
  const [mode, setMode] = useState<'character' | 'zoom'>('character')
  const [file, setFile] = useState<File | null>(null)
  const [background, setBackground] = useState<File | null>(null)
  const [preset, setPreset] = useState('bounce')
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [videoSource, setVideoSource] = useState<'generated' | 'coverr' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [coverrQuery, setCoverrQuery] = useState('')
  const [isDownloading, setIsDownloading] = useState(false)

  async function generateVideo(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!file) {
      setError('애니메이션으로 만들 이미지를 선택해 주세요.')
      return
    }

    if (!supportedTypes.includes(file.type)) {
      setError('PNG, JPG, JPEG, WEBP 파일만 업로드할 수 있습니다.')
      return
    }

    setError(null)
    setVideoUrl(null)
    setVideoSource(null)
    setIsGenerating(true)

    try {
      const data = new FormData()
      const isCharacterMode = mode === 'character'
      data.append(isCharacterMode ? 'character' : 'file', file)

      if (isCharacterMode) {
        data.append('preset', preset)
        if (background) data.append('background', background)
      }

      const response = await fetch(
        isCharacterMode ? '/videos/character/generate' : '/videos/generate',
        {
        method: 'POST',
        body: data,
        },
      )
      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || '영상 생성에 실패했습니다.')
      }

      setVideoUrl((result as GenerationResult).video_url)
      setVideoSource('generated')
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : '영상 생성에 실패했습니다.',
      )
    } finally {
      setIsGenerating(false)
    }
  }

  async function downloadCoverrVideo(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const query = coverrQuery.trim()

    if (!query) {
      setError('찾을 영상 키워드를 입력해 주세요.')
      return
    }

    setError(null)
    setVideoUrl(null)
    setVideoSource(null)
    setIsDownloading(true)

    try {
      const data = new FormData()
      data.append('query', query)
      const response = await fetch('/videos/coverr/download', { method: 'POST', body: data })
      const result = await response.json()

      if (!response.ok) throw new Error(result.detail || 'Coverr 영상 다운로드에 실패했습니다.')
      setVideoUrl((result as GenerationResult).video_url)
      setVideoSource('coverr')
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : 'Coverr 영상 다운로드에 실패했습니다.')
    } finally {
      setIsDownloading(false)
    }
  }

  return (
    <main>
      <section className="hero">
        <p className="eyebrow">KIDS MOTION ENGINE</p>
        <h1>사진 한 장을<br />짧은 영상으로</h1>
        <p className="intro">
          투명 배경 캐릭터 PNG를 업로드하면 점프, 가벼운 흔들기, 댄스 모션의 5초 MP4를 만듭니다.
        </p>
      </section>

      <section className="generator" aria-labelledby="generator-title">
        <h2 id="generator-title">영상 만들기</h2>
        <div className="mode-switch" role="group" aria-label="영상 종류">
          <button
            className={mode === 'character' ? 'selected' : ''}
            type="button"
            onClick={() => setMode('character')}
          >캐릭터 모션</button>
          <button
            className={mode === 'zoom' ? 'selected' : ''}
            type="button"
            onClick={() => setMode('zoom')}
          >사진 줌</button>
        </div>
        <form onSubmit={generateVideo}>
          <label className="file-picker" htmlFor="image-file">
            <span>{file ? file.name : mode === 'character' ? '투명 PNG 캐릭터를 선택하세요' : '이미지를 선택하세요'}</span>
            <small>PNG · JPG · WEBP</small>
          </label>
          <input
            id="image-file"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            onChange={(event) => {
              setFile(event.target.files?.[0] ?? null)
              setError(null)
            }}
          />
          {mode === 'character' && (
            <>
              <label className="select-label" htmlFor="preset">모션</label>
              <select id="preset" value={preset} onChange={(event) => setPreset(event.target.value)}>
                <option value="bounce">점프</option>
                <option value="wave">가볍게 흔들기</option>
                <option value="sway">좌우 흔들기</option>
                <option value="dance">댄스</option>
              </select>
              <label className="file-picker" htmlFor="background-file">
                <span>{background ? background.name : '배경 이미지 선택 (선택 사항)'}</span>
                <small>없으면 단색 배경</small>
              </label>
              <input
                id="background-file"
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={(event) => setBackground(event.target.files?.[0] ?? null)}
              />
            </>
          )}
          <button type="submit" disabled={isGenerating}>
            {isGenerating ? '영상을 만드는 중…' : '5초 영상 만들기'}
          </button>
        </form>

        {error && <p className="message error" role="alert">{error}</p>}

        {videoUrl && videoSource === 'generated' && (
          <div className="result">
            <h3>영상이 준비됐어요</h3>
            <video controls src={videoUrl} />
            <a href={videoUrl} download>MP4 다운로드</a>
          </div>
        )}
      </section>

      <section className="generator" aria-labelledby="coverr-title">
        <h2 id="coverr-title">Coverr 영상 받기</h2>
        <p className="intro">키워드에 맞는 세로형 영상을 찾아 다운로드합니다.</p>
        <form onSubmit={downloadCoverrVideo}>
          <label className="select-label" htmlFor="coverr-query">영상 키워드</label>
          <input
            id="coverr-query"
            value={coverrQuery}
            onChange={(event) => setCoverrQuery(event.target.value)}
            placeholder="예: forest, ocean, city"
          />
          <button type="submit" disabled={isDownloading}>
            {isDownloading ? '영상을 받는 중…' : 'Coverr 영상 다운로드'}
          </button>
        </form>
        {error && <p className="message error" role="alert">{error}</p>}
        {videoUrl && videoSource === 'coverr' && (
          <div className="result">
            <video controls src={videoUrl} />
            <a href={videoUrl} download>MP4 다운로드</a>
            <p><a className="source-link" href="https://coverr.co" target="_blank" rel="noreferrer">Video source: Coverr</a></p>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
