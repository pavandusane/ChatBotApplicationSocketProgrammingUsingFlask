import MySQLdb
from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, join_room, leave_room
from flask_mysqldb import MySQL
import os
import time
import datetime

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = os.environ['username']
app.config['MYSQL_PASSWORD'] = os.environ['password']
app.config['MYSQL_DB'] = 'chatbot'

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password))
        account = cursor.fetchone()
        print(account)
        if account[1]==username and account[2]==password:
            #session['id'] = account['id']
            print("Session 12")
            print(account)
            print(account[1])
            msg = 'Logged in successfully !'
            return render_template('index.html')
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/index')
def home():
    return render_template("index.html")


@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],data['room'],data['message']))
    socketio.emit('receive_message', data, room=data['room'])
    msg = data['message']
    id=data['room']
    name=data['username']
    ts = time.time()
    timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    print(msg)
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT into user_data (id,name,message,time) values(%s,%s,%s,%s)",(id,name,msg,timestamp))
    mysql.connection.commit()
    cursor.close()

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


if __name__ == '__main__':
    socketio.run(app, debug=True)