import server
import mpd_parser
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
gets = db['get_requests']

if __name__ == '__main__':
	webserver = server.webserver_thread()
	webserver.start()

def parse_mpd(file):
	mpd = mpd_parser.Parser(file)
	print mpd.media

def db_insert_get_request(obj):
	gets.insert(obj)
