# PC가 꺼져 있어도 도는 자동화 설정

목표:

```text
Codex 공식 자동화
→ 매일 오전 8시 뉴스 조사/요약
→ 카드뉴스 이미지 생성
→ GitHub Pages에 업로드
→ GitHub Actions가 Kakao 나에게 보내기 전송
```

## 사용자가 해야 하는 일

### 1. Codex 자동화 변경 승인

Codex 앱에 표시된 `전날 AI 뉴스 만화 카드뉴스 요약` 자동화 수정 제안을 승인합니다.

핵심 변경:

- 실행 환경: `local` → `worktree`
- 시간: 매일 오전 8시
- 방식: Codex 공식 자동화 기능 사용
- 금지: ChatGPT/Plus 웹 화면 자동 조작, 비공식 GPT 자동 호출

### 2. GitHub Secrets 등록

GitHub 저장소에서 아래 메뉴로 이동합니다.

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

아래 3개를 등록합니다.

```text
KAKAO_REST_API_KEY
KAKAO_CLIENT_SECRET
KAKAO_REFRESH_TOKEN
```

값 위치:

- `KAKAO_REST_API_KEY`: Kakao Developers 앱의 REST API 키
- `KAKAO_CLIENT_SECRET`: Kakao Developers 카카오 로그인용 Client Secret
- `KAKAO_REFRESH_TOKEN`: 로컬 `config/kakao_token.json` 안의 `refresh_token`

절대 이 값들을 README, 채팅, GitHub 일반 파일에 붙여 넣지 않습니다.

### 3. 자동 흐름

Codex 자동화가 카드뉴스를 `docs/cardnews/YYYY-MM-DD/`에 올리고 main 브랜치에 푸시하면, GitHub Actions가 자동으로 실행됩니다.

Actions는 최신 카드뉴스 폴더를 찾아 아래 링크를 Kakao로 보냅니다.

```text
https://nark0-urban.github.io/ai-news-aria/cardnews/YYYY-MM-DD/
```

## 약관 리스크 기준

이 구조는 ChatGPT 웹사이트를 봇처럼 자동 조작하지 않습니다. Codex 앱의 공식 자동화 기능, GitHub Actions, Kakao REST API를 사용합니다.

다만 모든 서비스 약관 리스크가 0이라고 보장할 수는 없습니다. 안정성을 위해 다음은 하지 않습니다.

- ChatGPT Plus 자동 로그인
- ChatGPT 웹 UI 자동 입력/출력 수집
- Codex 사용량을 API처럼 우회 사용
- OpenAI 사용량 제한 우회
- 비밀키를 저장소 파일에 커밋
