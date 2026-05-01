# AI News Aria

매일 전날 AI 소식을 아리아 캐릭터가 설명하는 만화형 카드뉴스로 만들고, 카카오톡 나와의 채팅으로 보내기 위한 프로젝트입니다.

## 현재 목표

추가 OpenAI API 과금 없이 Codex/GPT 자동화 사용량 안에서 카드뉴스를 만들고, Kakao OAuth + 무료 이미지 호스팅을 통해 카카오톡으로 전송합니다.

## 폴더 구조

```text
ai-news-aria/
  assets/
    character/
      aria_reference.png
    app_icon/
      ai_news_aria_icon_source.png
      ai_news_aria_kakao_128.png
  config/
    config.example.json
  output/
    cardnews/
      YYYY-MM-DD/
        card_01.png
        card_02.png
        cards.json
    published/
  scripts/
    cleanup_outputs.ps1
  work/
    drafts/
```

## 생성물 관리 규칙

- 매일 생성되는 카드뉴스 이미지는 `output/cardnews/YYYY-MM-DD/` 아래에 저장합니다.
- 카카오톡에 보낸 뒤 공개 URL 관리가 필요한 파일은 `output/published/`에 따로 둘 수 있습니다.
- 임시 원고, 테스트 이미지, 중간 결과물은 `work/drafts/`에 둡니다.
- 오래된 날짜 폴더는 `scripts/cleanup_outputs.ps1`로 정리합니다.

## 카카오 앱 아이콘

Kakao Developers 앱 이미지 업로드용 파일:

```text
assets/app_icon/ai_news_aria_kakao_128.png
```

## 오래된 결과물 정리

예: 30일보다 오래된 카드뉴스 결과물을 미리 보기

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_outputs.ps1 -KeepDays 30 -DryRun
```

실제로 삭제

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_outputs.ps1 -KeepDays 30
```

## 로컬 설정 만들기

Kakao REST API 키와 OAuth 토큰은 채팅이나 문서에 붙여넣지 말고, 로컬 설정 파일에만 저장합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\init_config.ps1
```

생성된 `config/config.json`에서 `YOUR_KAKAO_REST_API_KEY`만 Kakao Developers의 REST API 키로 바꿉니다.

## 카드뉴스 샘플 렌더링

현재 렌더러는 추가 OpenAI API 비용 없이 `cards.json`과 기존 아리아 이미지를 조합해 PNG를 만듭니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\render_cardnews.ps1 -Sample
```

결과는 `output/cardnews/YYYY-MM-DD/` 아래에 생성됩니다.

## Kakao OAuth와 전송

Kakao Developers 설정을 마친 뒤 최초 1회 토큰을 발급합니다.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\kakao_auth.ps1
```

브라우저로 표시된 URL을 열어 동의하면 `config/kakao_token.json`이 생성됩니다.

텍스트 메시지 테스트:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\send_kakao.ps1 -Text "아리아 카드뉴스 테스트입니다."
```

## 다음 단계

1. Kakao Developers 앱 설정
2. Kakao OAuth 토큰 발급 스크립트 추가
3. 카드뉴스 렌더링 스크립트 추가
4. 무료 이미지 호스팅 또는 GitHub Pages 연결
5. 카카오톡 나에게 보내기 테스트
