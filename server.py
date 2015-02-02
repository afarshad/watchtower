from flask import Flask, request
import threading
import os
import requests
import datetime
import manager

app = Flask(__name__)

path_to_mpds = 'mpds/'
remote_host = 'http://www-itec.uni-klu.ac.at/ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/'

@app.route('/<file_>.mpd', methods=['GET'])
def request_for_mpd(file_):
	if not file_available_locally(path_to_mpds, file_+'.mpd'):
		get_file(file_+'.mpd')
	manager.parse_mpd(path_to_mpds + file_+'.mpd')


@app.route('/<file_>.m4s', methods=['GET'])
def request_for_m4s(file_):
	obj = {'date': datetime.datetime.utcnow(), 'src-ip': request.remote_addr, 'request': file_ + '.m4s'}
	manager.db_insert_get_request(obj)
	
def file_available_locally(path, file_):
	return os.path.isfile(path + file_)

def get_file(file_):
	""" This doesn't work yet, for some reason it returns HTML, rather
	than XML even when following forwards/redirects """
	if not os.path.isdir(path_to_mpds):
		os.makedirs(path_to_mpds)

	print '[getting]' + remote_host + file_
	response = request_file(remote_host, file_)

	if response.status_code == 200:
		with open(path_to_mpds + file_, "wb") as mpd_file:
			mpd_file.write(response.content)

def request_file(ip, file_):
	response = requests.get(remote_host)
	return response

class webserver_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        app.run()