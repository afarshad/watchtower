import sniffer
import engine
import re

from engine import MeasurementEngine
from mpd_parser import Parser
from request import Get
from session import Session
from gui import web
from time import sleep
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']

sessions = {}

def new_client(local_mpd, request):
	parser = Parser(local_mpd)
	mpd = parser.mpd
	session = Session(mpd, request.timestamp)
	global sessions
	session_identifier = str(request.src_ip) + '-' + str(request.host)
	sessions[session_identifier] = session

def get_playback_bitrate(url):
	"""Parse the URL to unreliably(!) determine the playback bitrate."""
	pattern = re.compile(ur'.*\_(.*kbit).*')
	match = re.match(pattern, url)
	bitrate = int(match.group(1).replace('kbit', ''))
	return bitrate

def handle_m4s_request(request):
	session_identifier = str(request.src_ip) + '-' + str(request.host)
	session = sessions[session_identifier]

	key = request.path
	key = key.split('/')[-2] + '/' + key.split('/')[-1]

	entry = dict(request.__dict__.items() + session.mpd[key].items())
	bitrate = get_playback_bitrate(entry['path'])
	entry['bitrate'] = bitrate 

	client = db[session_identifier]
	client.insert(entry)

if __name__ == '__main__':
	sniff = sniffer.sniffing_thread()
	sniff.start()
	while(True):
		sleep(0.1)