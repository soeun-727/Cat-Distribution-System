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
#}
# app.py

from flask import Flask, request, render_template, make_response, redirect, url_for
from markupsafe import escape
from flask_sqlalchemy import SQLAlchemy
import os
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'cds.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

socketio = SocketIO(app, cors_allowed_origins="*")

session_storage = {}
users = {
    'guest': 'guest',
    'admin': 'temp'
}

class Search(db.Model):
    __tablename__ = 'Search'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=True)
    search_term = db.Column(db.String(100), nullable=False)

# ---------------- Routes ---------------- #

@app.before_request
def assign_session():
    """방문 시 로그인 여부와 상관없이 세션 쿠키를 부여"""
    if 'sessionid' not in request.cookies:
        session_id = os.urandom(8).hex()
        session_storage[session_id] = None  # 로그인 안 한 상태
        resp = make_response()
        resp.set_cookie(
            'sessionid',
            session_id,
            httponly=True,
            samesite='Strict',  # SameSite=Strict
            secure=False
        )
        return resp  # 요청 처리 전에 쿠키 발급

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

    cats = [
        {"name": "Cheese", "age": "18 months old", "image": "cheese.jpg"},
        {"name": "John", "age": "12 months old", "image": "john.jpg"},
        {"name": "Kitty", "age": "15 months old", "image": "kitty.jpg"},
        {"name": "Tuna", "age": "27 months old", "image": "tuna.jpg"},
    ]

    query_lower = query.lower()
    filtered_cats = [cat for cat in cats if query_lower in cat["name"].lower()] if query else cats

    history = Search.query.order_by(Search.id.desc()).all()

    return render_template(
        'search.html',
        cats=filtered_cats,
        history=history,
        search_term=query
    )

@app.route('/<cat_name>.html')
def cat_profile(cat_name):
    return f"This is the profile page for {cat_name.capitalize()}!"

@app.route('/exploit')
def exploit():
    return render_template('exploit.html')

# ---------------- Socket.IO ---------------- #

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

# ----------------------------------------------- #

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
