import threading
import time
import flot
import ConfigParser
import yaml

from flask import Flask, render_template, jsonify
from pymongo import Connection
from time import sleep

app = Flask(__name__)
graphing_data = []

@app.route('/')
def homepage():
    return render_template('index.html', graphs=graphing_data)

@app.route('/data')
def return_graphing_data():
    get_graphing_data()
    return jsonify({'data': graphing_data})

def get_graphing_data():
    connection = Connection('localhost', 27017)
    db = connection['qoems']
    gets = db['get_requests']

    cursor = gets.find()
    temp_array = []
    for element in cursor:
        temp_array.append((element['time'], str(element['bandwidth'])))
    global graphing_data
    graphing_data = temp_array
    connection.close()

def prepare_graphing_data(buffer_):
    for metric in report[buffer_]:
        if metric not in graphs_to_display[buffer_]:
            continue
        temp_array = []
        for idx, val in enumerate(report[buffer_][metric]):
            temp_array.append((report[buffer_]['time_elapsed'][idx], report[buffer_][metric][idx]))
        graphing_data[buffer_][metric] = temp_array

class webserver_thread(threading.Thread):
    daemon = True
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        app.run()

webserver = webserver_thread()
webserver.start()
