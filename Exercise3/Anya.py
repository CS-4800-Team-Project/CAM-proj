from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/question', methods=['GET'])
def question():
    return jsonify({'question': 'Are there problems in your life? (y/n)'})

@app.route("/answer/<yesorno>", methods=['POST'])
def search_answer(yesorno):
    if yesorno == 'y':
        response = {'response': 'Can you solve it?'}
    elif yesorno == 'n':
        response = {'response': "Then don't worry!"}
    else:
        response = {'error': 'Wrong input, please try again.'}
    return jsonify(response)

app.run(host = "0.0.0.0")
