#"C:\SISS\HC\Cat-Distribution-System\app.py"

from flask import Flask, request, render_template, make_response, redirect, url_for
from markupsafe import escape
from flask_socketio import SocketIO, send
from flask_sqlalchemy import SQLAlchemy
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
#    'admin': FLAG
#}

class Search(db.Model):
    __tablename__ = 'Search'
    id = db.Column(db.Integer, primary_key=True)
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

    # 사용자 존재 여부 및 비밀번호 확인
    if username not in users:
        # 입력값은 escape로 무조건 이스케이프
        return render_template('login.html', error="User not found", last_user=escape(username))
    
    if users[username] != password:
        return render_template('login.html', error="Wrong password", last_user=escape(username))

    # 세션 쿠키 설정
    session_id = os.urandom(8).hex()
    session_storage[session_id] = username
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('sessionid', session_id, httponly=True, samesite='Strict')
    return resp

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()

    if query:
        db.session.add(Search(search_term=query))
        db.session.commit()

    filtered_results = Search.query.filter(Search.search_term.ilike(f'%{query}%')).order_by(Search.id.desc()).all() if query else []
    history = Search.query.order_by(Search.id.desc()).all()

    return render_template('search.html', results=filtered_results, history=history, search_term=query)

@socketio.on('message')
def handle_message(msg):
    if msg == "READY":
        history = Search.query.order_by(Search.id.desc()).all()
        for entry in history:
            send(entry.search_term)
    else:
        print(f"Received: {msg}")

@app.route('/<cat_name>.html')
def cat_profile(cat_name):
    return f"This is the profile page for {cat_name.capitalize()}!" 

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True)
