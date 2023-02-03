from flask import Flask, redirect, render_template, session, url_for, request
from solid.solid_api import SolidAPI
from solid.auth import Auth

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/')
def home():
    name = None
    if 'papayademousername' in session:
        name = session['papayademousername']
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
            auth = Auth()
            solid_connection = SolidAPI(auth)
            auth.login(IDP, request.form['username'], request.form['password'])
            session['papayademousername'] = request.form['username']
            return redirect(url_for("home"))
        except Exception as inst:
            error = inst
    return render_template('login.html', error=error)
    
    