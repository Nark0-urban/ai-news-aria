# Offline Automation Plan

## 목표

사용자는 매일 아침 전날 핵심 AI 뉴스를 미소녀 뉴스 큐레이터 `아리아`가 설명하는 만화형 카드뉴스 이미지로 받고 싶어 한다.

중요한 추가 조건:

- 컴퓨터가 꺼져 있어도 자동으로 작업되어야 한다.
- 추가 OpenAI API 비용은 쓰지 않는다.
- 가능하면 GPT/Codex 구독 사용량 안에서 처리한다.
- 최종 결과는 카카오톡 `나와의 채팅`으로 받는다.

## 현재 자동화 상태

현재 Codex 자동화:

```text
ID: ai
이름: 전날 AI 뉴스 만화 카드뉴스 요약
상태: ACTIVE
일정: 매일 오전 8시
작업 경로: C:\Users\cabin\Desktop\Codex\AI 카드뉴스 제작
실행 환경: local
```

`local` 실행 환경은 로컬 컴퓨터의 파일과 스크립트에 의존한다. 따라서 컴퓨터가 꺼져 있으면 실행을 기대하기 어렵다.

## 핵심 제약

ChatGPT/Codex 구독은 사람이 쓰는 GPT/Codex 작업에는 적합하지만, 일반적인 서버/클라우드 자동화에서 GPT를 호출하려면 보통 OpenAI API 키가 필요하다.

따라서 “PC가 꺼져 있어도 자동 실행”과 “OpenAI API 비용 없음”을 동시에 만족하려면 다음 중 하나를 선택해야 한다.

## 선택지 A: Codex 클라우드/워크트리 자동화 중심

가장 이상적인 방향이다.

```text
Codex 자동화
→ 전날 AI 뉴스 조사
→ cards.json 생성
→ 카드뉴스 이미지 렌더링
→ 공개 URL 발행
→ Kakao 나에게 보내기
```

조건:

- Codex 자동화가 로컬이 아닌 원격/워크트리 환경에서 실행되어야 한다.
- 프로젝트 파일과 아리아 이미지가 원격 실행 환경에서도 접근 가능해야 한다.
- Kakao REST API 키와 OAuth 토큰을 안전하게 저장할 방법이 필요하다.

장점:

- GPT/Codex 구독 사용량 중심으로 갈 수 있다.
- PC가 꺼져 있어도 실행될 가능성이 가장 높다.

주의:

- 현재 자동화는 `local`이다.
- 원격 실행 환경에서 로컬 비밀 파일인 `config/config.json`, `config/kakao_token.json`을 그대로 쓸 수 없다.
- 원격 환경이 이미지 렌더링과 카카오 전송까지 처리할 수 있는지 확인해야 한다.

## 선택지 B: GitHub Actions + GitHub Pages 중심

PC가 꺼져도 확실히 돌아가는 무료 클라우드 방식이다.

```text
GitHub Actions 스케줄
→ 무료 RSS/공식 블로그 수집
→ 규칙 기반 요약 또는 미리 정한 템플릿 정리
→ 카드뉴스 PNG 렌더링
→ GitHub Pages 공개
→ Kakao 나에게 보내기
```

장점:

- PC가 꺼져 있어도 실행된다.
- GitHub public repository 기준 무료 범위로 운영하기 쉽다.
- GitHub Pages로 이미지 공개 URL을 만들 수 있다.

한계:

- GitHub Actions 안에서 GPT를 쓰려면 OpenAI API 키가 필요하다.
- OpenAI API 비용을 쓰지 않으려면 요약 품질은 규칙 기반 또는 RSS 제목/본문 추출 기반으로 제한된다.
- “아리아가 자연스럽게 설명하는 원고” 품질은 Codex/GPT가 직접 작성할 때보다 떨어질 수 있다.

## 선택지 C: 혼합 방식

현실적인 1차 운영안이다.

```text
Codex 자동화: 전날 뉴스 조사 + cards.json 초안 작성
GitHub Actions: 렌더링 + Pages 발행 + Kakao 전송
```

단, Codex 자동화가 PC 꺼짐 상태에서도 실행되는 환경이어야 완전 자동화가 된다.

만약 Codex 자동화가 로컬에서만 실행된다면, 이 방식은 PC가 켜져 있을 때만 완성된다.

## 추천 방향

1차 목표는 다음 순서가 좋다.

1. 현재 로컬 프로젝트에서 카드 렌더링과 Kakao 전송을 완성한다.
2. GitHub 저장소를 만든다.
3. 아리아 기준 이미지와 렌더링 스크립트를 GitHub에 올린다.
4. GitHub Pages로 `output/published/`를 공개한다.
5. GitHub Actions로 매일 렌더링/발행/전송을 돌린다.
6. GPT가 꼭 필요한 원고 생성 단계만 Codex 자동화가 담당할 수 있는지 확인한다.
7. Codex 자동화가 PC 꺼짐 상태에서 안정적으로 실행되지 않는다면, 뉴스 원고 생성은 완전 자동보다 반자동으로 남긴다.

## 현재 결론

“PC가 꺼져 있어도”라는 조건까지 포함하면, 순수 로컬 자동화만으로는 목표를 달성할 수 없다.

추가 비용 없이 가장 현실적인 구조는 다음 둘 중 하나다.

```text
1. Codex 원격 자동화가 가능하면:
   Codex 자동화 + GitHub Pages + Kakao API

2. Codex 원격 자동화가 어렵다면:
   GitHub Actions + GitHub Pages + Kakao API
   단, GPT 수준의 자연스러운 뉴스 원고 생성은 제한됨
```

