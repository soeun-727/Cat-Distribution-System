from flask import Flask, request, make_response, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sibling-secret-key'

# 임시 사용자
users = {
    'admin': '1P4sSW0rD',
    'guest': 'guest'
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    username = request.values.get('username', '')  # GET/POST 모두 처리
    password = request.values.get('password', '')

    if username and (username not in users or users[username] != password):
        # XSS 발생 (escape 없음)
        error = f"Invalid login for user: {username}"

    if username in users and users[username] == password:
        resp = make_response(f"Welcome, {username}!")
        # 세션 쿠키 발급 (SameSite=Strict)
        resp.set_cookie(
            'session', 
            f'{username}-session-value',
            httponly=True,
            samesite='Strict'
        )
        return resp

    html = f"""
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>Login (Sibling Domain)</h1>
        <form method="POST" action="/login">
            Username: <input name="username" value="{username}"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        <p style="color:red;">{error}</p>
    </body>
    </html>
    """
    response = make_response(html)
    # sibling domain → 원래 도메인간 접근 테스트용 (실제 도메인 값 넣기)
    response.headers['Access-Control-Allow-Origin'] = 'https://vulnerable-YOUR-LAB-ID.web-security-academy.net'
    return response

if __name__ == '__main__':
    app.run(port=5001, debug=True)
