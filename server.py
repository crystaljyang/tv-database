
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "aoo2129"
DATABASE_PASSWRD = "5194"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.

	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
	"""
	request is a special object that Flask provides to access web request information:

	request.method:   "GET" or "POST"
	request.form:     if the browser submitted a form, this contains the data in the form
	request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

	See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
	"""

	# DEBUG: this is debugging code to see what request looks like
	print(request.args)

	#
	# Flask uses Jinja templates, which is an extension to HTML where you can
	# pass data to a template and dynamically generate HTML based on the data
	# (you can think of it as simple PHP)
	# documentation: https://realpython.com/primer-on-jinja-templating/
	#
	# You can see an example template in templates/index.html
	#
	# context are the variables that are passed to the template.
	# for example, "data" key in the context variable defined below will be 
	# accessible as a variable in index.html:
	#
	#     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
	#     <div>{{data}}</div>
	#     
	#     # creates a <div> tag for each element in data
	#     # will print: 
	#     #
	#     #   <div>grace hopper</div>
	#     #   <div>alan turing</div>
	#     #   <div>ada lovelace</div>
	#     #
	#     {% for n in data %}
	#     <div>{{n}}</div>
	#     {% endfor %}
	#

	#
	# render_template looks in the templates/ folder for files.
	# for example, the below file reads template/index.html
	#
	return render_template("index.html")

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

# actor homepage
@app.route('/actors')
def actors():
	select_name_id_query = "SELECT name, actor_id FROM actors"
	cursor = g.conn.execute(text(select_name_id_query))
	names = []
	ids = []
	for result in cursor:
		names.append(result[0])
		ids.append(result[1])
	cursor.close

	context = dict(names=names, ids=ids, len = len(names))

	return render_template("actors.html", **context)

#individual actor
@app.route('/actors/<id>')
def individual_actor(id):
	select_name_query = "SELECT name FROM actors WHERE '{id}' = actor_id".format(id=id)
	select_shows_query = """SELECT name
						 FROM tvshows t, actedin a
						 WHERE '{id}' = a.actor_id and t.tvshow_id = a.tvshow_id""".format(id=id)
	select_dob_query = "SELECT dob FROM actors WHERE '{id}' = actor_id".format(id=id)
	select_numworks_query = "SELECT numworks FROM actors WHERE '{id}' = actor_id".format(id=id)
	
	# Execute queries
	cursor = g.conn.execute(text(select_shows_query))
	shows = []
	for result in cursor:
		shows.append(result[0])
	cursor.close
	
	name = g.conn.execute(text(select_name_query)).fetchone()[0]
	dob = g.conn.execute(text(select_dob_query)).fetchone()[0]
	numworks = g.conn.execute(text(select_numworks_query)).fetchone()[0]

	context = dict(name=name, shows=shows, dob=dob, numworks=numworks)
	print(name, dob, numworks)
	return render_template("indiv_direct.html", **context)

# director homepage
@app.route('/directors')
def directors():
	select_name_id_query = "SELECT name, director_id FROM directors"
	cursor = g.conn.execute(text(select_name_id_query))
	names = []
	ids = []
	for result in cursor:
		names.append(result[0])
		ids.append(result[1])
	cursor.close

	context = dict(names=names, ids=ids, len = len(names))

	return render_template("directors.html", **context)

#individual director
@app.route('/directors/<id>')
def individual_director(id):
	select_name_query = "SELECT name FROM directors WHERE '{id}' = director_id".format(id=id)
	select_shows_query = """SELECT name
						 FROM tvshows t, directedby d
						 WHERE '{id}' = d.director_id and t.tvshow_id = d.tvshow_id""".format(id=id)
	select_dob_query = "SELECT dob FROM directors WHERE '{id}' = director_id".format(id=id)
	select_numworks_query = "SELECT numworks FROM directors WHERE '{id}' = director_id".format(id=id)
	
	# Execute queries
	cursor = g.conn.execute(text(select_shows_query))
	shows = []
	for result in cursor:
		shows.append(result[0])
	cursor.close
	
	name = g.conn.execute(text(select_name_query)).fetchone()[0]
	dob = g.conn.execute(text(select_dob_query)).fetchone()[0]
	numworks = g.conn.execute(text(select_numworks_query)).fetchone()[0]

	context = dict(name=name, shows=shows, dob=dob, numworks=numworks)
	print(name, dob, numworks)
	return render_template("indiv_direct.html", **context)

