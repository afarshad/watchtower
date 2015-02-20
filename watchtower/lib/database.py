from watchtower import config
from pymongo import Connection

def open_connection():
	connection = Connection(config.database['host'], int(config.database['port']))
	return connection[config.database['name']]