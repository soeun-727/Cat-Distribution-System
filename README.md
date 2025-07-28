# Cat-Distribution-System
To adopt kitties :3

## 페이지 구성
- home 페이지에서 입양할 고양이 확인 가능(고양이 클릭하면 세부정보 알 수 있음)
- 우상단에 My Account 클릭 시 로그인 페이지로 연결
- form이 있는 페이지 하나 구상할 예정(취약점 있는 페이지)

## 시나리오 정리
### 1. WebSocket handshake 찾기
### 2. 원래chat history 보이는 페이지에서 READY 메시지 수신 시 전체 history로 응답하는 거 확인
### 3. 웹소켓 exploit하려고 하면 same site restriction 땜에 안됨
### 4. sibling Domain 허용하는 거 찾기
### 5. sibling domain에 접속해서 취약점 찾기
### 6. XSS 있어서 우회 가능
### 7. SameSite restriction 우회 (왜 url 인코딩 필요하지?)
### 8. 익스플로잇 서버에서 전송하고 (이건 어케되는 걸까)
### 9. 전송된 메시지 분석해서 admin 정보 획득
