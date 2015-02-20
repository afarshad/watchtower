import sniffer
import api
import re
import os
import requests
import json
import engine

from watchtower import config
from watchtower.lib import database
from time import sleep
from mpd_parser import Parser
from session import Session
from pymongo import Connection

class Manager(object):
	db = database.open_connection()

	sessions = {}
	path_to_mpds = 'mpds/'

	def __init__(self):
		sniff = sniffer.sniffing_thread(self)
		sniff.start()

		_api = api.api_thread()
		_api.start()

		while(1):
			#self.send_data_to_engine()
			sleep(5)

	def handle_mpd_request(self, request):
		if not self.file_available_locally(self.path_to_mpds, request.file_):
			self.get_file(request.host + request.path)
		self.new_client(self.path_to_mpds + request.file_, request)

	def file_available_locally(self, path, file_):
		if not os.path.exists(path):
			os.makedirs(path)
		return os.path.isfile(path + file_)

	def get_file(self, url):
		file_ = url.split('/')[-1]

		with open(self.path_to_mpds + file_, 'wb') as handle:
			if not "http" in url:
				url = 'http://' + url
			response = requests.get(url, verify=False, allow_redirects=True, stream=True)

			if not response.ok:
				return

			for block in response.iter_content(1024):
				if not block:
					break
				handle.write(block)

	def send_data_to_engine(self):
		r = requests.get('http://' + config.api['host'] + ':' + str(config.api['port']) + '/api/sessions')
		response = json.loads(r.text)

		for session in response['sessions']:
			r = requests.get('http://' + config.api['host'] + ':' + str(config.api['port']) + '/api/sessions/' + session + '?fields=timestamp,duration,bitrate,width,height')
			entries = json.loads(r.text)
			data = []
			for entry in entries:
				for document in entries[entry]:
					data.append(document)
			engine.handle_this_method_call(data)


	def new_client(self, local_mpd, request):
		parser = Parser(local_mpd)
		mpd = parser.mpd
		session = Session(mpd, request.timestamp)
		session_identifier = str(request.src_ip) + '-' + str(request.host)
		self.sessions[session_identifier] = session

	def handle_m4s_request(self, request):
		session_identifier = str(request.src_ip) + '-' + str(request.host)
		session = self.sessions[session_identifier]

		key = request.path
		key = key.split('/')[-2] + '/' + key.split('/')[-1]

		entry = dict(request.__dict__.items() + session.mpd[key].items())
		bitrate = self.get_playback_bitrate(entry['path'])
		entry['bitrate'] = bitrate 

		client = self.db[session_identifier]
		client.insert(entry)

	def get_playback_bitrate(self, url):
		"""Parse the URL to unreliably(!) determine the playback bitrate."""
		pattern = re.compile(ur'.*\_(.*kbit).*')
		match = re.match(pattern, url)
		bitrate = int(match.group(1).replace('kbit', ''))
		return bitrate or 0