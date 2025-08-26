// /static/js/search.js
(function () {
    const historyList = document.getElementById("historyList");
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");

    // 검색 기록 추가
    function addHistoryItem(term) {
        if (!historyList) return; // 페이지에 없을 수 있음
        const li = document.createElement("li");
        li.textContent = term;
        historyList.prepend(li);
    }

    // 쿠키 가져오기
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    // 세션 ID 가져오기 (없으면 중단)
    const sessionid = getCookie("sessionid");
    if (!sessionid) {
        console.error("세션 쿠키가 없습니다. 로그인 후 이용하세요.");
        return;
    }

    // Socket.IO 연결 (포트 727 고정)
    const socket = io(`${window.location.protocol}//${window.location.hostname}:727`, {
        withCredentials: true,
    });

    socket.on("connect", () => {
        console.log("Socket.IO connected");
        socket.emit("READY", { sessionid: sessionid });
    });

    socket.on("search_history", data => {
        if (data.search_term) addHistoryItem(data.search_term);
    });

    socket.on("system", data => console.log(data.msg));
    socket.on("error", data => console.error("Socket.IO error:", data.error));

    // 검색폼 이벤트 등록 (폼이 있을 때만)
    if (searchForm && searchInput) {
        searchForm.addEventListener("submit", e => {
            e.preventDefault();
            const term = searchInput.value.trim();
            if (!term) return;

            socket.emit("search", { sessionid: sessionid, q: term });
            searchInput.value = "";
        });
    }
})();
