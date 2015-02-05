#!/usr/bin/python
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

#interface = 'eth2.1000'

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
                src_IP=pkt[IP].src
        if get_found:
            for h in header_lines:
                if 'host: ' in h.lower():
                    host=h.split(":")[1].strip(" ").split("\r\n")[0]
        if get_found:
            print str(src_IP),'GET URL:',host+str(get_found)
#sniff(iface=interface, filter='tcp port 80', prn=cb, store=0)
sniff(filter='tcp port 80', prn=cb, store=0)
