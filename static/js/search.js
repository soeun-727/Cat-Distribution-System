//static/js/search.js
(function () {
    const historyList = document.getElementById("historyList");
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");

    function addHistoryItem(term) {
        const li = document.createElement("li");
        li.textContent = term;
        historyList.prepend(li);
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    // Socket.IO 연결
    const socket = io(`${window.location.protocol}//${window.location.hostname}:727`);

    socket.on("connect", () => {
        console.log("Socket.IO connected");
        socket.emit("READY", { sessionid: getCookie("sessionid") });
    });

    socket.on("search_history", data => {
        if (data.search_term) addHistoryItem(data.search_term);
    });

    socket.on("system", data => console.log(data.msg));
    socket.on("error", data => console.error("Socket.IO error:", data.error));

    searchForm.addEventListener("submit", e => {
        e.preventDefault();
        const term = searchInput.value.trim();
        if (!term) return;

        socket.emit("search", { sessionid: getCookie("sessionid"), q: term });
        searchInput.value = "";
    });
})();
