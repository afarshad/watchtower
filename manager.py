import server
import mpd_parser
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
mpd = {}
gets = db['get_requests']

if __name__ == '__main__':
	sniffer = server.sniffing_thread()
	sniffer.start()
	
	while(True):
		pass

def parse_mpd(file):
	global mpd
	mpd = mpd_parser.Parser(file)

def db_insert_get_request(obj):
	key = obj['full_path']
	key = key.slice('/')[-2] + '/' + key.slice('/')[-1]
	new_obj = dict(obj.items() + mpd[key].items()) 
	gets.insert(new_obj)