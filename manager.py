import server
import mpd_parser
from engine import Engine
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
gets = db['get_requests']
mpd = {}

if __name__ == '__main__':
	sniffer = server.sniffing_thread()
	sniffer.start()
	
	while(True):
		pass

def parse_mpd(file):
	global mpd
	mpd = mpd_parser.Parser(file)

def db_insert_get_request(obj):
	key = obj['path']
	key = key.split('/')[-2] + '/' + key.split('/')[-1]
	new_obj = dict(obj.items() + mpd.medy[key].items()) 
	gets.insert(new_obj)