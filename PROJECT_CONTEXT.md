# Project Context: AI News Aria

이 프로젝트는 매일 전날의 AI 관련 핵심 뉴스, 제품 업데이트, 논문/연구, 정책/규제, 개발자 커뮤니티 반응을 모아 오리지널 캐릭터 `아리아`가 설명하는 만화형 카드뉴스로 만들고, Kakao 나에게 보내기로 알림을 보내기 위한 작업 공간이다.

## 핵심 방향

- 별도 OpenAI API 과금 없이 Codex/GPT 구독 사용량 안에서 진행한다.
- ChatGPT 웹 화면을 브라우저 매크로나 비공식 자동화로 조작하지 않는다.
- 카드뉴스는 텍스트 나열이 아니라 아리아가 옆에서 설명하는 이미지형 요약으로 만든다.
- Kakao 전송은 로컬 `config/config.json`과 `config/kakao_token.json`을 사용한다.
- GitHub Pages는 카드뉴스 이미지를 볼 수 있는 공개 URL을 제공하는 용도로 사용한다.

## 자동화 원칙

- 현재 자동화는 PC가 켜져 있고 Codex가 실행 가능한 상태일 때 동작하는 로컬 자동화로 본다.
- 자동화 이름은 `전날 AI 뉴스 만화 카드뉴스 요약`이다.
- 실행 시각은 매일 오전 8시로 설정되어 있지만, 로컬 실행 환경 상태에 따라 실제 실행은 지연될 수 있다.
- 로컬 Git 명령으로 `git add`, `git commit`, `git push`를 직접 실행하지 않는다. 이 작업 폴더의 `.git/index.lock` 생성 권한이 Codex 자동화 환경에서 차단될 수 있기 때문이다.
- GitHub 발행은 Codex GitHub 커넥터로 처리한다. 커넥터를 사용할 수 없으면 raw git으로 우회하지 말고 실패 이유를 보고한다.

## 캐릭터 설정

캐릭터 이름: 아리아

아리아는 AI 뉴스 큐레이터 역할의 오리지널 미소녀 캐릭터다. 밝고 깔끔한 톤의 애니메이션 뉴스 해설자 느낌을 유지한다.

기준 이미지:

```text
assets/character/aria_reference.png
```

디자인 규칙:

- 은발 또는 밝은 회색 계열 머리
- 별 모양 액세서리
- 뉴스 큐레이터 느낌의 단정한 재킷
- 과한 무기, 위협적인 분위기, 어두운 공포 연출은 사용하지 않는다.
- 카드 전체를 캐릭터가 차지하지 않게 하고, 내용 영역을 충분히 확보한다.

## 카드뉴스 형식

권장 규격:

```text
1080 x 1350 PNG
```

기본 구성:

```text
카드 1: 표지
카드 2-8: 주요 AI 뉴스 해설
필요 시 카드 9: 커뮤니티 반응 또는 종합 정리
```

각 카드에 들어갈 정보:

- 화면 제목
- 핵심 요약
- 중요 포인트
- 아리아 말풍선
- 출처명 및 URL

## 결과물 저장 규칙

매일 결과물은 날짜별 폴더에 저장한다.

```text
output/cardnews/YYYY-MM-DD/
docs/cardnews/YYYY-MM-DD/
```

예시:

```text
output/cardnews/2026-05-04/card_01.png
output/cardnews/2026-05-04/cards.json
docs/cardnews/2026-05-04/index.html
```

GitHub Pages용 파일은 `docs/` 아래에 둔다.

## 발행 절차

1. 뉴스 조사 및 출처 정리
2. `cards.json` 작성
3. 렌더링 스크립트로 PNG 카드뉴스 생성
4. `scripts/publish_to_pages.py`로 `docs/cardnews/YYYY-MM-DD/`에 복사
5. GitHub 커넥터로 `Nark0-urban/ai-news-aria`의 `main` 브랜치에 커밋
6. GitHub Pages URL 반영 확인
7. `scripts/send_latest_cardnews_kakao.py --date YYYY-MM-DD`로 Kakao 전송
