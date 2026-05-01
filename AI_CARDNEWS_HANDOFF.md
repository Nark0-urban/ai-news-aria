# AI Card News Aria Handoff

이 문서는 다른 Codex 세션이나 AI 에이전트가 `AI 카드뉴스 제작` 프로젝트를 열었을 때 지금까지의 대화 맥락을 빠르게 이해하고 이어서 작업할 수 있도록 만든 인계 문서입니다.

## 한 줄 요약

사용자는 매일 아침 전날 AI 관련 뉴스/정보를 모아 오리지널 미소녀 뉴스 큐레이터 `아리아`가 말풍선으로 설명하는 만화형 카드뉴스 이미지로 받고 싶어 한다. 최종 목표는 카드뉴스 이미지를 카카오톡 `나와의 채팅`으로 자동 전송하는 것이다.

## 사용자가 원하는 최종 결과

- 매일 아침 전날 AI 소식 요약
- 뉴스, 공식 블로그, 연구/논문, 정책/규제, 커뮤니티 반응 등을 참고
- 딱딱한 텍스트 요약이 아니라 이미지 카드뉴스
- 카드뉴스는 미소녀 캐릭터가 말풍선으로 설명하는 만화 형식
- 캐릭터는 오리지널 `아리아`
- 카카오톡 `나와의 채팅`으로 자동 전송
- 가능한 한 추가 비용 없이 진행
- 컴퓨터가 꺼져 있어도 자동 작업이 진행되길 원함

## 비용 관련 결정

중요: 사용자는 추가 API 비용 발생을 원하지 않는다.

따라서 1차 설계는 다음 방향이다.

- 별도 OpenAI API 키를 사용하지 않는다.
- OpenAI 이미지 생성 API를 직접 호출하지 않는다.
- Codex/GPT 자동화 사용량 또는 구독 범위 안에서 카드뉴스 생성 작업을 한다.
- Kakao 전송은 OAuth + Kakao REST API를 사용한다.
- n8n과 MCP는 1차 버전에서는 사용하지 않는다.
- 카카오톡 전송은 무료 쿼터 안에서 처리하는 방향이다.
- 카카오 메시지에 이미지를 넣으려면 공개 이미지 URL이 필요하므로, GitHub Pages 같은 무료 호스팅을 후보로 둔다.

## 현재 프로젝트 위치

목표 프로젝트 경로:

```text
C:\Users\cabin\Desktop\Codex\AI 카드뉴스 제작
```

이 폴더를 Codex 프로젝트로 열고 작업하면 된다.

## 현재 프로젝트 구조

```text
AI 카드뉴스 제작/
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
    published/
  scripts/
    cleanup_outputs.ps1
  work/
    drafts/
  README.md
  PROJECT_CONTEXT.md
  WORKLOG.md
```

## 이미 만든 자산

아리아 기준 이미지:

```text
assets/character/aria_reference.png
```

Kakao Developers 앱 이미지 원본:

```text
assets/app_icon/ai_news_aria_icon_source.png
```

Kakao Developers 업로드용 128px 이미지:

```text
assets/app_icon/ai_news_aria_kakao_128.png
```

카카오 콘솔 업로드 조건은 JPG/GIF/PNG, 권장 128px, 최대 250KB였고, `ai_news_aria_kakao_128.png`는 이 조건에 맞게 생성되었다.

## 캐릭터 설정

캐릭터 이름: 아리아

아리아는 오리지널 AI 뉴스 큐레이터 캐릭터다.

유지해야 할 특징:

- 은청색 단발
- 별 모양 헤어핀
- 밝고 똑똑한 표정
- 흰 셔츠와 네이비 재킷
- 작은 태블릿
- 밝은 미래형 뉴스룸 배경
- 말풍선으로 AI 뉴스를 설명

피해야 할 방향:

- 과한 가챠풍 장신구
- 어두운 분위기
- 무기
- 노출이 강한 의상
- 너무 복잡한 배경
- 기존 게임/애니 캐릭터를 연상시키는 복제
- Kakao/OpenAI 등 실제 회사 로고 사용

