from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )
@app.route('/login')
def login():
    
    