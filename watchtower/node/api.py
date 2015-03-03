import threading

import pymongo
from bson.json_util import dumps
from flask import Flask, url_for, jsonify, request

from watchtower import config
from watchtower.lib import database

app = Flask(__name__)
db = database.open_connection()

@app.route('/')
def api_root():
	return 'Welcome'

@app.route('/api/sessions')
def api_sessions():
	collections = get_collections()
	return jsonify(sessions=collections)

@app.route('/api/sessions/<path:id_>')
def api_specific_sessions(id_):
	sessions = set(id_.split(','))

	projection = {'_id': 0}
	fields = request.args.get('fields')
	if fields:
		fields = fields.split(',')
		for field in fields:
			projection[field] = 1

	most_recent = request.args.get('mostRecent')
	if most_recent:
		limit = 1
		sort_order = pymongo.DESCENDING
	else:
		limit = 0
		sort_order = pymongo.ASCENDING

	collections = get_collections()

	response = {}
	for session in sessions:
		if session in collections:
			response[session] = list()
			client = db[session]
			print request.args
			for document in client.find({}, projection, limit=limit).sort('timestamp', sort_order):
				response[session].append(document)

	return dumps(response)

def get_collections():
	return db.collection_names(include_system_collections=False)

class api_thread(threading.Thread):
	daemon = True
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		app.run(host=config.api['host'], port=config.api['port'])