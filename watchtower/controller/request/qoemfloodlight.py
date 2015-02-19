#!/usr/bin/env python2.7

"""qoemfloodlight.py - Sends JSON-RPC commands to the Floodlight controller."""

import lib.qoemlib as lib
import httplib
import json

TAG = 'request'

class Request:

    _config = None
    _controller = None

    def __init__(self, controller):
        """Initialise redirection instance with useful objects.

        Instantiated controller and configuration objects are passed for use within this instance.

        """
        self._controller = controller

    def stop(self):
        """Stop redirection object."""
        pass

    class StaticFlowEntryPusher:
        """Represents calls made to the Floodlight's Static Flowpusher API."""

        def __init__(self, host, port):
            """Initialise object with hostname and port of Floodlight controller."""
            self.host = host
            self.port = port

        def get(self, data):
            """Send HTTP GET request to Floodlight API."""
            ret = self._rest_call({}, 'GET')
            return json.loads(ret[2])

        def set(self, data):
            """Send HTTP POST request to Floodlight API."""
            ret = self._rest_call(data, 'POST')
            return ret[0] == 200

        def remove(self,data):
            """Send HTTP DELETE request to Floodlight API."""
            ret = self._rest_call(data, 'DELETE')
            return ret[0] == 200

        def _rest_call(self, data, action):
            """Send REST call to Floodlight controller's Static Flowpusher API."""
            path = '/wm/staticflowentrypusher/json'
            headers = {
                'Content-type': 'application/json',
                'Accept': 'application/json',
                }
            body = json.dumps(data)
            conn = httplib.HTTPConnection(self.host, self.port)
            conn.request(action, path, body, headers)
            response = conn.getresponse()
            ret = (response.status, response.reason, response.read())
            conn.close()
            return ret

    class Device:
        """Represents calls made to the Floodlight's Device API."""

        def __init__(self, host, port):
            """Initialise object with hostname and port of Floodlight controller."""
            self.host = host
            self.port = port

        def get(self, data):
            """Send HTTP GET request to Floodlight API."""
            ret = self._rest_call(data, 'GET')
            result = json.loads(ret[2])
            if result != []:
                try:
                    port = str(result[0]['attachmentPoint'][0]['port'])
                    dpid = str(result[0]['attachmentPoint'][0]['switchDPID'])
                    mac = str(result[0]['mac'][0])
                except IndexError:
                    raise
                try:
                    vlan = str(result[0]['vlan'][0])
                except:
                    vlan = '-1'
                return (port, dpid, mac, vlan)
            else:
                raise KeyError

        def _rest_call(self, data, action):
            """Send REST call to Floodlight controller's Device API."""
            path = '/wm/device/?ipv4=' + data
            conn = httplib.HTTPConnection(self.host, self.port)
            conn.request('GET', path)
            response = conn.getresponse()
            ret = (response.status, response.reason, response.read())
            conn.close()
            return ret

    def add_redirect(self, expr, node_host, node_port, openflow_host, openflow_port):
        """Add a redirect for content requests matching given expression to a given node."""
        pusher = self.StaticFlowEntryPusher(openflow_host, openflow_port)
        device = self.Device(openflow_host, openflow_port)
        try:
            (_, connected_dpid, node_mac, node_vlan) = device.get(node_host)
        except KeyError:
            raise
        # TODO remove the expr from the rule, as it does not need for the QoEM purpose, we want to redirect all traffic.

        redirect_to = {
            "switch": connected_dpid,
            "name": "redirect_to-" + node_host + "-" + node_port + "-" + expr,
            "priority": "32766",
            "ether-type": 0x0800,
            "protocol": 0x06,
            "dst-ip": expr,
            "dst-port": "80",
            "vlan-id":node_vlan,
            "active": "true",
            "actions": "output=flood,"+"set-dst-mac=" + node_mac + ",set-dst-ip=" + node_host +
                ",set-dst-port=" + node_port +",output=flood"
        }

        pusher.remove({"name":"redirect_to-" + node_host + "-" + node_port + "-" + expr})
        pusher.set(redirect_to)

    def remove_redirect(self, expr, node_host, node_port, openflow_host, openflow_port):
        """Remove a redirect for content requests matching given expression to given node."""
        pusher = self.StaticFlowEntryPusher(openflow_host, openflow_port)
        pusher.remove({"name":"redirect_to-" + node_host + "-" + node_port + "-" + expr})
