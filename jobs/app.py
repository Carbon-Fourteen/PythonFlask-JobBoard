import sqlite3
from flask import Flask, render_template, g

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
	jobs = execute_sql('SELECT job.id, job.title, job.description, job.salary, employer.id as employer_id, employer.name as employer_name FROM job JOIN employer ON employer.id = job.employer_id')
	return render_template('index.html', jobs=jobs)