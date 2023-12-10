import logging
import threading
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, User, Word
from dotenv import load_dotenv, find_dotenv
from db_operations import add_user, get_users, update_user, delete_user, add_word, get_words, update_word, delete_word
from prompter import send_prompt_to_openai 
from authlib.integrations.flask_client import OAuth
import asyncio
import os
from os import environ as env
import json
from urllib.parse import urlencode
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jlo_ai.db'
app.config['TEMPLATES_AUTO_RELOAD'] = True
db.init_app(app)

tasks = {}

oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

async def process_openai_api(CMD, tag, SPINS, task_id):
    text_response, difficult_words = await send_prompt_to_openai(CMD, tag, SPINS)
    tasks[task_id] = {'text_response': text_response, 'difficult_words': difficult_words}

def start_async_task(coro):
    """
    Starts an asyncio event loop and runs the given coroutine.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)
    loop.close()

@app.route('/get_prompt_results', methods=['POST'])
def get_prompt_results():
    data = request.get_json()
    CMD = data['CMD']
    tag = data['tag']
    SPINS = data['SPINS']

    task_id = str(uuid.uuid4())

    # Start a new thread to run the async function
    thread = threading.Thread(target=start_async_task, args=(process_openai_api(CMD, tag, SPINS, task_id),))
    thread.start()

    return jsonify({'task_id': task_id})





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




@app.route('/check_task_status', methods=['GET'])
def check_task_status():
    task_id = request.args.get('task_id')
    result = tasks.get(task_id)
    if result:
        return jsonify(result)
    else:
        return jsonify({'status': 'processing'})

@app.route('/prompter', methods=['GET'])
def prompter():
    # Render the prompter form
    return render_template('prompter_form.html')

    
 
                           

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
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)