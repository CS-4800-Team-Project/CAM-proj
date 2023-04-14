from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder="template")

API_KEY = '8101db824a1c4a8ea99f3e7f77e01a75'

def search_recipes(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        results = search_recipes(search_query)
        return render_template('search_results.html', results=results)
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    print('search function called')
    search_query = request.args.get('query')
    if search_query is not None:
        results = search_recipes(search_query)
        print(f"query results: {results}")
        return jsonify({'results': results})
    else:
        return jsonify({'error': 'No search query provided'})



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

