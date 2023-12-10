from gevent import monkey
monkey.patch_all()
import os
from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from models import db, User, Word
from db_operations import add_user, get_users, update_user, delete_user, add_word, get_words, update_word, delete_word
from prompter import send_prompt_to_openai
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv, find_dotenv
import json

# Load environment variables
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Initialize Flask and its extensions
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jlo_ai.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='gevent')

# Setup OAuth
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=os.environ.get("AUTH0_CLIENT_ID"),
    client_secret=os.environ.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{os.environ.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/")
def home():
    if 'user' in session:
        # User is logged in, render the index page with user session details
        return render_template('index.html', session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))
    else:
        # User is not logged in, render the home page
        return render_template("home.html")


# Clear the Jinja2 cache
app.jinja_env.cache = {}

@socketio.on('send_prompt')
def handle_send_prompt(data):
    CMD = data['CMD']
    tag = data['tag']
    SPINS = data['SPINS']

    response, difficult_words = send_prompt_to_openai(CMD, tag, SPINS)
    emit('prompt_response', {'text_response': response, 'difficult_words': difficult_words})


@app.route('/prompter', methods=['GET'])
def prompter():
    # Render the prompter form
    return render_template('prompter_form.html')

@socketio.on('send_prompt')
def handle_send_prompt(data):
    CMD = data['CMD']
    tag = data['tag']
    SPINS = data['SPINS']

    response, difficult_words = send_prompt_to_openai(CMD, tag, SPINS)
    emit('prompt_response', {'text_response': response, 'difficult_words': difficult_words})

    
 
                           

@app.route('/add_user', methods=['GET', 'POST'])
def route_add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        response = add_user(username, email)
        return jsonify({'message': response})
    return render_template('add_user.html')

@app.route('/users', methods=['GET'])
def route_get_users():
    users = get_users()
    return render_template('users.html', users=users)

@app.route('/update_user/<int:user_id>', methods=['GET', 'POST'])
def route_update_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('route_get_users'))
    return render_template('update_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def route_delete_user(user_id):
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('route_get_users'))

@app.route('/add_word', methods=['GET', 'POST'])
def route_add_word():
    if request.method == 'POST':
        japanese = request.form['japanese']
        english = request.form['english']
        response = add_word(japanese, english)
        return jsonify({'message': response})
    return render_template('add_word.html')

@app.route('/get_words', methods=['GET'])
def route_get_words():
    words = get_words()
    return render_template('get_words.html', words=words)

@app.route('/update_word/<int:word_id>', methods=['GET', 'POST'])
def route_update_word(word_id):
    word = Word.query.get(word_id)
    if request.method == 'POST':
        word.japanese = request.form['japanese']
        word.english = request.form['english']
        db.session.commit()
        return redirect(url_for('route_get_words'))
    return render_template('update_word.html', word=word)

@app.route('/delete_word/<int:word_id>', methods=['POST'])
def route_delete_word(word_id):
    word = Word.query.get(word_id)
    db.session.delete(word)
    db.session.commit()
    return redirect(url_for('route_get_words'))

@app.cli.command('create_db')
def create_db():
    db.create_all()
    print("Database tables created.")

if __name__ == '__main__':
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler

    http_server = WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    http_server.serve_forever()
