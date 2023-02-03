from flask import Flask, redirect, render_template, session, url_for

app = Flask(__name__)


@app.route('/')
def home(name=None):
    return render_template(
        "home.html",
        name = name,
    )
@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        try:
            IDP = 'https://solidcommunity.net'
            auth.login(IDP, request.form['username'], request.form['password'])
            return home(request.form['username'])
        except :
            error = 'Invalid username/password' 
    return render_template('login.html', error=error)
    
    