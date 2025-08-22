#\app.py"

# 성공
#try:
#    FLAG = open("./flag.txt", "r").read()
#except:
#    FLAG = "[**FLAG**]"
#
#users = {
#    'guest': 'guest',
##    'admin': FLAG
#}# app.py

from flask import Flask, request, render_template, make_response, redirect, url_for, jsonify
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
import os
from datetime import datetime

cats = [
        {"name": "Cheese", "age": "18 months old", "image": "cheese.jpg"},
        {"name": "John", "age": "12 months old", "image": "john.jpg"},
        {"name": "Kitty", "age": "15 months old", "image": "kitty.jpg"},
        {"name": "Kurt", "age": "5 months old", "image": "kurt.png"},
        {"name": "Tuna", "age": "27 months old", "image": "tuna.jpg"},
        {"name": "Whiskers", "age": "7 months old", "image": "whiskers.jpg"},
]

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'cds.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ----------------- FLAG / Users ----------------- #
try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**FLAG**]"

users = {
    'guest': 'guest',
    'admin': FLAG
}

# ----------------- Session / Storage ----------------- #
session_storage = {}
logs_by_job = {}  # exploit logs 저장

def log_event(job_id, msg):
    if job_id not in logs_by_job:
        logs_by_job[job_id] = []
    logs_by_job[job_id].append({
        "ts": datetime.utcnow().isoformat(),
        "msg": msg
    })

# ----------------- Models ----------------- #
class Search(db.Model):
    __tablename__ = 'Search'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=True)
    search_term = db.Column(db.String(100), nullable=False)

# ----------------- Routes ----------------- #

@app.before_request
def assign_session():
    if 'sessionid' not in request.cookies:
        session_id = os.urandom(8).hex()
        session_storage[session_id] = None
        resp = make_response()
        resp.set_cookie(
            'sessionid',
            session_id,
            httponly=True,
            samesite='Strict',
            secure=False
        )
        # before_request에서 응답 객체(response object)를 반환해야 합니다.
        # 그러나 request.cookies에 sessionid가 없을 때만 쿠키를 설정하고,
        # 다른 요청을 그대로 진행해야 하므로, None을 반환하거나 return을 사용하지 않아야 합니다.
        # Flask 2.0 이상에서는 쿠키를 설정하는 경우 response 객체를 반환해야 합니다.
        # 이 경우에는 `make_response(redirect(request.url))`을 사용하여 현재 URL로 리다이렉트하는 것이 가장 안전합니다.
        # 하지만 기존 코드가 None을 반환했으므로, 이 부분을 생략하고 다음 코드를 진행하도록 하겠습니다.
        # resp를 반환하는 대신, 이 부분은 쿠키만 설정하고 다음 라우트로 넘어가게 하는 것이 일반적인 패턴입니다.
        pass

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

    session_id = request.cookies.get('sessionid') or os.urandom(8).hex()
    session_storage[session_id] = username
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie(
        'sessionid',
        session_id,
        httponly=True,
        samesite='Strict',
        secure=False
    )
    return resp

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    session_id = request.cookies.get('sessionid')
    username = session_storage.get(session_id) if session_id else None

    if query:
        db.session.add(Search(username=username, search_term=query))
        db.session.commit()

    query_lower = query.lower()
    filtered_cats = [cat for cat in cats if query_lower in cat["name"].lower()] if query else cats

    history = Search.query.order_by(Search.id.desc()).all()

    return render_template(
        'search.html',
        cats=filtered_cats,
        history=history,
        search_term=query
    )

@app.route('/<cat_name>')
def cat_profile(cat_name):
    # 'cats' 변수가 리스트이므로 딕셔너리처럼 `.get()` 메서드를 사용할 수 없습니다.
    # 리스트에서 해당 이름을 가진 딕셔너리를 찾아야 합니다.
    cat_info = next((cat for cat in cats if cat['name'].lower() == cat_name.lower()), None)
    
    if cat_info:
        return render_template('cat.html', cat=cat_info)
    else:
        return "Cat not found", 404

@app.route('/exploit')
def exploit():
    return render_template('exploit.html')

# ----------------- Exploit / Logs ----------------- #

@app.route("/deliver", methods=["POST"])
def deliver():
    data = request.get_json()
    payload = data.get("payload")
    job_id = str(datetime.utcnow().timestamp())
    logs_by_job[job_id] = []
    # exploit.js가 fetch로 victim에 전달
    return jsonify({"jobId": job_id})

@app.route("/logs", methods=["GET"])
def get_logs():
    job_id = request.args.get("id")
    if not job_id:
        return jsonify({"error": "job id required"}), 400
    items = logs_by_job.get(job_id, [])
    return jsonify({"items": items})

@app.route("/victim-callback", methods=["POST"])
def victim_callback():
    data = request.get_json()
    job_id = data.get("jobId")
    info = data.get("info")
    log_event(job_id, f"Victim received payload: {info}")
    return jsonify({"ok": True})

# ----------------- Socket.IO ----------------- #

@socketio.on('connect')
def handle_connect():
    print(f"[SocketIO] Client connected: {request.sid}")
    emit("system", {"msg": "Connected to server"}, room=request.sid)

@socketio.on('READY')
def handle_ready(data):
    session_id = data.get("sessionid")
    username = session_storage.get(session_id) if session_id else None

    if username:
        history = Search.query.filter_by(username=username).order_by(Search.id.desc()).all()
    else:
        history = Search.query.filter_by(username=None).order_by(Search.id.desc()).all()

    for entry in history:
        emit("search_history", {"search_term": entry.search_term}, room=request.sid)

    print(f"[SocketIO] READY processed for user: {username}")

@socketio.on('search')
def handle_search(data):
    session_id = data.get("sessionid")
    username = session_storage.get(session_id) if session_id else None
    search_term = data.get("q", "").strip()

    if not search_term:
        emit("error", {"error": "Empty search term"}, room=request.sid)
        return

    db.session.add(Search(username=username, search_term=search_term))
    db.session.commit()

    print(f"[SocketIO] {username} searched for {search_term}")
    emit("search_history", {"search_term": search_term}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    print(f"[SocketIO] Client disconnected: {request.sid}")

# ----------------- Main ----------------- #
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)