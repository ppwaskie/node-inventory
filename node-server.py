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
import etcd3

app = Flask(__name__)
api = Api(app)

# Define a custom serializer to handle IPv4Address and IPv4Interface objects properly
def _custom_json_encoder(self, obj):
    if isinstance(obj, ipaddress._IPAddressBase):
        return str(obj)

    return obj.__dict__

json.JSONEncoder.default = _custom_json_encoder

# etcd cluster targets, TODO - move into config file?
host = "10.10.1.2"
port = 2379

# Define the REST endpoints
class Node(Resource):
    def get(self, name):
        # open the etcd target
        client = etcd3.client(host=host, port=port)

        for value, _metadata in client.get_prefix('/hosts'):
            json_nodedata = json.loads(value.decode('utf-8'))

            if (name == json_nodedata["hostname"]):
                client.close()
                return json_nodedata, 200

        client.close()
        return "Host " + name + " not found", 404

#    def post(self, name):

#    def put(self, name):

#    def delete(self, name):

class NodeList(Resource):
    def get(self):
        # open the etcd target
        client = etcd3.client(host=host, port=port)

        hostdata = list()

        for value, _metadata in client.get_prefix('/hosts'):
            hostdata.append(json.loads(value.decode('utf-8')))

        client.close()

        return hostdata, 200

# Create the API resource and link it up
api.add_resource(Node, "/node/<string:name>")
api.add_resource(NodeList, "/getNodes")

app.run(debug=True)