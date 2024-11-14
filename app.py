from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

def load_user_domains(username):
    with open(f"{username}_domains.txt", 'r') as d:
        data = json.load(d)
    return data.get('domains')



@app.route('/')
def index():   
    return render_template('index.html')



# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001)