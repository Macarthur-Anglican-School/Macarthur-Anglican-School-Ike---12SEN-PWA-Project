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
        query = text('SELECT * FROM vulnerabilities ORDER BY owasp_rank;')
        result = connection.execute(query).fetchall()

    return render_template('index.html', vulnerabilities=result)

@app.route('/incidents/<vul_id>')
def incident_page(vul_id):
    # TASK 1: Connect to the database
    with engine.connect() as connect1:
        # This way of connecting to the database 
        # ensures that the connection is automatically closed as soon as the function finishes
        query = text(f'SELECT inc_name, inc_year, inc_url FROM incidents WHERE vul_id = :vul_id')
        result1 = connect1.execute(query, {"vul_id":vul_id}).fetchall() 

    # TASK 2: Fetch the Vulnerability Name for the heading (JOIN or separate query)
    with engine.connect() as connect2:
        # This way of connecting to the database 
        # ensures that the connection is automatically closed as soon as the function finishes
        query = text(f'SELECT vul_name FROM vulnerabilities WHERE id = :vul_id')
        result2 = connect2.execute(query, {"vul_id": vul_id}).fetchone()

    # TASK 3: Fetch all Incidents linked to this vul_id, return incidents list
    print(result1)
    print(result2)

    print(vul_id) #this is a print statement to help you understand what data is being returned
    return render_template('incidents.html', vulnerability = result2, incidents = result1)

@app.route('/add-incident', methods=['GET', 'POST'])
def add_incident():
    if request.method == 'POST':
        # TASK 1: Get form data
        inc_name = request.form.get['inc_name']
        inc_year = request.form['inc_year']
        inc_url = request.form['inc_url']
        vul_id = request.form['vul_id']

        # TASK 2: Insert new incident into the database
        with engine.connect() as connection:
            query = text(f'INSERT INTO incidents (inc_name, inc_year, inc_url, vul_id) VALUES ({inc_name}, {inc_year}, {inc_url}, {vul_id})')
            connection.execute(query)

        return redirect(url_for('/'))  # Redirect to home page after adding incident

    # If GET request, render the add incident form
    return render_template('add_incident.html')
app.run(debug=True, reloader_type='stat', port=5000)