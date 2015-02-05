import mpd_parser
import sniffer
from time import sleep
from engine import MeasurementEngine
from pymongo import Connection

connection = Connection('localhost', 27017)
db = connection['qoems']
gets = db['get_requests']

engine = MeasurementEngine()
mpd = {}

if __name__ == '__main__':
	sniff = sniffer.sniffing_thread()
	sniff.start()
	
	while(True):
		sleep(0.1)

def parse_mpd(file):
	global mpd
	mpd = mpd_parser.Parser(file)

def db_insert_get_request(obj):
	key = obj['path']
	key = key.split('/')[-2] + '/' + key.split('/')[-1]
	new_obj = dict(obj.items() + mpd.medy[key].items())
	bitrate = engine.get_playback_bitrate(new_obj['path'])
	new_obj['bitrate'] = bitrate
	gets.insert(new_obj)