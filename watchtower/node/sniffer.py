import threading
import os
import logging
import calendar
import sys
import time

import requests
from scapy.all import packet, sniff

import request

manager = None

def packet_capture(packet):
	get_found = str()
	host = str()

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
			get_request = request.Get(calendar.timegm(time.gmtime()), src_ip, host, get_found, file_)
			sys.stdout.write('[get]')
			handle_get_request(get_request)

def handle_get_request(request):
	file_type = get_file_type(request.file_)

	if file_type == '.mpd':
		sys.stdout.write('.mpd ')
		request_for_mpd(request)
	elif file_type == '.m4s':
		sys.stdout.write('.m4s ')
		request_for_m4s(request)

def get_file_type(file_):
	if file_[-4:] == '.mpd':
		return '.mpd'
	elif file_[-4:] == '.m4s':
		return '.m4s'

def request_for_mpd(request):
	sys.stdout.write('-> handling mpd\n')
	manager.handle_mpd_request(request)

def request_for_m4s(request):
	sys.stdout.write('-> handling m4s\n')
	manager.handle_m4s_request(request)

class sniffing_thread(threading.Thread):
	daemon = True
	def __init__(self, _manager):
		global manager
		manager = _manager
		#self.debug()
		threading.Thread.__init__(self)

	def run(self):
		try:
			sniff(iface="eth2.1000", filter='tcp port 80', prn=packet_capture, store=0)
		except Exception as e:
			print 'error: ' + str(e)
			sys.exit(1)

	def debug(self):
		handle_get_request(request.Get(calendar.timegm(time.gmtime()), '0.0.0.0', 'http://www-itec.uni-klu.ac.at', '/ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd', 'BigBuckBunny_2s_isoffmain_DIS_23009_1_v_2_1c2_2011_08_30.mpd'))
		handle_get_request(request.Get(calendar.timegm(time.gmtime()), '0.0.0.0', 'http://www-itec.uni-klu.ac.at', 'ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/bunny_2s_8000kbit/bunny_2s4.m4s', 'bunny_2s4.m4s'))
		time.sleep(1)
		handle_get_request(request.Get(calendar.timegm(time.gmtime()), '0.0.0.0', 'http://www-itec.uni-klu.ac.at', 'ftp/datasets/mmsys12/BigBuckBunny/bunny_2s/bunny_2s_8000kbit/bunny_2s5.m4s', 'bunny_2s4.m4s'))