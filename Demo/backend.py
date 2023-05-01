from flask import Flask, render_template, request, jsonify, url_for, redirect
import requests
import openai

# Replace your_api_key with your actual OpenAI API key
openai.api_key = "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"

app = Flask(__name__, template_folder="template")

API_KEY = '8101db824a1c4a8ea99f3e7f77e01a75'

def search_recipes(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        return []

def generate_recipe(ingredients):
    prompt = f"Create a delicious recipe using the following ingredients: {', '.join(ingredients)}.\n\nRecipe:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )

    recipe = response.choices[0].text.strip()
    return recipe

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'search_query' in request.form:
            search_query = request.form['search_query']
            results = search_recipes(search_query)
            return render_template('search_results.html', results=results)
        elif 'ingredients' in request.form:
            ingredients = request.form['ingredients'].split(', ')
            recipe = generate_recipe(ingredients)
            return render_template('generated_recipe.html', recipe=recipe)
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

@app.route('/recipe/<int:recipe_id>', methods=['GET'])
def recipe_details(recipe_id):
    recipe = get_recipe_details(recipe_id)
    bg_image = url_for('static', filename='Food.jpg')
    if recipe:
        return render_template('recipe_details.html', recipe=recipe, bg_image=bg_image)
    else:
        return redirect(url_for('index'))

def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)


