from flask import Flask, render_template, request
import pymysql

app = Flask(__name__)

# Set up database connection
cnx = pymysql.connect(user='root', password='Blackops1871!',
                      host='127.0.0.1', database='recipes_db')
# Enable user cursor
cursor = cnx.cursor()

# Execute search query to return recipe results
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        select_query = f"SELECT title, url, rating, reviews, made_it_count " \
                       f"FROM recipes WHERE title LIKE '%{search_query}%'"
        cursor.execute(select_query)
        results = cursor.fetchall()
        # Return value of search results to display file
        return render_template('results.html', results=results)
    # Use result template from index display file
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
