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

    if (window._socket && window._socket.connected) {
        window._socket.disconnect();
    }

    const socket = io(`${window.location.protocol}//${window.location.hostname}:727`);
    window._socket = socket;  

    socket.once("connect", () => {
        console.log("Socket.IO connected");
        socket.emit("READY", { sessionid: sessionid }); 
    });

    socket.off("search_history"); 
    socket.on("search_history", data => {
        if (!historyList) return;
        if (data.reset) historyList.innerHTML = "";
        if (data.search_term) addHistoryItem(data.search_term);
    });

    socket.off("system");
    socket.on("system", data => console.log(data.msg));

    socket.off("error");
    socket.on("error", data => console.error("Socket.IO error:", data.error));

    if (searchForm && searchInput) {
        searchForm.addEventListener("submit", e => {
            e.preventDefault();
            const term = searchInput.value.trim();
            if (!term) return;

            socket.emit("search", { sessionid: sessionid, q: term }, () => {
                window.location.href = `/search?q=${encodeURIComponent(term)}`;
            });
        });
    }

})();