참고: 사용자가 한때 `니케 스타일`, `가챠겜 일러스트 느낌`을 원했지만 결과가 너무 과하다고 판단했고, 최종적으로는 첫 번째 깔끔한 아리아 이미지 스타일을 기준으로 하기로 했다.

## 카드뉴스 형식

권장 이미지 규격:

```text
1080 x 1350 PNG
```

기본 구성:

```text
카드 1: 표지
카드 2-6: 주요 AI 뉴스 해설
카드 7: 커뮤니티 반응 또는 개발자 관점
카드 8: 오늘 주목할 포인트
```

각 카드에 들어가야 할 요소:

- 카드 제목
- 뉴스 핵심 요약
- 아리아의 말풍선 대사
- 아리아 표정/포즈
- 보조 캡션
- 중요도
- 출처명/출처 링크

생성물 저장 규칙:

```text
output/cardnews/YYYY-MM-DD/
```

예시:

```text
output/cardnews/2026-05-01/card_01.png
output/cardnews/2026-05-01/card_02.png
output/cardnews/2026-05-01/cards.json
```

임시 작업물:

```text
work/drafts/
```

발행 또는 공개 URL 준비용 결과물:

```text
output/published/
```

오래된 결과물 정리:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_outputs.ps1 -KeepDays 30
```

먼저 삭제 대상만 보려면:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_outputs.ps1 -KeepDays 30 -DryRun
```

## 자동화 상태

Codex 자동화 이름:

```text
전날 AI 뉴스 만화 카드뉴스 요약
```

자동화 ID는 생성 결과상 `ai`로 표시되었다.

자동화 의도:

- 매일 오전 8시 실행
- 전날 AI 관련 소식 조사
- 아리아 캐릭터 기준으로 만화 카드뉴스 원고/JSON 생성
- 카카오톡 전송용 짧은 텍스트도 함께 생성
- 결과물은 `output/cardnews/YYYY-MM-DD/`에 저장

작업 디렉터리는 다음으로 업데이트했다.

```text
C:\Users\cabin\Desktop\Codex\AI 카드뉴스 제작
```

다른 세션에서 자동화가 보이지 않거나 작동 경로가 다르면 이 경로를 다시 확인해야 한다.

중요: 확인 결과 현재 자동화 실행 환경은 `local`이다. 따라서 로컬 PC가 꺼져 있으면 실행을 기대하기 어렵다. 사용자의 새 요구사항인 “PC가 꺼져 있어도 추가 비용 없이 자동 실행”을 만족하려면 `OFFLINE_AUTOMATION_PLAN.md`를 먼저 읽고, Codex 원격/워크트리 자동화 가능 여부 또는 GitHub Actions 기반 무료 클라우드 구조를 검토해야 한다.

## Kakao Developers에서 사용자가 해야 할 일

사용자는 아직 카카오 앱 설정을 진행 중인 상태다. 다음 절차를 안내하면 된다.

1. Kakao Developers 접속
   ```text
   https://developers.kakao.com/
   ```
2. 내 애플리케이션 콘솔 접속
   ```text
   https://developers.kakao.com/console/app
   ```
3. 앱 생성
   ```text
   앱 이름 예시: AI 뉴스 아리아
   ```
4. 앱 이미지 업로드
   ```text
   assets/app_icon/ai_news_aria_kakao_128.png
   ```
5. 앱 키 메뉴에서 REST API 키 확인
   - 이 키는 채팅에 그대로 붙여넣지 않도록 안내한다.
   - 나중에 `config/config.json` 같은 로컬 설정 파일에 넣게 한다.
6. 제품 설정 > 카카오 로그인에서 활성화 ON
7. Redirect URI 등록
   ```text
   http://localhost:8765/callback
   ```
8. 제품 설정 > 카카오 로그인 > 동의항목에서 `talk_message` 또는 카카오톡 메시지 전송 권한 설정

관련 공식 문서:

```text
https://developers.kakao.com/docs/latest/ko/kakaotalk-message/rest-api
https://developers.kakao.com/docs/ko/getting-started/quota
```

## 왜 OAuth를 쓰는가

