from flask import Flask, render_template,request, jsonify
import os 
import json
from domains_check_MT import check_url_mt as dcmt



# Initialize Flask app
app = Flask(__name__)

@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

# Load user domains from file if it exists
def load_user_domains(username):
if os.path.exists(f"{username}_domains.txt"):
    with open(f"{username}_domains.txt", 'r') as d:
        data = json.load(d)
    return data.get("urls", [])


# Save user domains to file and return the list of domains
@app.route('/checkurl', methods=['GET', 'POST'])
def checkurl():
    username = request.form.get('username')
    if not username:
        return jsonify({'error': 'Username is required'})
    urls = load_user_domains(username)
    results = dcmt(urls)
    return jsonify(results)


@app.route('/')
def index():   
    return render_template('index.html')




# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001)