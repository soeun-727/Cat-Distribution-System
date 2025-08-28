from flask import Flask, request, render_template, make_response
from markupsafe import Markup

app = Flask(__name__, template_folder=".")
app.secret_key = "sibling-secret-key"

@app.after_request
def add_cors_headers(response):
    if request.path.startswith("/secret"):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:777'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

users = {
    "admin": "p4sSw0Rd",
    "guest": "guest"
}

@app.route("/", methods=["GET", "POST", "OPTIONS"])
@app.route("/<path:path>", methods=["GET", "POST", "OPTIONS"])
def login(path=None):
    if request.method == "OPTIONS":
        # CORS preflight 요청은 바로 200 OK로
        resp = make_response()
        resp.headers['Access-Control-Allow-Origin'] = 'http://localhost:777'
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp

    error = ""
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
                path="/"
            )
            return resp
        else:
            error = f"Invalid login for user: {username}"

    scheme = request.scheme
    exploit_server_url = f"{scheme}://localhost:777/collect"
    safe_username = Markup(username)

    return render_template("login.html",
                           error=error,
                           exploit_server_url=exploit_server_url,
                           username=safe_username)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=727, debug=False)
