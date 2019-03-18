import sqlite3
import datetime
from flask import Flask, render_template, g, request, redirect, url_for

#Location of the database.
#Hardcoded here so it can be reused.
PATH = 'db/jobs.sqlite'

app = Flask(__name__)


def open_connection():
	#Connect to the database if it isn't already connected.
	connection = getattr(g, '_connection', None)
	if connection == None:
		connection = g._connection = sqlite3.connect(PATH)
	#This makes row indexing easier.
	connection.row_factory = sqlite3.Row
	return connection
	
	
def execute_sql(sql, values=(), commit=False, single=False):
	#Used for easier execution of sql statements.
	#Get the database connection.
	connection = open_connection()
	cursor = connection.execute(sql, values)
	if commit == True:
		results = connection.commit()
	else:
		#Ternary if based on number of results obtained.
		results = cursor.fetchone() if single else cursor.fetchall()
		
	cursor.close()
	return results
	
	
#Calls close_connection when the app context is destroyed.
@app.teardown_appcontext
def close_connection(exception):
	connection = getattr(g, '_connection', None)
	if connection is not None:
		connection.close()

		
#Decorators
#Decorators can be used to inject additional functionality to one or more functions.
@app.route('/')
@app.route('/jobs')
def jobs():
	#Get information about all jobs from the database.
	jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
	return render_template('index.html', jobs=jobs)
	
	
@app.route('/job/<job_id>')
def job(job_id):
	#Get information about a specific job from the database.
	job = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id WHERE job.id = ?', [job_id], single=True)
	return render_template('job.html', job=job)
	

@app.route('/employer/<employer_id>')	
def employer(employer_id):
	employer = execute_sql('SELECT * FROM employer WHERE id=?', [employer_id], single=True)
	#Get all jobs from a specific employer.
	jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary FROM job JOIN employer ON employer.id = job.employer_id WHERE employer.id = ?', [employer_id])
	#Get all reviews for a specific employer.
	reviews = execute_sql('SELECT review, rating, title, date, status FROM review JOIN employer ON employer.id = review.employer_id WHERE employer.id = ?', [employer_id])
	return render_template('employer.html', employer=employer, jobs=jobs, reviews=reviews)
	
	
@app.route('/employer/<employer_id>/review', methods=('GET', 'POST'))
def review(employer_id):
	if request.method == 'POST':
		review = request.form['review']
		rating = request.form['rating']
		title = request.form['title']
		status = request.form['status']
		
		date = datetime.datetime.now().strftime("%m/%d/%Y")
		execute_sql('INSERT INTO review (review, rating, title, date, status, employer_id) VALUES (?, ?, ?, ?, ?, ?)', (review, rating, title, date, status, employer_id), commit=True)
	
		#Redirect back to the employer page after POST of review.
		return redirect(url_for('employer', employer_id=employer_id))
	
	return render_template('review.html', employer_id=employer_id)