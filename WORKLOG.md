# Worklog

## 2026-05-01

### 결정한 방향

- 매일 전날 AI 뉴스를 카드뉴스로 정리한다.
- 카드뉴스는 텍스트 카드가 아니라 오리지널 캐릭터 `아리아`가 말풍선으로 설명하는 만화형 이미지로 만든다.
- 카카오톡 전송은 1차 버전에서 MCP/n8n 없이 Kakao OAuth + REST API로 진행한다.
- 추가 OpenAI API 비용을 피하기 위해 별도 `OPENAI_API_KEY` 기반 이미지 생성 API 호출은 사용하지 않는 방향으로 잡았다.
- 카카오톡 이미지 전송을 위해 생성 이미지에는 공개 URL이 필요하므로 GitHub Pages 같은 무료 호스팅을 후보로 둔다.

### 생성한 자산

- 아리아 기준 캐릭터 이미지
  - `assets/character/aria_reference.png`
- Kakao Developers 앱 이미지용 아이콘 원본
  - `assets/app_icon/ai_news_aria_icon_source.png`
- Kakao Developers 업로드용 128px 아이콘
  - `assets/app_icon/ai_news_aria_kakao_128.png`

### 만든 프로젝트 구조

```text
assets/
config/
output/cardnews/
output/published/
scripts/
work/drafts/
```

### 추가한 문서/설정

- `README.md`
- `PROJECT_CONTEXT.md`
- `WORKLOG.md`
- `config/config.example.json`
- `.gitignore`
- `scripts/cleanup_outputs.ps1`

### 자동화

Codex 자동화 `전날 AI 뉴스 만화 카드뉴스 요약`을 생성/수정했다.

현재 자동화는 아리아 기준 이미지를 참고해 매일 오전 8시에 전날 AI 뉴스를 만화 카드뉴스 원고/JSON 형태로 만들도록 설정되어 있다.

프로젝트 이동 후 자동화의 작업 경로를 새 프로젝트 폴더로 변경해야 한다.

### 사용자가 해야 할 외부 설정

Kakao Developers:

1. 앱 생성
2. 앱 이미지 업로드
3. 카카오 로그인 활성화
4. Redirect URI 등록
   ```text
   http://localhost:8765/callback
   ```
5. `talk_message` 동의항목 설정

GitHub:

- 무료 이미지 공개 URL을 만들기 위해 GitHub 계정 또는 GitHub Pages 사용 여부를 결정한다.

### 이어서 구현한 스크립트

- `scripts/init_config.ps1`
  - `config/config.example.json`을 `config/config.json`으로 복사한다.
  - `config/config.json`은 `.gitignore`에 포함되어 있어 민감정보 저장용으로 쓴다.
- `scripts/kakao_auth.ps1`
  - Kakao OAuth authorization code 흐름을 로컬 콜백 `http://localhost:8765/callback`으로 처리한다.
  - access token / refresh token을 `config/kakao_token.json`에 저장한다.
- `scripts/send_kakao.ps1`
  - Kakao `나에게 보내기` REST API 호출용 스크립트다.
  - 이미지 URL이 없으면 텍스트 템플릿, 이미지 URL이 있으면 피드 템플릿으로 전송한다.
- `scripts/render_cardnews.ps1`
  - 추가 OpenAI API 호출 없이 기존 아리아 이미지와 `cards.json`을 조합해 PNG 카드뉴스를 렌더링한다.
  - `-Sample` 옵션으로 샘플 카드뉴스를 바로 생성할 수 있다.

### 확인한 자동화

- 자동화 ID: `ai`
- 이름: `전날 AI 뉴스 만화 카드뉴스 요약`
- 상태: `ACTIVE`
- 일정: 매일 오전 8시
- 작업 경로: `C:\Users\cabin\Desktop\Codex\AI 카드뉴스 제작`

### 검증

- `powershell -ExecutionPolicy Bypass -File .\scripts\render_cardnews.ps1 -Sample` 실행 성공
- 샘플 PNG가 `output/cardnews/2026-05-01/` 아래에 생성됨
