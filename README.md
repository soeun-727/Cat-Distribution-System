# Cat-Distribution-System
To adopt kitties ^..^

## 페이지 구성
- home 페이지에서 입양할 고양이 확인 가능(고양이 클릭하면 세부정보 알 수 있음)
- 우상단에 Login 클릭 시 로그인 페이지로 연결
- Search 기능이 있음 (취약점 있는 부분)
- 전체 Search History를 반환하는 기능 구현

## 문제 풀이 시나리오 정리
### 1. WebSocket handshake 찾기
### 2. READY 메시지 수신 시 서버가 전체 Search history로 응답하는 거 확인
### 3. 웹소켓 exploit하려고 하면 same site restriction 땜에 안됨
### 4. sibling domain 허용하는 거 찾기
### 5. sibling domain에 접속해서 취약점 찾기
### 6. XSS 있어서 우회 가능
### 7. SameSite restriction 우회하여 서버가 전체 기록 반환하도록 (url 인코딩 쓰도록)
### 8. 전송된 메시지 분석해서 admin 정보 획득
