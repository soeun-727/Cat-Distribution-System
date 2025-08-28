from flask import Flask, request, render_template, make_response, redirect, url_for, session
import secrets
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
from flask import send_from_directory, make_response
from flask import jsonify

# ----------------- Flask / DB / SocketIO ----------------- #
app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'cds.db')
app.config['SQLALCHEMY_DATABASE_URI'] += '?check_same_thread=False'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
from flask import Flask, request, send_from_directory

# ----------------- CSRF ----------------- #
def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_hex(16)
    return session["_csrf_token"]

app.jinja_env.globals["csrf_token"] = generate_csrf_token

# ----------------- Users / FLAG ----------------- #
try:
    KEY = open("./key.txt", "r").read()
except:
    KEY = "[**FLAG**]"

users = {
    'kitty': 'kitty',
    'admin': KEY
}

# ----------------- Session ----------------- #
session_storage = {}

# ----------------- DB ----------------- #
class Search(db.Model):
    __tablename__ = 'Search'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(32), nullable=False)
    search_term = db.Column(db.String(100), nullable=False)

# ----------------- Session 처리 ----------------- #
@app.before_request
def ensure_session_cookie():
    session_id = request.cookies.get('sessionid')
    if not session_id:
        session_id = os.urandom(8).hex()
        # 새 쿠키를 response 단계에서 심어줄 수 있도록 request에 저장
        request.new_session_id = session_id
    else:
        request.new_session_id = None
    request.session_id = session_id or request.new_session_id

@app.after_request
def attach_cookie(response):
    # 새 session_id가 있으면 쿠키 설정
    if getattr(request, "new_session_id", None):
        response.set_cookie(
            'sessionid',
            request.new_session_id,
            httponly=False,
            samesite='Strict',
            secure=False
        )

    # style.css와 view.js에만 Access-Control-Allow-Origin 적용
    if request.path.startswith("/secret"):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:777'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

# ----------------- Routes ----------------- #
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if username not in users:
        return render_template('login.html', error="User not found", last_user=escape(username))
    
    if users[username] != password:
        return render_template('login.html', error="Wrong password", last_user=escape(username))

    session_storage[request.session_id] = username
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('sessionid', request.session_id, httponly=False, samesite='Strict', secure=False)
    return resp

cats = [
    {"name": "Cheese", "age": "18 months old", "image": "cheese.jpg"},
    {"name": "John", "age": "12 months old", "image": "john.jpg"},
    {"name": "Kitty", "age": "15 months old", "image": "kitty.jpg"},
    {"name": "Kurt", "age": "5 months old", "image": "kurt.png"},
    {"name": "Tuna", "age": "27 months old", "image": "tuna.jpg"},
    {"name": "Whiskers", "age": "7 months old", "image": "whiskers.jpg"},
]

@app.route('/cat/<cat_name>')
def cat_profile(cat_name):
    safe_name = escape(cat_name)
    cat_info = next((cat for cat in cats if cat['name'].lower() == safe_name.lower()), None)
    if cat_info:
        return render_template('cat.html', cat=cat_info)
    return "Cat not found", 404

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    session_id = request.cookies.get("sessionid")

    if query:
        # 홈에서 이동한 검색어도 저장
        db.session.add(Search(session_id=session_id, search_term=query))
        db.session.commit()

    query_lower = query.lower()
    filtered_cats = [cat for cat in cats if query_lower in cat["name"].lower()] if query else cats
    return render_template('search.html', cats=filtered_cats, search_term=query)

# ----------------- Socket.IO ----------------- #
@socketio.on('connect')
def handle_connect():
    print(f"[SocketIO] Client connected: {request.sid}")
    emit("system", {"msg": "Connected to server"}, room=request.sid)

@socketio.on('READY')
def handle_ready(data):
    print("Handshake Cookies:", request.cookies)
    # 브라우저 쿠키에서 sessionid 자동 확인
    session_id = request.cookies.get("sessionid")

    if session_id:
        # /secret 요청처럼 쿠키가 존재하면 전체 기록 반환
        history = Search.query.filter_by(session_id=session_id).order_by(Search.id.desc()).all()
        for entry in history:
            emit("search_history", {"search_term": entry.search_term}, room=request.sid)
    else:
        # 쿠키 없는 요청(exploit 서버 등) → 새 세션만 반환
        emit("search_history", {"search_term": None}, room=request.sid)

@socketio.on('search')
def handle_search(data):
    session_id = data.get("sessionid") or request.cookies.get("sessionid")
    search_term = data.get("q", "").strip()
    if not search_term:
        emit("error", {"error": "Empty search term"}, room=request.sid)
        return

    #익스플로잇 서버에서 확인용, 오류뜨면 지우자
    print(f"[SEARCH] session_id={session_id}, term={search_term}")  
    db.session.add(Search(session_id=session_id, search_term=search_term))
    db.session.commit()
    emit("search_history", {"search_term": search_term}, room=request.sid)

    return {"ok": True} 

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[SocketIO] Client disconnected: {request.sid}")

# ----------------- Payload ----------------- #
payload_storage = {"latest": ""}
@app.route('/deliver', methods=['POST', 'OPTIONS'])
def deliver():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:777"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    payload = request.json.get("payload", "")
    payload_storage["latest"] = payload

    response = jsonify({"status": "ok"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:777"
    return response

@app.route("/get_payload")
def get_payload():
    return payload_storage.get("latest", ""), 200

@app.route('/victim')
def victim():
    return render_template('victim.html')

# ----------------- Main ----------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=727, debug=True)
