gui = {}
api = {}
database = {}
sniffer={}

def _setup_node_defaults():
    global gui
    gui['host'] = '0.0.0.0'
    gui['port'] = 80

    global api
    api['host'] = '0.0.0.0'
    api['port'] = 5000

    global database
    database['name'] = 'watchtower_node'
    database['host'] = 'localhost'
    database['port'] = 27017

    global sniffer
    sniffer['ifname'] = 'lo'


