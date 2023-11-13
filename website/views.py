from flask import Flask, Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import sqlite3

def account_exists(email, username):
    conn = sqlite3.connect('website/database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone():
        conn.close()
        return True

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        conn.close()
        return True

    conn.close()
    return False

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
def home():
    return render_template('home.html')

@views.route("/login", methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('views.logout'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form

        if (not username) and (not password):
            flash('Please provide account information.', category='error')
        elif not username:
            flash('Please provide a username.', category='error')
        elif not password:
            flash('Please provide a password.', category='error')
        else:
            conn = sqlite3.connect('website/database.db')
            c = conn.cursor()

            c.execute("SELECT * FROM users WHERE username=?", (username,))
            user = c.fetchone()

            conn.close()

            if user:
                if check_password_hash(user[3], password):
                    session["id"] = user[0]
                    session["username"] = username
                    session["displayName"] = user[5]
                    session.permanent = remember

                    flash('Logged in successfully!', category='success')
                    return redirect(url_for('views.messages'))
                else:
                    flash('Incorrect password. Try a different password.', category='error')
            else:
                flash('User does not exist.', category='error')

    return render_template('login.html')

@views.route("/login/quick")
def quickLogin():
    return render_template('quick-login.html')

@views.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if account_exists(email, username):
            flash('You already have an account!', category='error')
        elif len(email) < 4 or not '@' in email:
            flash('Email is not valid!', category='error')
        elif len(username) < 5:
            flash('Username must be atleast 4 characters!', category='error')
        elif password1 != password2:
            flash('Password confirmation does not match!', category='error')
        elif len(password1) < 7:
            flash('Password must be atleast 6 characters!', category='error')
        else:
            conn = sqlite3.connect('website/database.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, username, password, quick_login, display_name) VALUES (?, ?, ?, ?, ?)", (email, username, generate_password_hash(password1), None, username))
            conn.commit()
            conn.close()

            flash('Your account has been created!', category='success')
            return redirect(url_for('views.login'))

    return render_template('signup.html')

@views.route("/me/messages/", methods=['GET', 'POST'])
def messages():
    if "displayName" in session:
        friend_names = []
        id = session['id']

        conn = sqlite3.connect('website/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (int(id),))
        friends = c.fetchone()[6]

        if friends is not None:
            for id in friends:
                c.execute("SELECT * FROM users WHERE id=?", (int(id),))
                user = c.fetchone()[5]
                friend_names.append(user)

        if request.method == 'POST':
            friend_name = request.form.get('friend-name')

            print(friend_name)
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=?", (friend_name,))
            result = c.fetchone()
            requests = result[7].split('.') if result and result[7] else None

            if not result:
                flash('This person does not exist!', 'error')
            elif friend_name in friend_names:
                flash('You are already friends with this person!', 'error')
            elif requests:
                if session['id'] in requests:
                    flash('You have already sent this person a friend request!', 'error')
                else:
                    c = conn.cursor()
                    requests.append(str(session['id']))
                    c.execute("UPDATE users SET friend_requests = ? WHERE username = ?", ('.'.join(requests), friend_name))
                    flash(f'Sent friend request to {friend_name}', 'success')
            else:
                c = conn.cursor()
                c.execute("UPDATE users SET friend_requests = ? WHERE username = ?", (session['id'], friend_name))
                flash(f'Sent friend request to {friend_name}', 'success')

            conn.commit()
            conn.close()

        return render_template('messages-close.html', 
                               username=session['displayName'], 
                               friends_list_length=len(friend_names), 
                               friends_names=friend_names)
    else:
        return redirect(url_for('views.login'))
    
@views.route("/me/messages/friend/<friend>", methods=['GET', 'POST'])
def messages_open(friend):
    if "displayName" in session:
        friend_names = []
        id = session['id']

        conn = sqlite3.connect('website/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (int(id),))
        friends = c.fetchone()[6]

        if friends is not None:
            for id in friends:
                c.execute("SELECT * FROM users WHERE id=?", (int(id),))
                user = c.fetchone()[5]
                friend_names.append(user)

            c.execute("SELECT * FROM users WHERE display_name=?", (friend,))
            friend_id = str(c.fetchone()[0])

            c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;", ("chat." + str(session['id']) + "." + friend_id,))
            chat = c.fetchone()
            chat_name = None

            if chat is None:
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;", ('chat.' + friend_id + '.' + str(session['id']),))
                chat = c.fetchone()
                if chat is None:
                    chat = []
                    chat_name = None
                else:
                    c = conn.cursor()
                    c.execute(f"SELECT * FROM '{'chat.' + friend_id + '.' + str(session['id'])}'")
                    chat = c.fetchall()
                    chat_name = 'chat.' + friend_id + '.' + str(session['id'])
            else:
                c = conn.cursor()
                c.execute(f"SELECT * FROM '{'chat.' + str(session['id']) + '.' + friend_id}'")
                chat = c.fetchall()
                chat_name = 'chat.' + str(session['id']) + '.' + friend_id

        if request.method == "POST":
            message = request.form.get('message')
            if message:
                c.execute(f"INSERT INTO '{chat_name}' (sent_by, content, time_sent, read) VALUES (?, ?, ?, ?)", (session["id"], message, datetime.now().strftime("%H:%M"), 0))
                c.execute(f"SELECT * FROM '{chat_name}' WHERE id=?", (c.lastrowid,))
                chat.append(c.fetchone())
                conn.commit()
                return redirect('/me/messages/friend/' + friend)
        
        conn.close()

        return render_template('messages-open.html', 
                               username=session['displayName'], 
                               friends_list_length=len(friend_names), 
                               friends_names=friend_names, 
                               friend=friend, 
                               messages_list_length=len(chat), 
                               messages=chat, 
                               id=str(session['id']))
    else:
        return redirect(url_for('views.login'))
    
@views.route("/me/messages/add", methods=['GET', 'POST'])
def messages_add_friend():
    if "displayName" in session:
        friend_names = []
        id = session['id']

        conn = sqlite3.connect('website/database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id=?", (int(id),))
        friends = c.fetchone()[6]

        if friends is not None:
            for id in friends:
                c = conn.cursor()
                c.execute("SELECT * FROM users WHERE id=?", (int(id),))
                user = c.fetchone()[5]
                friend_names.append(user)
                conn.close()

        return render_template('messages-add-friend.html', 
                               username=session['displayName'], 
                               friends_list_length=len(friend_names), 
                               friends_names=friend_names
                               )
    else:
        return redirect(url_for('views.login'))
    
@views.route("/me/messages/redirect/<friend>")
def system_redirect(friend):
    return redirect(url_for('views.messages_open/friend', value=friend))
    
@views.route("/me/account/logout")
def logout():
    session.pop("username", None)
    session.pop("displayName", None)
    return redirect(url_for('views.login'))

@views.route("/me/info/messages")
def info_messages():
    conn = sqlite3.connect('website/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (session['id'],))
    user = c.fetchone()
    requests_ids = user[7].split(".") if user[7] and user[7] is not None else []
    requests = []

    for id in requests_ids:
        if id:
            c.execute("SELECT * FROM users WHERE id=?", (int(id),))
            requests.append(c.fetchone()[2])

    conn.close()
    return render_template('info-messages.html', requests=requests, requests_list_length=len(requests))

@views.route("/me/friends/add/accept/", methods=['GET'])
def accept_request():
    friend_name = request.args.get('value')

    conn = sqlite3.connect('website/database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (friend_name,))
    friend_id = c.fetchone()[0]

    c.execute("SELECT * FROM users WHERE id=?", (session['id'],))
    requests_ids = c.fetchone()[7].split(".")
    id_index = None

    for index, current_id in enumerate(requests_ids[:]):
        print(current_id, friend_id, index)
        if str(current_id) == str(friend_id):
            id_index = index

    if id_index is not None:
        requests_ids.pop(id_index)
        c.execute("UPDATE users SET friend_requests = ? WHERE id = ?", (".".join(requests_ids), session['id']))
        c.execute("SELECT * FROM users WHERE id=?", (session['id'],))
        friends_list = c.fetchone()[6].split('.') if c.fetchone()[6] else []
        friends_list.append(str(friend_id))
        c.execute("UPDATE users SET friends = ? WHERE id = ?", ('.'.join(friends_list), session['id']))

        c.execute("SELECT * FROM users WHERE id=?", (friend_id,))
        friends_list = c.fetchone()[6].split('.') if c.fetchone()[6] else []
        friends_list.append(str(session['id']))
        c.execute("UPDATE users SET friends = ? WHERE id = ?", ('.'.join(friends_list), friend_id))

        c.execute(f"""CREATE TABLE 'chat.{session['id']}.{friend_id}' (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_by TEXT,
            content TEXT,
            time_sent TEXT,
            read INTEGER
        )""")

        conn.commit()


    conn.close()

    
    return redirect(url_for('views.messages'))