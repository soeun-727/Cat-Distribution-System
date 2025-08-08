#"C:\SISS\HC\Cat-Distribution-System\app.py"

from flask import Flask, request, render_template, make_response, redirect, url_for
from markupsafe import escape
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
from flask import session
import urllib
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)
socketio = SocketIO(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'cds.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

session_storage = {}

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

users = {
    'guest': 'guest',
    'admin': 'temp'
}

class Search(db.Model):
    __tablename__ = 'Search'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=True)
    search_term = db.Column(db.String(100), nullable=False)

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

    # 세션 쿠키 설정 (로그인 성공 시)
    session_id = os.urandom(8).hex()
    session_storage[session_id] = username
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie(
        'sessionid',
        session_id,
        httponly=True,
        samesite='Strict',  # CTF 기본 보안 설정
        secure=False        # HTTPS면 True
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

attack_success_sessions = set()

@socketio.on('message')
def handle_message(msg):
    session_id = request.cookies.get('sessionid')
    username = session_storage.get(session_id)

    if msg == "READY":
        if session_id in attack_success_sessions:
            # 익스플로잇 성공 세션은 전체 기록 반환
            history = Search.query.order_by(Search.id.desc()).all()
        else:
            # 로그인한 사용자는 자기 기록만, 로그인 안 한 사용자는 username이 None인 기록 반환
            if username:
                history = Search.query.filter_by(username=username).order_by(Search.id.desc()).all()
            else:
                history = Search.query.filter_by(username=None).order_by(Search.id.desc()).all()

        for entry in history:
            send(entry.search_term)

    elif msg == "EXPLOIT_TRIGGER":
        if session_id:
            attack_success_sessions.add(session_id)
            print(f"Attack success session: {session_id}")

    else:
        print(f"Received unknown message: {msg}")


@app.route('/<cat_name>.html')
def cat_profile(cat_name):
    return f"This is the profile page for {cat_name.capitalize()}!" 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
