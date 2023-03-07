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
web3providers = {
    "ethereum" : 'https://goerli.infura.io/v3/85e35e212e7c431a838571e469b3c64b',
    "starknet" : 'https://starknet-goerli.infura.io/v3/85e35e212e7c431a838571e469b3c64b',
    "avalanche" : 'https://avalanche-fuji.infura.io/v3/85e35e212e7c431a838571e469b3c64b'
    }

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
            profile = solid_connection.get('https://'+request.form['username']+'.solidcommunity.net/profile/card#me')
            uname = re.findall(r'foaf:name \"(.*)\"',profile.text)[0]
            session['papayademousername'] = uname
            session['papayademoacctname'] = request.form['username']
            return redirect(url_for("home"))
        except Exception as inst:
            error = inst
    return render_template('login.html', error=error)

@app.route('/avatar')
def avatar():
    # implement not pre existing avatar later
    # get avatar url from pod public folder
    USERNAME = session['papayademoacctname']
    avatar_file_url = 'https://'+USERNAME+'.solidcommunity.net/public/avatar.md'
    avatar_url_from_pod = solid_connection.get(avatar_file_url).text
    return render_template('avatar.html', name = session['papayademousername'], avatar_url = avatar_url_from_pod)

@app.route('/avatarcreator', methods=['POST', 'GET'])
def avatarcreator():
    # implement not pre existing avatar later
    # get avatar url from pod public folder
    USERNAME = session['papayademoacctname']
    if request.method == 'POST' :
        avatar_file_url = 'https://'+USERNAME+'.solidcommunity.net/public/avatar.md'
        avatar_url = request.form['avatarUrl']
        f = io.BytesIO(avatar_url.encode('UTF-8'))
        solid_connection.put_file(avatar_file_url, f, 'text/markdown')
        return redirect(url_for("avatar"))
    return render_template('avatarcreator.html')
    
    

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
    session['papayademochain'] = chain
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
        session['papayademobalance'] = balance_wei
    else :
        error = "Not able to connect to " + chain + " Network"
    return render_template('wallet.html', name = uname, error = error, balance = balance, new_wallet = new_wallet)

@app.route('/wallet/txn', methods=['POST', 'GET'])
def txn():
    error = None
    msg = None
    if request.method == 'POST' :
        try :
            USERNAME = session['papayademoacctname']
            chain = session['papayademochain']
            web3provider = web3providers[chain]
            web3_connection = Web3(HTTPProvider(web3provider))
            web3_connection.middleware_onion.inject(geth_poa_middleware, layer=0)
            wallet_folder = 'https://' + USERNAME + '.solidcommunity.net/public/wallet/' + chain + '/testnet/'
            private_wallet_folder = 'https://' + USERNAME + '.solidcommunity.net/private/wallet/' + chain + '/testnet/'
            wallet_address_file_name = wallet_folder + 'wallet_address.md'
            wallet_address_resp = solid_connection.get(wallet_address_file_name)
            wallet_address = wallet_address_resp.text
            private_key_file_name = private_wallet_folder + 'private_key.md'
            private_key = solid_connection.get(private_key_file_name).text
            TO_USER = request.form['toUser']
            AMOUNT = request.form['amountInput']
            is_signed = request.form['signed']
            TO_ADDRESS = solid_connection.get('https://' + TO_USER + '.solidcommunity.net/public/wallet/'+ chain + '/testnet/wallet_address.md').text
            transaction = {
                    "nonce": web3_connection.eth.get_transaction_count(wallet_address),
                    "gas": 21000,
                    "to": TO_ADDRESS,
                    "value": web3_connection.toWei(AMOUNT, "wei"),
                    "gasPrice" : 25000000000,
                    "chainId" : 43113
            }
            if is_signed:
                signed_txn = web3_connection.eth.account.signTransaction(transaction, private_key)
                txn_hash = web3_connection.eth.sendRawTransaction(signed_txn.rawTransaction)
                msg = "Transaction processed and the hash is "+ txn_hash.hex()
            else :
                msg = "Transaction not Signed"
        except ZeroDivisionError as e:
            error = e
    else :
        msg = "Welcome to the Transaction Form"
    return render_template('txn.html', error = error, msg = msg, balance = str(session['papayademobalance']))
        
    
    