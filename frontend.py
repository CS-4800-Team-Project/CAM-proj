from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# Set up database connection
cnx = pymysql.connect(user='root', password='Blackops1871!',
                      host='127.0.0.1', database='recipes_db')
cursor = cnx.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    select_query = f"SELECT title, url, rating, reviews, made_it_count " \
                   f"FROM recipes WHERE title LIKE '%{query}%'"
    cursor.execute(select_query)
    results = cursor.fetchall()
    # return the results to the frontend for display
    return render_template('search_results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
