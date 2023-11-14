import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

DATABASE_USERNAME = "aoo2129"
DATABASE_PASSWRD = "5194"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"

# creates database engine that connects to URI
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():

    # sets up database connection

	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):

	# closes database at end of web request

	try:
		g.conn.close()
	except Exception as e:
		pass

@app.route('/')
def index():
    # DEBUG: this is debugging code to see what request looks like
	print(request.args)

	return render_template("index.html")

# tvshows homepage
@app.route('/tvshows')
def shows():
	select_name_id_query = "SELECT name, tvshow_id FROM tvshows"
	cursor = g.conn.execute(text(select_name_id_query))
	names = []
	ids = []
	for result in cursor:
		names.append(result[0])
		ids.append(result[1])
	cursor.close

	context = dict(names=names, ids=ids, len = len(names))

	return render_template("tvshows.html", **context)

#individual tvshow
@app.route('/tvshows/<id>')
def individual_tvshow(id):
	select_name_query = "SELECT name FROM tvshows WHERE '{id}' = tvshow_id".format(id=id)
	select_streaming_query = "SELECT platform from streaming WHERE '{id}' = tvshow_id".format(id=id)
	select_genre_query = "SELECT genre FROM genre WHERE '{id}' = tvshow_id".format(id=id)

	# execute queries
	cursor = g.conn.execute(text(select_streaming_query))
	streaming = []
	for result in cursor:
		streaming.append(result[0])
	cursor.close

	name = g.conn.execute(text(select_name_query)).fetchone()[0]
	streaming = g.conn.execute(text(select_streaming_query)).fetchone()[0]
	genre = g.conn.execute(text(select_genre_query)).fetchone()[0]

	context = dict(name=name, streaming=streaming, genre=genre, id=id)
	print(name, streaming, genre)
	return render_template("indiv_tvshows.html", **context)

# episodes
@app.route('/tvshows/<id>/episode')
def episodes(id):

	# displays basic info
	select_ep_title_query = "SELECT title FROM episodes WHERE '{id}' = tvshow_id".format(id=id)
	select_synopsis_query = "SELECT synopsis FROM episodes WHERE '{id}' = tvshow_id".format(id=id)
	select_dofe_query = "SELECT date_aired FROM episodes WHERE '{id}' = tvshow_id".format(id=id)
	select_runtime_query = "SELECT runtime FROM episodes WHERE '{id}' = tvshow_id".format(id=id)

	# execute queries for basic info
	ep_title = g.conn.execute(text(select_ep_title_query)).fetchone()[0]
	synopsis = g.conn.execute(text(select_synopsis_query)).fetchone()[0]
	dofe = g.conn.execute(text(select_dofe_query)).fetchone()[0]
	runtime = g.conn.execute(text(select_runtime_query)).fetchone()[0]

	# displays reviews
	select_tvname_query = "SELECT name FROM tvshows WHERE '{id}' = tvshow_id".format(id=id)
	select_reviewid_query = "SELECT review_id FROM reviews WHERE '{id}' = tvshow_id".format(id=id)
	select_title_query = "SELECT title FROM reviews WHERE '{id}' = tvshow_id".format(id=id)
	select_user_query = """SELECT name 
	                	   FROM reviews r, users u 
						   WHERE r.user_id = u.user_id""".format(id=id)
	select_rating_query = "SELECT rating FROM reviews WHERE '{id}' = tvshow_id".format(id=id)
	select_review_query = "SELECT content FROM reviews WHERE '{id}' = tvshow_id".format(id=id)
	
	# execute queries for reviews
	tv_name = g.conn.execute(text(select_tvname_query)).fetchone()[0]
	review_id = g.conn.execute(text(select_reviewid_query)).fetchone()[0]
	title = g.conn.execute(text(select_title_query)).fetchone()[0]
	user = g.conn.execute(text(select_user_query)).fetchone()[0]
	rating = g.conn.execute(text(select_rating_query)).fetchone()[0]
	review = g.conn.execute(text(select_review_query)).fetchone()[0]

	context = dict(ep_title=ep_title, synopsis=synopsis, dofe=dofe, runtime=runtime,
		id=id, tv_name=tv_name, review_id=review_id, title=title, user=user,
		rating=rating, review=review)

	print(ep_title, synopsis, rating, dofe, runtime)
	
	return render_template("indiv_episodes.html", **context)

# collections homepage
@app.route('/collections')
def collections():
	select_name_id_query = "SELECT name, user_id, tvlist_id FROM collections"
	cursor = g.conn.execute(text(select_name_id_query))
	names = []
	users = []
	tvlist = []
	for result in cursor:
		names.append(result[0])
		users.append(result[1])
		tvlist.append(result[2])
	cursor.close

	context = dict(names=names, users=users, tvlist=tvlist, len = len(names))

	return render_template("collections.html", **context)

# individual collection
@app.route('/collections/<user>/<list>')
def individual_collection(user, list):
	select_name_query = "SELECT name FROM collections WHERE '{user}' = user_id and '{list}' = tvlist_id".format(user=user, list=list)
	select_shows_query = """SELECT t.name 
  	FROM tvshows t, tvlist l, collections c 
  	WHERE c.user_id = l.user_id and c.user_id = '{user}' 
  	and c.tvlist_id = '{list}' and 
  	l.tvshow_id = t.tvshow_id and 
  	c.tvlist_id = l.tvlist_id""".format(user=user, list=list)
	select_numshows_query = "SELECT numshows FROM collections WHERE '{user}' = user_id and '{list}' = tvlist_id".format(user=user, list=list)

	# execute queries
	cursor = g.conn.execute(text(select_shows_query))
	shows = []
	for result in cursor:
		shows.append(result[0])
	cursor.close

	name = g.conn.execute(text(select_name_query)).fetchone()[0]
	numshows = g.conn.execute(text(select_numshows_query)).fetchone()[0]

	context = dict(name=name, shows=shows, numshows=numshows)
	print(name, user, list, shows, numshows)
	return render_template("indiv_collection.html", **context)

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
		return render_template("review_error.html")
	return redirect('/reviews')
# link to another.html
@app.route('/another')
def another():
	return render_template("another.html")

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
		
        # runs the server and shows help text

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
