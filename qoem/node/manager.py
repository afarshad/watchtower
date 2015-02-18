import sniffer
import re
import os
import requests
from time import sleep
from mpd_parser import Parser
from session import Session
from api import api
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']

sessions = {}
path_to_mpds = 'mpds/'

def handle_mpd_request(request):
	if not file_available_locally(path_to_mpds, request.file_):
		get_file(request.host + request.path)
	new_client(path_to_mpds + request.file_, request)

def file_available_locally(path, file_):
	if not os.path.exists(path):
		os.makedirs(path)
	return os.path.isfile(path + file_)

def get_file(url):
	file_ = url.split('/')[-1]

	with open(path_to_mpds + file_, 'wb') as handle:
		if not "http" in url:
			url = 'http://' + url
		response = requests.get(url, verify=False, allow_redirects=True, stream=True)

		if not response.ok:
			return

		for block in response.iter_content(1024):
			if not block:
				break
			handle.write(block)

def new_client(local_mpd, request):
	parser = Parser(local_mpd)
	mpd = parser.mpd
	session = Session(mpd, request.timestamp)
	global sessions
	session_identifier = str(request.src_ip) + '-' + str(request.host)
	sessions[session_identifier] = session

def handle_m4s_request(request):
	session_identifier = str(request.src_ip) + '-' + str(request.host)
	session = sessions[session_identifier]

	key = request.path
	key = key.split('/')[-2] + '/' + key.split('/')[-1]

	entry = dict(request.__dict__.items() + session.mpd[key].items())
	# bitrate = get_playback_bitrate(entry['path'])
	# entry['bitrate'] = bitrate 

	client = db[session_identifier]
	client.insert(entry)


if __name__ == '__main__':
	sniff = sniffer.sniffing_thread()
	sniff.start()

	while(1):
		sleep(0.1)