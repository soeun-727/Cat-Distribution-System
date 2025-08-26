// /static/js/search.js
(function () {
    const historyList = document.getElementById("historyList");
    const searchForm = document.getElementById("searchForm");
    const searchInput = document.getElementById("searchInput");

    function addHistoryItem(term) {
        if (!historyList) return;
        const li = document.createElement("li");
        li.textContent = term;
        historyList.prepend(li);
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    const sessionid = getCookie("sessionid");

    const socket = io(`${window.location.protocol}//${window.location.hostname}:727`);

    socket.on("connect", () => {
        console.log("Socket.IO connected");
        socket.emit("READY", { sessionid: sessionid }); 
    });

    socket.on("search_history", data => {
    if (!historyList) return;
    if (data.reset) historyList.innerHTML = ""; // 새로고침 시 초기화
    if (data.search_term) addHistoryItem(data.search_term);
});


    socket.on("system", data => console.log(data.msg));
    socket.on("error", data => console.error("Socket.IO error:", data.error));

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
