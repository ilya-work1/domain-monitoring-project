from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from login import check_login, check_username_avaliability, registration
from domains_check_MT import check_url_mt as check_url
import os
import json
from datetime import timedelta



# Initialize Flask app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = True  
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=10) 
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    """
    Check if the users is logged in or not and redirect to the login or dashboard page"""
    if not session.get("username"):
        # if not, then redirect to the login page
        return render_template("index.html")
    return render_template('dashboard.html', username=session.get("username"))


@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)


@app.route('/login', methods=['POST'])
def login():
    """
    Check login credentials and create flask session"""
    # Get input user from form
    username = request.form.get('username')
    password = request.form.get('password')
    print(f'username:{username}, password:{password}')
    # Check credentials
    if check_login(username, password):
        session['username'] = username  # Create session
        print("you are logged in", session['username'])
        return redirect("/")
    else:
        print("you are not logged in")
        error_message = "Wrong Username or Password"
        return render_template("index.html", error=error_message)
    

@app.route('/checkUserAvaliability', methods=['GET'])
def checkUserAvaliability():
    username = request.args.get('username')
    if check_username_avaliability(username):
        return { "available": True }
    else:
        return { "available": False }



@app.route('/register')
def register():
    return render_template('registration.html')

@app.route('/NewUser', methods=['POST'])
def NewUser():
    username = request.form.get('username')
    password = request.form.get('password')
    registration(username, password)
    return redirect('/')
    

@app.route("/logout")
def logout():
    # session['username'] = None
    session.pop('username', default=None)
    return redirect("/")


@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' in session:
        # return render_template('dashboard.html')
        return f'Welcome to your dashboard, {session["username"]}!'
    return 'You are not logged in.', 401

def check_username_domains(username):
    if os.path.exists(f'{username}.json'):
        with open(f'{username}.json', 'r') as f:
            data = json.load(f)
        return data.get('domains', [])
    return []


@app.route('/check_domains', methods=['POST'])
def check_domains():
    try:
        username = session.get('username')
        if not username:
            return jsonify({'message': 'You are not logged in!'}), 401
        
        # Get domains from request body
        data = request.get_json()
        domains = data.get('domains', [])
        print("Domains received:", domains)

        # Use existing check_url_mt function
        results = check_url(domains)
        print("Results:", results)

        return jsonify(results)
    except Exception as e:
        return jsonify({'message': 'An error occurred while checking domains.', 'error': str(e)}), 500




    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
