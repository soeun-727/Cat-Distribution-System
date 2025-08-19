// /static/js/search.js

(function () {
    const historyList = document.getElementById("historyList");
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");

    // 새로운 검색 기록 추가
    function addHistoryItem(term) {
        const li = document.createElement("li");
        li.textContent = term;
        historyList.prepend(li);
    }

    // 쿠키에서 sessionid 가져오기
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    let webSocket = null;

    function openWebSocket() {
        return new Promise(res => {
            if (webSocket) {
                res(webSocket);
                return;
            }

            // 웹소켓 연결 (Socket.IO 대신 일반 WebSocket 사용 가능)
            webSocket = new WebSocket(searchForm.getAttribute("action").replace(/^http/, "ws"));

            webSocket.onopen = function () {
                console.log("WebSocket connected");
                webSocket.send(JSON.stringify({ type: "READY", sessionid: getCookie("sessionid") }));
                res(webSocket);
            };

            webSocket.onmessage = function (evt) {
                const msg = evt.data;

                try {
                    const data = JSON.parse(msg);

                    if (data.search_term) {
                        addHistoryItem(data.search_term);
                    } else if (data.error) {
                        console.error("Error:", data.error);
                    }
                } catch (e) {
                    console.error("Invalid message:", msg);
                }
            };

            webSocket.onclose = function () {
                console.warn("WebSocket disconnected");
                webSocket = null;
            };
        });
    }

    function sendSearch(term) {
        if (!webSocket) return;
        const payload = { type: "search", sessionid: getCookie("sessionid"), q: term };
        webSocket.send(JSON.stringify(payload));
    }

    searchForm.addEventListener("submit", function (e) {
        e.preventDefault();
        const term = searchInput.value.trim();
        if (!term) return;

        openWebSocket().then(() => sendSearch(term));
        searchInput.value = ""; // 입력창 초기화
    });

    // 페이지 로드 시 웹소켓 연결
    openWebSocket();
})();
