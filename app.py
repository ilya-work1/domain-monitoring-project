from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

@app.route('/<filename>')
def file(filename):
    return app.send_static_file(filename)

@app.route('/')
def index():   
    return render_template('index.html')

@app.route('/register')
def register():   
    return render_template('registration.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001)