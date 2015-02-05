import threading
import os
from node import manager
import logging
import requests
import manager
import calendar

from scapy.all import *

path_to_mpds = 'mpds/'

def packet_capture(packet):
	get_found=str()
	host=str()

	if packet.haslayer(Raw):
		load = packet[Raw].load
		try:
			headers, body = load.split(r"\r\n\r\n", 1)
		except:
			headers = load
			body = ''
		header_lines = headers.split(r"\r\n")
		for h in header_lines:
			if 'get /' in h.lower():
				get_found = h.split(' ')[1]
				src_ip = packet[IP].src
		if get_found:
			for h in header_lines:
				if 'host: ' in h.lower():
					host = h.split(":")[1].strip(" ").split("\r\n")[0]
			file_ = get_found.split('/')[-1]
			handle_get_request(src_ip, host, get_found, file_)

def handle_get_request(src_ip, host, full_path, file_):
	file_type = get_file_type(file_)

	if file_type == '.mpd':
		request_for_mpd(host, full_path, file_)
	elif file_type == '.m4s':
		request_for_m4s(src_ip, host, full_path, file_)

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
		response = requests.get('http://' + url, verify=False, allow_redirects=True, stream=True)

		if not response.ok:
			return

		for block in response.iter_content(1024):
			if not block:
				break
			handle.write(block)

def request_for_m4s(src_ip, host, full_path, file_):
	print 'request for m4s'
	obj = {'time': calendar.timegm(time.gmtime()), 'src-ip': src_ip, 'host': host, 'request': file_, 'path': full_path }
	manager.db_insert_get_request(obj)

def file_available_locally(path, file_):
	return os.path.isfile(path + file_)

class sniffing_thread(threading.Thread):
	daemon = True
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		#sniff(iface="eth2.1000", filter='tcp port 80', prn=packet_capture, store=0)
		sniff(filter='tcp port 80', prn=packet_capture, store=0)

# handle_get_request('0.0.0.0', 'http://www-itec.uni-klu.ac.at', '/ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd', 'BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd')
manager.parse_mpd(path_to_mpds + 'BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd')
request_for_m4s('0.0.0.0', 'www.google.com', 'bunny_2s_50kbit/bunny_2s10.m4s', 'bunny_2s10.m4s')
