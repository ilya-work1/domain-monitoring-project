from flask import Flask

# Initialize Flask app
app = Flask(__name__)



@app.route('/')
def index():   
    return render_template('index.html')

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001)