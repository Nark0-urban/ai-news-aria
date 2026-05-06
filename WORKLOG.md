# Worklog

## 2026-05-01

- 프로젝트 골격 구성: `assets/`, `config/`, `output/`, `scripts/`, `work/`
- Kakao OAuth 및 나에게 보내기용 로컬 스크립트 초안 구성
- 카드뉴스 렌더링 스크립트와 샘플 카드뉴스 생성 확인
- GitHub Pages를 공개 URL 호스팅 방식으로 사용하기로 결정

## 2026-05-03

- 오래된 실험 산출물과 불필요한 GitHub Actions 흐름 정리
- Kakao 토큰과 설정은 GitHub Secrets가 아니라 로컬 설정 파일만 사용하기로 정리
- 자동화는 PC가 켜져 있고 Codex가 실행 가능한 로컬 환경 기준으로 보기로 정리

## 2026-05-05

- `output/cardnews/2026-05-04/`에 카드뉴스 9장과 `cards.json` 생성
- `docs/cardnews/2026-05-04/`에 GitHub Pages용 파일 복사
- Kakao 전송은 성공했지만, GitHub Pages 반영 전이라 링크 404가 발생
- 원인: Codex 자동화 환경에서 `.git/index.lock` 생성 권한이 차단되어 raw git 커밋/푸시 실패

## 2026-05-06

- 자동화가 raw `git add/commit/push`를 직접 실행하지 않도록 지시문 수정
- GitHub 발행은 Codex GitHub 커넥터를 사용하도록 자동화 기준 변경
- `scripts/publish_to_pages.py`의 깨진 한글과 날짜별 HTML 제목 오류 수정
- `PROJECT_CONTEXT.md`를 UTF-8 한글 기준으로 재작성
