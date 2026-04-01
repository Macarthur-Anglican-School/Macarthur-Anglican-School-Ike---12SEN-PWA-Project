from flask import Flask, request, render_template, redirect, url_for
from sqlalchemy import create_engine, text

app = Flask(__name__)

engine = create_engine('sqlite:///.database/cyberwatch.db') #link to the cyberwatch database here

#route for index.html
@app.route('/')
def home(): 
    
    with engine.connect() as connection:
        # This way of connecting to the database 
        # ensures that the connection is automatically closed as soon as the function finishes
        query = text(
            'SELECT vulnerabilities.*, COUNT(incidents.id) AS incident_count '
            'FROM vulnerabilities '
            'LEFT JOIN incidents ON incidents.vul_id = vulnerabilities.id '
            'GROUP BY vulnerabilities.id '
            'ORDER BY vulnerabilities.owasp_rank;'
        )
        result = connection.execute(query).fetchall()

    return render_template('index.html', vulnerabilities=result)

@app.route('/incidents/<vul_id>')
def incident_page(vul_id):
    selected_year = request.args.get('year', '').strip()

    with engine.connect() as connection:
        incidents_years_query = text(
            'SELECT DISTINCT inc_year FROM incidents '
            'WHERE vul_id = :vul_id ORDER BY inc_year DESC'
        )
        available_years = connection.execute(
            incidents_years_query, {"vul_id": vul_id}
        ).fetchall()

        incidents_query = (
            'SELECT inc_name, inc_year, inc_url FROM incidents '
            'WHERE vul_id = :vul_id'
        )
        query_params = {"vul_id": vul_id}

        if selected_year:
            incidents_query += ' AND inc_year = :selected_year'
            query_params["selected_year"] = selected_year

        incidents_query += ' ORDER BY inc_year DESC, inc_name ASC'
        result1 = connection.execute(text(incidents_query), query_params).fetchall()

        vulnerability_query = text(
            'SELECT vul_name FROM vulnerabilities WHERE id = :vul_id'
        )
        result2 = connection.execute(
            vulnerability_query, {"vul_id": vul_id}
        ).fetchone()

    return render_template(
        'incidents.html',
        vulnerability=result2,
        incidents=result1,
        available_years=available_years,
        selected_year=selected_year
    )

@app.route('/add-incident', methods=['GET', 'POST'])
def add_incident():
    if request.method == 'POST':
        # TASK 1: Get form data
        inc_name = request.form.get('inc_name')
        inc_year = request.form.get('inc_year')
        inc_url = request.form.get('inc_url')
        vul_id = request.form.get('vul_id')
        print('VUL_ID:', vul_id) # Debugging statement to check if vul_id is being received correctly
        
        # TASK 2: Insert new incident into the database
        # with engine.connect() as connection:
        print('hi')
        connection = engine.connect()  # Establish a connection to the database
        query = text(f'INSERT INTO incidents (inc_name, inc_year, inc_url, vul_id) VALUES (:inc_name, :inc_year, :inc_url, :vul_id);')
        connection.execute(query, {
            "inc_name": inc_name,
            "inc_year": inc_year,
            "inc_url": inc_url,
            "vul_id": vul_id
        })
        connection.commit()
        connection.close()

        return redirect(url_for('home'))  # Redirect to home page after adding incident

    # If GET request, render the add incident form
    return render_template('add-incident.html')
app.run(debug=True, reloader_type='stat', port=5000)
