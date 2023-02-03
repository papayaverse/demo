from flask import Flask, redirect, render_template, session, url_for, request
from solid.solid_api import SolidAPI
from solid.auth import Auth
from getpass import getpass
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
import json
import io
import re

app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

auth = Auth()
solid_connection = SolidAPI(auth)
web3_connection = None

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
            auth.login(IDP, request.form['username'], request.form['password'])
            profile = solid_connection.get('https://ramtest.solidcommunity.net/profile/card#me')
            uname = re.findall(r'foaf:name \"(.*)\"',profile.text)[0]
            session['papayademousername'] = uname
            session['papayademoacctname'] = request.form['username']
            return redirect(url_for("home"))
        except Exception as inst:
            error = inst
    return render_template('login.html', error=error)

@app.route('/wallet')
def wallet():
    uname = session['papayademousername']
    USERNAME = session['papayademoacctname']
    balance = 0
    new_wallet = False
    error = None
    web3providers = {
    "ethereum" : 'https://goerli.infura.io/v3/85e35e212e7c431a838571e469b3c64b',
    "starknet" : 'https://starknet-goerli.infura.io/v3/85e35e212e7c431a838571e469b3c64b',
    "avalanche" : 'https://avalanche-fuji.infura.io/v3/85e35e212e7c431a838571e469b3c64b'
    }
    chain = "avalanche" # change to an option later
    web3provider = web3providers[chain]
    web3_connection = Web3(HTTPProvider(web3provider))
    web3_connection.middleware_onion.inject(geth_poa_middleware, layer=0)
    if web3_connection.isConnected():
        wallet_folder = 'https://' + USERNAME + '.solidcommunity.net/public/wallet/' + chain + '/testnet/'
        private_wallet_folder = 'https://' + USERNAME + '.solidcommunity.net/private/wallet/' + chain + '/testnet/'
        required_files = ['provider.md', 'wallet_address.md']
        criterion = all([solid_connection.item_exists(wallet_folder + i) for i in required_files])
        if criterion: # Does the user already have a wallet?
            wallet_address_file_name = wallet_folder + 'wallet_address.md'
            wallet_address_resp = solid_connection.get(wallet_address_file_name)
            wallet_address = wallet_address_resp.text
        else :
            #create_wallet
            my_account = web3_connection.eth.account.create(USERNAME)
            wallet_address = my_account._address
            new_wallet = True
            ## Save wallet information if new wallet
            def save_wallet_info(file_string, file_nm):
                f = io.BytesIO(file_string.encode('UTF-8'))
                file_name = file_nm
                solid_connection.put_file(file_name, f, 'text/markdown')
            # Save provider
            save_wallet_info(web3provider, wallet_folder + 'provider.md')
            # Save wallet address
            save_wallet_info(wallet_address, wallet_folder + 'wallet_address.md')
            # Save private key
            private_key = my_account._private_key.hex()
            save_wallet_info(private_key, private_wallet_folder + 'private_key.md')
        balance_wei = web3_connection.eth.get_balance(account = wallet_address) # gets balance in wei
        balance = str(Web3.fromWei(balance_wei, 'ether'))
    else :
        error = "Not able to connect to " + chain + " Network"
    return render_template('wallet.html', name = uname, error = error, balance = balance, new_wallet = new_wallet)
    