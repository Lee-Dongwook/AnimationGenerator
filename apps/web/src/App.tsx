import { useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

const supportedTypes = ['image/png', 'image/jpeg', 'image/webp']

type GenerationResult = {
  video_url: string
}

function App() {
  const [file, setFile] = useState<File | null>(null)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

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
    setIsGenerating(true)

    try {
      const data = new FormData()
      data.append('file', file)

      const response = await fetch('/videos/generate', {
        method: 'POST',
        body: data,
      })
      const result = await response.json()

      if (!response.ok) {
        throw new Error(result.detail || '영상 생성에 실패했습니다.')
      }

      setVideoUrl((result as GenerationResult).video_url)
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

  return (
    <main>
      <section className="hero">
        <p className="eyebrow">KIDS MOTION ENGINE</p>
        <h1>사진 한 장을<br />짧은 영상으로</h1>
        <p className="intro">
          이미지를 업로드하면 부드러운 줌 효과가 적용된 5초 MP4 영상을 만듭니다.
        </p>
      </section>

      <section className="generator" aria-labelledby="generator-title">
        <h2 id="generator-title">영상 만들기</h2>
        <form onSubmit={generateVideo}>
          <label className="file-picker" htmlFor="image-file">
            <span>{file ? file.name : '이미지를 선택하세요'}</span>
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
          <button type="submit" disabled={isGenerating}>
            {isGenerating ? '영상을 만드는 중…' : '5초 영상 만들기'}
          </button>
        </form>

        {error && <p className="message error" role="alert">{error}</p>}

        {videoUrl && (
          <div className="result">
            <h3>영상이 준비됐어요</h3>
            <video controls src={videoUrl} />
            <a href={videoUrl} download>MP4 다운로드</a>
          </div>
        )}
      </section>
    </main>
  )
}

export default App
