from flask import Flask
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = '<replace with a secret key>'
toolbar = DebugToolbarExtension(app)


@app.route('/')
def index():
    return '<body>' \
           '<h1>Flask DebugToolbar!</h1>' \
           '</body>'


if __name__ == '__main__':
    app.run(debug=True)
