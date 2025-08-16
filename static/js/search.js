// /static/js/search.js

// Socket.IO 연결
const socket = io.connect(location.origin);

// 쿠키에서 sessionid 가져오기
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

const sessionid = getCookie("sessionid");

// 검색 기록 리스트 요소
const historyList = document.getElementById("historyList");

// 새로운 검색 기록 추가
function addHistoryItem(term) {
    const li = document.createElement("li");
    li.textContent = term;
    historyList.prepend(li); // 최신 기록 위로
}

// Socket.IO 연결 완료 시 ready 이벤트 전송
socket.on("connect", () => {
    console.log("Connected to server via Socket.IO");
    socket.emit("ready", { sessionid: sessionid });
});

// 서버에서 검색 기록 받을 때
socket.on("search_history", data => {
    if (data.search_term) addHistoryItem(data.search_term);
});

// 에러 메시지 받기
socket.on("error", data => {
    console.error("Error:", data.error);
});

// 검색 폼 처리
const searchForm = document.getElementById("searchForm");
const searchInput = document.getElementById("searchInput");

searchForm.addEventListener("submit", function (e) {
    e.preventDefault();

    const query = searchInput.value.trim();
    if (!query) return;

    // Socket.IO로 서버에 검색 이벤트 전송
    socket.emit("search", { sessionid: sessionid, q: query });

    // 서버에 전송 후 바로 입력 비우기
    searchInput.value = "";
    console.log("Socket connected?", socket.connected);

});
