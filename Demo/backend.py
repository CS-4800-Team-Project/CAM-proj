from flask import Flask, render_template, request, jsonify, url_for, redirect, flash
import requests
import openai
import os
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import secrets


# Set up database connection
db = sqlite3.connect('recipes_db.db', check_same_thread=False)
cursor = db.cursor()


def init_db():
    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')

    # Create ratings table
    cursor.execute('''CREATE TABLE IF NOT EXISTS ratings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        recipe_id INTEGER NOT NULL,
                        rating INTEGER NOT NULL,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    # Create favorites table
    cursor.execute('''CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        recipe_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    # Create searches table
    cursor.execute('''CREATE TABLE IF NOT EXISTS searches (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        query TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id))''')

    # Commit the changes
    db.commit()


init_db()

openai.api_key = os.environ.get('OPENAI_API_KEY')

app = Flask(__name__, template_folder="template", static_folder="static")

app.config['SECRET_KEY'] = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

API_KEY = '8101db824a1c4a8ea99f3e7f77e01a75'

def search_recipes(query):
    url = f"https://api.spoonacular.com/recipes/complexSearch?apiKey={API_KEY}&query={query}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json()['results']
        for result in results:
            recipe_id = result['id']
            cursor.execute("SELECT AVG(rating) FROM ratings WHERE recipe_id = ?", (recipe_id,))
            average_rating = cursor.fetchone()[0]
            result['averageRating'] = average_rating
        return results
    else:
        return []


def generate_recipe(ingredients):
    prompt = f"Create a delicious recipe using most the following ingredients, it is not necessarry to use all the ingridients use your best judgement: {', '.join(ingredients)}.\n\nRecipe:"
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,  # Adjust temperature, higher is more creative and random lower is more focused
    )

    recipe = response.choices[0].text.strip()
    return recipe

@app.route('/', methods=['GET', 'POST'])
def index():
    logo_image = url_for('static', filename='Yum.jpg')
    if request.method == 'POST':
        if 'search_query' in request.form:
            search_query = request.form['search_query']
            results = search_recipes(search_query)
            return render_template('search_results.html', results=results, logo_image=logo_image, current_user=current_user)
        elif 'ingredients' in request.form:
            ingredients = request.form['ingredients'].split(', ')
            recipe = generate_recipe(ingredients)
            return render_template('generated_recipe.html', recipe=recipe, logo_image=logo_image, current_user=current_user)
    return render_template('index.html', logo_image=logo_image, current_user=current_user)


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
    cursor.execute("SELECT COUNT(*) FROM favorites WHERE recipe_id = ?", (recipe_id,))
    favorites_count = cursor.fetchone()[0]
    bg_image = url_for('static', filename='Food.jpg')
    if recipe:
        return render_template('recipe_details.html', recipe=recipe, bg_image=bg_image, favorites_count=favorites_count)
    else:
        return redirect(url_for('index'))


def get_recipe_details(recipe_id):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/generated_recipe', methods=['GET'])
def generated_recipe():
    if request.args.get('ingredients'):
        ingredients = request.args.get('ingredients').split(', ')
        recipe = generate_recipe(ingredients)
        bg_image = url_for('static', filename='Food.jpg')
        return render_template('generated_recipe.html', recipe=recipe, bg_image=bg_image)
    else:
        return redirect(url_for('index'))

class User(UserMixin):
    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password = password

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    if result:
        return User(result[0], result[1], result[2], result[3])
    else:
        return None



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        password = request.form['password']

        user = load_user_by_username(username_or_email)
        if not user:
            user = load_user_by_email(username_or_email)

        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('profile'))
        else:
            return "Invalid username or password."
    else:
        return render_template('login.html')


@app.route('/rate_recipe/<int:recipe_id>', methods=['POST'])
@login_required
def rate_recipe(recipe_id):
    rating_value = request.form['rating']
    user_id = current_user.id

    cursor.execute("SELECT * FROM ratings WHERE user_id = ? AND recipe_id = ?", (user_id, recipe_id))
    existing_rating = cursor.fetchone()

    if existing_rating:
        cursor.execute("UPDATE ratings SET rating = ? WHERE user_id = ? AND recipe_id = ?", (rating_value, user_id, recipe_id))
    else:
        cursor.execute("INSERT INTO ratings (user_id, recipe_id, rating) VALUES (?, ?, ?)", (user_id, recipe_id, rating_value))

    db.commit()
    return redirect(url_for('recipe_details', recipe_id=recipe_id))



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        if check_username_exists(username):
            return "Username already exists."

        # Save the new user to the database
        hashed_password = generate_password_hash(password, method='sha256')

        query = "INSERT INTO users (username, password, email) VALUES (?, ?, ?)"
        cursor.execute(query, (username, hashed_password, email))
        db.commit()

        return redirect(url_for('login'))

    # Render the signup.html template when the request method is 'GET'
    return render_template('signup.html')

@app.route('/profile')
@login_required
def profile():
    top_ratings, searches_count = get_user_stats(current_user.id)
    favorite_recipes = get_favorite_recipes(current_user.id)
    return render_template('profile.html', current_user=current_user, top_ratings=top_ratings, searches_count=searches_count, favorite_recipes=favorite_recipes, get_recipe_details=get_recipe_details)



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/toggle_favorite/<int:recipe_id>', methods=['POST'])
@login_required
def toggle_favorite_route(recipe_id):
    toggle_favorite(current_user.id, recipe_id)
    return redirect(url_for('recipe_details', recipe_id=recipe_id))


def get_profile_link():
    if current_user.is_authenticated:
        return url_for('profile')
    else:
        return url_for('login')

# Updated function
def load_user_by_username(username):
    cursor.execute("SELECT id, username, email, password FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    if result:
        user_id, username, email, password = result
        user = User(user_id, username, email, password)
        return user
    else:
        return None

# Updated function
def load_user_by_email(email):
    cursor.execute("SELECT id, username, email, password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()

    if result:
        user_id, username, email, password = result
        user = User(user_id, username, email, password)
        return user
    else:
        return None

# Updated function
def check_username_exists(username):
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()

    return result is not None

# Updated function
def get_user_stats(user_id):
    cursor.execute("SELECT recipe_id, rating FROM ratings WHERE user_id = ? ORDER BY rating DESC LIMIT 3", (user_id,))
    top_ratings = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM searches WHERE user_id = ?", (user_id,))
    searches_count = cursor.fetchone()[0]

    cursor.execute("SELECT recipe_id FROM favorites WHERE user_id = ?", (user_id,))
    favorite_recipes = cursor.fetchall()

    return top_ratings, favorite_recipes

# Updated function
def toggle_favorite(user_id, recipe_id):
    cursor.execute("SELECT * FROM favorites WHERE user_id = ? AND recipe_id = ?", (user_id, recipe_id))
    existing_favorite = cursor.fetchone()

    if existing_favorite:
        cursor.execute("DELETE FROM favorites WHERE user_id = ? AND recipe_id = ?", (user_id, recipe_id))
    else:
        cursor.execute("INSERT INTO favorites (user_id, recipe_id) VALUES (?, ?)", (user_id, recipe_id))

    db.commit()

# Updated function
def get_favorite_recipes(user_id):
    cursor.execute("SELECT recipe_id FROM favorites WHERE user_id = ?", (user_id,))
    favorite_recipe_ids = [row[0] for row in cursor.fetchall()]
    favorite_recipes = []
    for recipe_id in favorite_recipe_ids:
        recipe = get_recipe_details(recipe_id)
        if recipe:
            favorite_recipes.append(recipe)
    return favorite_recipes

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
