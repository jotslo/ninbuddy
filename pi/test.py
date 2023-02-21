from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def dashboard():
    return render_template('dashboard.html')

@app.route('/data')
def get_data():
    # Return some example data as a JSON response
    data = {'message': 'Hello, World!'}
    return jsonify(data)

@app.route('/main.js')
def get_main_js():
    # Return the contents of main.js as a JavaScript response
    with open('pi/templates/main.js', 'r') as f:
        return f.read()

if __name__ == '__main__':
    app.run(port=8000)