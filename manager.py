import server
import mpd_parser
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
gets = db['get_requests']

if __name__ == '__main__':
	sniffer = server.sniffing_thread()
	sniffer.start()
	
	while(True):
		pass

def parse_mpd(file):
	mpd = mpd_parser.Parser(file)
	# print mpd.medy

def db_insert_get_request(obj):
	gets.insert(obj)