# reviews homepage
@app.route('/reviews')
def reviews():
	select_tvid_query = "SELECT tvshow_id FROM tvshows"
	select_tvname_query = "SELECT tvshow_id, name FROM tvshows"
	select_reviewid_query = "SELECT review_id FROM reviews"
	select_title_query = "SELECT review_id, title FROM reviews"
	select_review_to_tvid = "SELECT review_id, tvshow_id FROM reviews"
	select_user_query = """SELECT review_id, name
						   FROM reviews r, users u
						   WHERE r.user_id = u.user_id"""
	select_rating_query = "SELECT review_id, rating FROM reviews"
	select_episode_query = """SELECT review_id, e.title
						   FROM reviews r, episodes e
						   WHERE r.episode_id = e.episode_id and
						   e.tvshow_id = r.tvshow_id"""
	select_review_query = "SELECT review_id, content FROM reviews"

	# Execute queries
	cursor = g.conn.execute(text(select_tvid_query))
	tv_id = []
	for result in cursor:
		tv_id.append(result[0])
	cursor.close
	cursor = g.conn.execute(text(select_tvname_query))
	tv_name = {}
	for result in cursor:
		tv_name[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_reviewid_query))
	review_id = []
	for result in cursor:
		review_id.append(result[0])
	cursor.close
	cursor = g.conn.execute(text(select_title_query))
	title = {}
	for result in cursor:
		title[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_review_to_tvid))
	review_to_tvid = {}
	for result in cursor:
		review_to_tvid[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_user_query))
	user = {}
	for result in cursor:
		user[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_rating_query))
	rating = {}
	for result in cursor:
		rating[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_episode_query))
	episode = {}
	for result in cursor:
		episode[result[0]] = result[1]
	cursor.close
	cursor = g.conn.execute(text(select_review_query))
	review = {}
	for result in cursor:
		review[result[0]] = result[1]
	cursor.close

	context = dict(tv_id=tv_id, tv_name=tv_name, review_id=review_id,title=title, user=user,
		rating=rating, episode=episode, review=review, review_to_tvid=review_to_tvid)

	return render_template("reviews.html", **context)

@app.route('/submit_review')
def submit_review():

	select_tvshowid_name = "SELECT tvshow_id, name FROM tvshows"
	select_tvid_query = "SELECT tvshow_id FROM tvshows"

	cursor = g.conn.execute(text(select_tvshowid_name))
	id_to_name = {} # dict of tvshow_id -> tvshow name
	for result in cursor:
		id_to_name[result[0]] = result[1]
	cursor.close

	cursor = g.conn.execute(text(select_tvid_query))
	tv_id = [] # list of tvshow_id
	for result in cursor:
		tv_id.append(result[0])
	cursor.close

	context = dict(id_to_name=id_to_name, tv_id=tv_id)
	return render_template("submit_review.html", **context)

# adds data to reviews database
@app.route('/submit', methods=['POST'])
def submit():

	params = {}
	params["review_id"] = request.form['id']
	params["user_id"] = request.form['user']
	params["tvshow_id"] = request.form['tvshow']
	params["episode_id"] = request.form['episode']
	params["rating"] = request.form['rating']
	params["title"] = request.form['title']
	params["content"] = request.form['content']

	insert_query = """INSERT INTO reviews VALUES
					  (:review_id, :user_id, :tvshow_id, :rating, :title, 
					  :content, :episode_id)"""
	try:
		g.conn.execute(text(insert_query), params)
		g.conn.commit()
	except:
		print("Error!")
	return redirect('/reviews')
	

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
	# accessing form inputs from user
	name = request.form['name']
	
	# passing params in for each variable into query
	params = {}
	params["new_name"] = name
	g.conn.execute(text('INSERT INTO test(name) VALUES (:new_name)'), params)
	g.conn.commit()
	return redirect('/')


@app.route('/login')
def login():
	abort(401)
	this_is_never_executed()


if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:

			python server.py

		Show the help text using:

			python server.py --help

		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
