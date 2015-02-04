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
                    host=h.split(":")[1].strip(" ").split("\r\n")[0]
        if get_found:
            print 'URL:'str(get_found)

def request_for_mpd(file_):
	print 'request for mpd'
	if not file_available_locally(path_to_mpds, file_+'.mpd'):
		get_file(file_+'.mpd')
	manager.parse_mpd(path_to_mpds + file_+'.mpd')

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