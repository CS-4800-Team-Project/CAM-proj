from flask import Flask, render_template, request, jsonify
import pymysql

app = Flask(__name__, template_folder="template")

# Set up database connection
cnx = pymysql.connect(user='root', password='Blackops1871!',
                      host='127.0.0.1', database='recipes_db')
if cnx.open:
    print('Database connection successful')
else:
    print('Database connection failed')

cursor = cnx.cursor()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        select_query = f"SELECT title, url, rating, reviews, made_it_count " \
                       f"FROM recipes WHERE title LIKE '%{search_query}%'"
        cursor.execute(select_query)
        results = cursor.fetchall()
        return render_template('search_results.html', results=results)
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    print('search function called')
    search_query = request.args.get('query')
    if search_query is not None:
        select_query = f"SELECT title, url, rating, reviews FROM recipes WHERE title LIKE %s"
        cursor.execute(select_query, ('%' + search_query + '%',))
        results = [{'title': row[0], 'url': row[1], 'rating': row[2], 'reviews': row[3]} for row in cursor.fetchall()]
        print(f"query results: {results}")
        return jsonify({'results': results})
    else:
        return jsonify({'error': 'No search query provided'})

    # call the displayResults function with the search results
    displayResults(results)





if __name__ == '__main__':
    app.run(debug=True)
