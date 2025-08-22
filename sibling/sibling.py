from flask import Flask, request, render_template, make_response, url_for

app = Flask(__name__, template_folder=".")
app.secret_key = "sibling-secret-key"

users = {
    "admin": "1P4sSW0rD",
    "guest": "guest"
}

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    username = request.form.get("username", "") if request.method=="POST" else ""
    password = request.form.get("password", "") if request.method=="POST" else ""

    if username:
        if username in users and users[username] == password:
            resp = make_response(f"Welcome {username}!")
            resp.set_cookie("session", f"{username}-session-value", httponly=True, samesite="Strict")
            return resp
        else:
            error = f"Invalid login for user: {username}"

    # 현재 요청 호스트/포트 기준으로 exploit 서버 URL 동적 생성
    scheme = request.scheme
    host = request.host.split(':')[0]  # 호스트만
    exploit_server_url = f"{scheme}://{host}:8000/collect"

    return render_template("login.html", error=error, exploit_server_url=exploit_server_url)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

