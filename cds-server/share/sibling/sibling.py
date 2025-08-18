from flask import Flask, request, render_template_string, make_response, redirect, url_for

app = Flask(__name__)
app.secret_key = 'sibling-secret-key'  # 실제로는 안전하게 관리하세요

# 사용자 저장 (임시)
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
    # POST 뿐 아니라 GET 요청도 처리 (GET 방식 공격 허용)
    username = request.values.get('username', '')  # GET, POST 둘 다 처리
    password = request.values.get('password', '')

    if username and (username not in users or users[username] != password):
        # reflected XSS 취약점 intentionally 유지 (이스케이프 없음)
        error = f"Invalid login for user: {username}"

    if username in users and users[username] == password:
        # 로그인 성공 시 환영 메시지
        resp = make_response(f"Welcome, {username}!")
        # 여기서 세션 쿠키 등 추가 가능
        return resp

    # XSS 취약점이 드러나도록 error 메시지 직접 삽입
    # 템플릿 스트링으로 직접 렌더링 (Jinja2 자동 이스케이프를 피해 XSS 구현)
    html = f"""
    <html>
    <head><title>Login</title></head>
    <body>
        <h1>Login</h1>
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
    # Access-Control-Allow-Origin 헤더 설정 (실제 sibling 도메인 주소로 변경 필요)
    response.headers['Access-Control-Allow-Origin'] = 'https://cms-YOUR-LAB-ID.web-security-academy.net'
    return response

if __name__ == '__main__':
    app.run(port=6000, debug=True)
