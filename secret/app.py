#secret/app.py
from flask import Flask, request, render_template, make_response
from markupsafe import Markup

app = Flask(__name__, template_folder=".")
app.secret_key = "sibling-secret-key"

users = {
    "admin": "p4sSw0Rd",
    "guest": "guest"
}

@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    # POST일 때는 form에서, GET일 때는 query string에서 username 받음
    username = request.form.get("username", "") if request.method == "POST" else request.args.get("username", "")
    password = request.form.get("password", "") if request.method == "POST" else ""

    if username:
        if username in users and users[username] == password:
            resp = make_response(f"Welcome {username}!")
            resp.set_cookie(
            "session",
            f"{username}-session-value",
            httponly=True,
            samesite="Strict",
        )

            return resp
        else:
            error = f"Invalid login for user: {username}"

    # 현재 요청 호스트/포트 기준으로 exploit 서버 URL 동적 생성
    scheme = request.scheme
    host = request.host.split(':')[0]  # 호스트만
    exploit_server_url = f"{scheme}://localhost:888/collect"

    # username을 HTML에서 스크립트 실행 가능하도록 safe 처리
    safe_username = Markup(username)

    return render_template("login.html",
                           error=error,
                           exploit_server_url=exploit_server_url,
                           username=safe_username)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=777, debug=False)
