from flask import Flask

app = Flask(__name__)

print("Are there problems in your life? (y/n)")

@app.route("/search/<yesorno>")
def search_answer(yesorno):
    if yesorno == 'y':
        print("Can you solve it?")
    elif yesorno == 'n':
        print("Then don't worry!")
    else:
        print('Wrong input, please try again.')
    return

app.run(host = "0.0.0.0")