OAuth는 카카오 계정 권한을 받아 `나에게 보내기` API를 호출하기 위한 인증 방식이다.

MCP나 n8n을 쓰더라도 결국 카카오톡 메시지 API를 호출하려면 OAuth 토큰이 필요하다. 그래서 1차 버전은 OAuth + Kakao REST API로 직접 진행하기로 했다.

## 왜 n8n/MCP를 당장 쓰지 않는가

n8n은 여러 서비스를 연결하는 자동화 배선판이고, MCP는 AI가 외부 도구를 호출하게 해주는 방식이다.

하지만 현재 목표는 작다.

```text
Codex 자동화
→ 카드뉴스 생성
→ 공개 URL 확보
→ Kakao OAuth로 나에게 보내기
```

따라서 1차 버전에서는 n8n/MCP를 넣지 않는 것이 단순하고 비용도 적다. 나중에 일정, 노션, 슬랙, 여러 채널 전송 등으로 확장할 때 검토한다.

## 이미지 URL 문제

카카오톡 메시지에 이미지를 넣으려면 로컬 파일 경로가 아니라 공개 URL이 필요하다.

즉 다음은 안 된다.

```text
C:\Users\...\card_01.png
```

다음 같은 형태가 필요하다.

```text
https://example.com/card_01.png
```

무료 후보는 GitHub Pages다.

향후 해야 할 일:

- GitHub 저장소 또는 Pages 경로 정하기
- 카드뉴스 이미지를 업로드
- Kakao 메시지 템플릿의 `image_url`에 공개 URL 넣기

## 다음 세션이 이어서 해야 할 작업

우선순위 순서:

1. 프로젝트 폴더를 연다.
   ```text
   C:\Users\cabin\Desktop\Codex\AI 카드뉴스 제작
   ```
2. `PROJECT_CONTEXT.md`, `WORKLOG.md`, 이 문서를 읽는다.
3. 사용자가 Kakao Developers 설정을 완료했는지 확인한다.
4. 완료했다면 다음 파일을 만든다.
   ```text
   config/config.json
   scripts/kakao_auth.py
   scripts/send_kakao.py
   ```
5. OAuth 최초 인증 흐름을 만든다.
   - 로컬 콜백 서버 `http://localhost:8765/callback`
   - authorization code 받기
   - access token / refresh token 저장
6. `나에게 보내기` 테스트 메시지를 보낸다.
7. 그다음 카드뉴스 렌더링 스크립트를 만든다.
   ```text
   scripts/render_cardnews.py
   ```
8. 샘플 카드뉴스 1장을 생성해서 `output/cardnews/YYYY-MM-DD/`에 저장한다.
9. 무료 이미지 호스팅 또는 GitHub Pages 연결을 결정한다.
10. 이미지 URL을 Kakao 메시지에 넣어 전송 테스트한다.

## 다른 세션을 위한 응답 톤

사용자는 개발/자동화 지식이 많지 않다고 했다. 따라서 설명은 다음처럼 해야 한다.

- 한 번에 너무 많은 선택지를 던지지 말 것
- 지금 해야 할 일과 나중에 할 일을 나눠서 설명할 것
- 링크와 경로를 명확히 줄 것
- 비용 발생 가능성을 항상 먼저 확인할 것
- REST API 키, 토큰 같은 민감정보는 채팅에 붙여넣지 말라고 안내할 것
- 가능한 작업은 직접 파일로 만들어줄 것

## 현재 결론

이 프로젝트는 아직 완성된 자동 전송 시스템이 아니다.

현재 완료된 것:

- 프로젝트 폴더 생성
- 캐릭터 기준 이미지 생성/저장
- 카카오 앱 아이콘 생성/저장
- 기본 문서 작성
- 결과물 관리 구조 작성
- 오래된 결과물 정리 스크립트 작성
- Codex 자동화 방향 설정

아직 남은 것:

- Kakao Developers 앱 설정 완료 확인
- OAuth 토큰 발급 스크립트
- Kakao 메시지 전송 스크립트
- 카드뉴스 이미지 렌더링 스크립트
- 공개 이미지 URL 호스팅
- 실제 카카오톡 전송 테스트
