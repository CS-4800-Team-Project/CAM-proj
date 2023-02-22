from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/v1/hello', methods=['GET'])
def hello():
    response = {
        'message': 'Hello, world!'
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
