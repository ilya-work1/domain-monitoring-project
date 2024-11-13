from flask import Flask, render_template , request , jsonify, session
import json

# Initialize Flask app
app = Flask(__name__)



@app.route('/')
def index():   
    return render_template('index.html')

@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not os.path.exists('users.json'):
        return jsonify({'message': 'No users registered!'}), 400

    with open('users.json', 'r') as f:
        users = json.load(f)

    # Validate credentials
    if username in users and users[username] == password:
        session['username'] = username  # Create session
        return jsonify({'message': 'Login successful!'}), 200
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'username' in session:
        return f'Welcome to your dashboard, {session["username"]}!'
    return 'You are not logged in.', 401

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001)