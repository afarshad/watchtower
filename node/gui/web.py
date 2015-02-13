import threading
import time
import flot
import ConfigParser
import yaml

from flask import Flask, render_template, jsonify
from pymongo import Connection
from time import sleep

app = Flask(__name__)

@app.route('/')
def homepage():
	sessions = get_active_sessions()
	return render_template('index.html', sessions=sessions)

@app.route('/data')
def print_sessions():
	get_session_information()

def get_active_sessions():
	connection = Connection('localhost', 27017)
	db = connection['qoems']

	collections = db.collection_names(include_system_collections=False)

	connection.close()
	return collections

def get_session_information():
	connection = Connection('localhost', 27017)
	db = connection['qoems']
	sessions = get_active_sessions()

	for session in sessions:
		client = db[session]
		cursor = client.find()
		print '*'*80
		print session
		print '*'*80
		max = 0
		min = 0
		for document in cursor:
			if document['bitrate'] > max:
				max = document['bitrate']
			if document['bitrate'] < min:
				min = document['bitrate']
		print ('max: ' + str(max) + ' min:' + str(min))
			

class webserver_thread(threading.Thread):
	daemon = True
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		app.run(host="0.0.0.0")

get_session_information()
webserver = webserver_thread()
webserver.start()