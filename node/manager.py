import sniffer
import re

from time import sleep
from mpd_parser import Parser
from session import Session
from api import api
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']

sessions = {}

def handle_mpd_request(local_mpd, request):
	new_client(local_mpd, request)

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