from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing
import datetime
import ampelControl
import sqlite3
from threading import Thread
import time

DATABASE = 'database/morsecodes.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


app = Flask(__name__)
#app.config.from_envvar('SETTINGS',silent=True)
app.config.from_object(__name__)

@app.route("/")
def hello():
    return render_template("index.html",date=datetime.datetime.now(),
     morsecodes=morsecodeQuery())


@app.route("/switch",methods=['POST'])
def switchLight():
	if request.form['state'] == "green":
		ampelControl.switchOn("green")
		ampelControl.switchOff("red")
	else:
		ampelControl.switchOn("red")
		ampelControl.switchOff("green")
	return "ok"

@app.route('/morse')
def getMorseCodes():
	info = morsecodeQuery()
	if info is None:
	    print 'error in database'
	else:
	    print info
	return "ok"

@app.route('/morseStop',methods=['POST'])
def morseStop():
	return "ok"

	
@app.route('/morseStart',methods=['POST'])
def startMorseCode():
	playID = request.form['playerID']
	morsecode = query_db("select morsecode,duration from entries where id=?",[playID],False)
	print morsecode
	morse_thread = Thread(target=playMorseCode, args = (morsecode[0][0],))
	morse_thread.start()
	return str(morsecode[0][1]) #duration

def playMorseCode(morsecode):
	for signal in morsecode:
		if signal == ".":
			print "short"
			time.sleep(0.5)
			#ampelControl.morseShort()
		else:
			print "long"
			time.sleep(1.5)
			#ampelControl.morseLong()


def morsecodeQuery():
	return query_db('select * from entries',[], one=False)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())


@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
	g.db.row_factory = sqlite3.Row
	cur = g.db.execute(query, args)
	rv = cur.fetchall()
	cur.close()
	return (rv[0] if rv else None) if one else rv


if __name__ == "__main__":

	app.debug = True
	app.run(host='0.0.0.0')
	#init_db()