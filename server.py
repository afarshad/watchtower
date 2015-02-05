import threading
import os
import logging
import requests
import datetime
import manager

from scapy.all import *

path_to_mpds = 'mpds/'
remote_host = 'http://www-itec.uni-klu.ac.at/ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/'

def cb(pkt):
	get_found=str()
	host=str()

	if pkt.haslayer(Raw):
		load = pkt[Raw].load
		try:
			headers, body = load.split(r"\r\n\r\n", 1)
		except:
			headers = load
			body = ''
		header_lines = headers.split(r"\r\n")
		for h in header_lines:
			if 'get /' in h.lower():
				get_found = h.split(' ')[1]
		if get_found:
			for h in header_lines:
				if 'host: ' in h.lower():
					host = h.split(":")[1].strip(" ").split("\r\n")[0]
			handle_get_request(host, get_found)

def handle_get_request(host, get):
	get_split = get.split('/')
	file_type = get_file_type(get_split[-1])

	if file_type == '.mpd':
		request_for_mpd(host, get, get_split[-1])
	elif file_type == '.m4s':
		pass

def get_file_type(file_):
	if file_[-4:] == '.mpd':
		return '.mpd'
	elif file_[-4:] == '.m4s':
		return '.m4s'

def request_for_mpd(host, full_path, file_):
	if not file_available_locally(path_to_mpds, file_):
		get_file(host + full_path)
	manager.parse_mpd(path_to_mpds + file_)

def get_file(url):
	file_ = url.split('/')[-1]	

	with open(path_to_mpds + file_, 'wb') as handle:
		response = requests.get(url, verify=False, allow_redirects=True, stream=True)

		if not response.ok:
			return

		for block in response.iter_content(1024):
			if not block:
				break
			handle.write(block)

def request_for_m4s(file_):
	print 'request for m4s'
	obj = {'date': datetime.datetime.utcnow(), 'src-ip': request.remote_addr, 'request': file_ + '.m4s'}
	manager.db_insert_get_request(obj)

def file_available_locally(path, file_):
	return os.path.isfile(path + file_)

class sniffing_thread(threading.Thread):
	daemon = True
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		sniff(filter='tcp port 80', prn=cb, store=0)

#handle_get_request('http://www-itec.uni-klu.ac.at', '/ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd')