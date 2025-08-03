# Cat-Distribution-System
To adopt kitties ₍^. .^₎⟆

## 페이지 구성
- home 페이지에서 입양할 고양이 확인 가능(고양이 클릭하면 세부정보 알 수 있음)
- 우상단에 Login 클릭 시 로그인 페이지로 연결
- Search 기능이 있음 (취약점 있는 부분)
- 전체 Search History를 반환하는 기능 구현

## 문제 풀이 시나리오
### 1. HTTP history를 통해 WebSocket 확인
- 페이지를 새로고침하면 WebSocket 연결이 자동으로 생성
- 클라이언트가 "READY" 메시지를 서버에 전송
- 서버는 전체 검색 기록으로 응답
### 2. CSWSH 페이로드
- WebSocket 주소 확인하고 스크립트로 연결 시도
- WebSocket 연결 후 "READY"를 보내고 서버 응답을 fetch()로 공격자 서버로 전송
- 공격자가 응답을 받을 수 있도록 no-cors 모드로 POST 요청
- 이 시점에서는 세션 쿠키가 없어 응답이 오지 않
### 3. 세션 쿠키의 Same Site attribute가 Strict여서 공격 안되는 것 확인 
- 개발자 도구 > Application 탭 > 쿠키를 통해 확인 가능
- 다른 도메인에서 요청 시 세션 쿠키가 브라우저에 전송되지 않음 
### 4. 취약점이 있는 sibling domain 확인
- Access-Control-Allow-Origin 을 통해 sibling domain 있는 것 확인 
- username 파라미터가 응답에 반영되는 reflected XSS
- GET 기반 XSS로 스크립트 전송 가능
### 5. sibling domain을 통해 SameSite restriction 우회
- 기존 CSWSH 스크립트를 URL 인코딩하여 username 파라미터에 삽입
- XSS가 실행되면 같은 사이트의 WebSocket 연결이므로 세션 쿠키 포함됨
- WebSocket 연결 → "READY" 전송 → 전체 히스토리 응답 → 공격자 서버로 유출
### 6. 전송된 메시지 분석해서 admin 정보 획득
- 로그인 하면 성공
### 12. admin으로 로그인하면 성공
