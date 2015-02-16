import threading
import os
import manager
import logging
import requests
import manager
import calendar
import sys

from time import sleep
from request import Get
from scapy.all import *

path_to_mpds = 'mpds/'

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
			get_request = Get(calendar.timegm(time.gmtime()), src_ip, host, get_found, file_)
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
	sys.stdout.write('-> handling mpd')
	if not file_available_locally(path_to_mpds, request.file_):
		get_file(request.host + request.full_path)
	manager.new_client(path_to_mpds + request.file_, request)

def get_file(url):
	file_ = url.split('/')[-1]

	with open(path_to_mpds + file_, 'wb') as handle:
		if not "http" in url:
			url = 'http://' + url
		response = requests.get(url, verify=False, allow_redirects=True, stream=True)

		if not response.ok:
			return

		for block in response.iter_content(1024):
			if not block:
				break
			handle.write(block)

def request_for_m4s(request):
	sys.stdout.write('-> handling m4s\n')
	manager.handle_m4s_request(request)

def file_available_locally(path, file_):
	return os.path.isfile(path + file_)

class sniffing_thread(threading.Thread):
	daemon = True
	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):
		try:
			# sniff(iface="eth2.1000", filter='tcp port 80', prn=packet_capture, store=0)
			sniff(filter='tcp port 80', prn=packet_capture, store=0)
		except Exception as e:
			print 'error: ' + str(e)
