# AnimationGenerator

이미지 한 장으로 짧은 줌 애니메이션 MP4를 만드는 로컬 웹 애플리케이션입니다.

## 현재 MVP

- 투명 PNG 캐릭터의 점프, 가벼운 흔들기, 좌우 흔들기, 댄스 모션 생성
- 선택한 배경 이미지 또는 단색 배경 합성
- PNG, JPG, JPEG, WEBP 사진의 5초(24fps) 줌 애니메이션 생성
- 생성한 MP4 브라우저 재생 및 다운로드

## 실행하기

터미널을 두 개 열어 각각 실행합니다.

```bash
# 터미널 1: 백엔드
source .venv/bin/activate
uvicorn backend.main:app --reload
```

```bash
# 터미널 2: 웹 앱
cd apps/web
pnpm dev
```

브라우저에서 Vite가 표시한 주소(보통 `http://localhost:5173`)를 엽니다.
백엔드 API 문서는 `http://127.0.0.1:8000/docs`에서 확인할 수 있습니다.

## 테스트

```bash
source .venv/bin/activate
python -m pytest -q
```

영상 생성에는 시스템에 FFmpeg가 설치되어 있어야 합니다. 설치 여부는 `ffmpeg -version`으로 확인합니다.

## 다음 확장 후보

- 캐릭터 이미지와 배경 이미지를 따로 업로드하는 모션 프리셋 화면
- 생성 길이와 줌 강도 선택
- 생성 작업을 비동기로 처리하고 진행 상태 표시
