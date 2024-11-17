from flask import Flask, render_template, request, session, redirect, jsonify
from flask_session import Session
from login import check_login, check_username_avaliability, registration
from domains_check_MT import check_url, analyzed_urls_queue

# Initialize Flask app
app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
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
        error_message = "Wrong user or password"
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


@app.route('/check_domains', methods=['POST'])
def check_domains():
    if not session.get("username"):
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    domains = data.get('domains', [])

    # Use your existing check_url function
    check_url(domains)

    # Collect results from the analyzed_urls_queue
    results = []
    while not analyzed_urls_queue.empty():
        results.append(analyzed_urls_queue.get())

    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8081)
