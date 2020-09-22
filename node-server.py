#!/usr/bin/python3
#
# TODO - add license header snippet
# Author: PJ Waskiewicz

# get Flask and Flask Restful imported for a simple API server
from flask import Flask
from flask_restful import Api, Resource, reqparse
from ipaddress import IPv4Address, IPv4Interface
import ipaddress
import json

app = Flask(__name__)
api = Api(app)

# Define a custom serializer to handle IPv4Address and IPv4Interface objects properly
def _custom_json_encoder(self, obj):
    if isinstance(obj, ipaddress._IPAddressBase):
        return str(obj)

    return obj.__dict__

json.JSONEncoder.default = _custom_json_encoder

# TODO - pull this from etcd eventually
nodes = [
    {
            "hostname": "host1",
            "available": True,
            "network": {
                "ipaddr": IPv4Address("10.10.1.60"),
                "gateway": IPv4Address("10.10.1.1"),
                "netmask": "255.255.255.0",
                "ethernet": {
                    "mtu": 1500,
                    "fc-mode": "none"
                },
            },
            "led": {
                "blinkstick": {
                    "frontColor": 0xffff,
                    "backColor": 0xffff,
                    "blinkRate": 4
                }
            },
    },
    {
            "hostname": "host2",
            "available": True,
            "network": {
                "ipaddr": IPv4Address("10.10.1.61"),
                "gateway": IPv4Address("10.10.1.1"),
                "netmask": "255.255.255.0",
                "ethernet": {
                    "mtu": 1500,
                    "fc-mode": "none"
                },
            },
            "led": {
                "blinkstick": {
                    "frontColor": 0xffff,
                    "backColor": 0xffff,
                    "blinkRate": 4
                }
            },
    }
]

# Define the REST endpoints
class Node(Resource):
    def get(self, name):
        for node in nodes:
            if (name == node["name"]):
                return node, 200
        return "Node not found", 404

#    def post(self, name):

#    def put(self, name):

#    def delete(self, name):

class NodeList(Resource):
    def get(self):
        foo = list()
        for node in nodes:
            foo.append(node)
        return foo, 200

# Create the API resource and link it up
api.add_resource(Node, "/node/<string:name>")
api.add_resource(NodeList, "/getNodes")

app.run(debug=True)