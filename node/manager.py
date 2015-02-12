import sniffer

from mpd_parser import Parser
from request import Get
from session import Session
from gui import web
from time import sleep
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
gets = db['get_requests']

sessions = {}

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
	key = key.split('/')[-2] + '/' +key.split('/')[-1]

	print session.mpd[key]
	# key = obj['path']
	# key = key.split('/')[-2] + '/' + key.split('/')[-1]
	# new_obj = dict(obj.items() + mpd.mpd[key].items())
	# bitrate = engine.get_playback_bitrate(new_obj['path'])
	# new_obj['bitrate'] = bitrate
	# gets.insert(new_obj)

if __name__ == '__main__':
	sniff = sniffer.sniffing_thread()
	sniff.start()
	
	while(True):
		sleep(0.1)