from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from login import check_login, check_username_avaliability, registration
from domains_check_MT import check_url_mt as check_url

# Initialize Flask app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def index():
    # check if the users is logged in or not
    if not session.get("username"):
        # if not there in the session then redirect to the login page
        return render_template("index.html")
    return render_template('dashboard.html')


@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)


@app.route('/login', methods=['POST'])
def login():
    # data = request.get_json()
    username = request.form.get('username')
    password = request.form.get('password')
    print(f'username:{username}, password:{password}')
    # if not os.path.exists('users.json'):
    #    return jsonify({'message': 'No users registered!'}), 400

    # with open('users.json', 'r') as f:
    #   users = json.load(f)

    # Validate credentials
    # if username in users and users[username] == password:
    if check_login(username, password):
        session['username'] = username  # Create session
        print("you are logged in", session['username'])

        # return jsonify({'message': 'Login successful!', 'redirect': '/dashboard'}), 200
        # return jsonify({'message': 'Login successful!'}), 200
    else:
        print("you are not logged in")
        # return jsonify({'message': 'Invalid credentials!'}), 401
        # return jsonify({'message': 'Invalid credentials!'}), 401
    return redirect("/", )


@app.route('/register')
def register():
    return render_template('registration.html')


@app.route("/logout")
def logout():
    session['username'] = None
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
        urls = check_username_domains(username)
        if not urls:
            return jsonify({'message': 'No domains to check!'}), 400
        
        # Use your existing check_url function
        results = check_url(urls)
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'message': 'An error occurred while checking domains.', 'error': str(e)}), 500



    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0' ,port=8080)