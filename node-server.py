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

# TODO - should we add a global etcd client connection used by all endpoints?  Needs investigation.

# Define the REST endpoints
class Node(Resource):
    def get(self, name):
        # open the etcd target
        client = etcd3.client(host=host, port=port)

        keys = set()

        for value, metadata in client.get_all():
            keys.add(metadata.key.decode('utf-8').split('/')[2])

        for key in keys:
            value, _metadata = client.get("/hosts/" + key + "/hostdata")
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
        keys = set()

        for value, metadata in client.get_all():
            keys.add(metadata.key.decode('utf-8').split('/')[2])

        for key in keys:
            value, _metadata = client.get("/hosts/" + key + "/hostdata")
            hostdata.append(json.loads(value.decode('utf-8')))

        client.close()

        return hostdata, 200

# TODO - Add an endpoint to return a node to an available state, put perhaps?

# Get the next available node in the database.  If it's available, atomically retrieve it
# and make it unavailable.
class GetNextAvailableNode(Resource):
    # Is this a proper use of a GET operation, since we'll be modifying data?
    def get(self):
        # open the etcd target
        client = etcd3.client(host=host, port=port)

        # parse the KV store and find the first object that is available.  Use a transaction
        # operation to find one, and then mark it unavailable in the KV store.  Return that
        # node object if the transaction succeeds.
        #
        # If the transaction does not succeed, continue parsing through the KV store.  This isn't
        # the most efficient mechanism ( O(n) ), but it's simple.
        keys = set()
        for value, metadata in client.get_all():
            keys.add(metadata.key.decode('utf-8').split('/')[2])

        for key in keys:
            node_available_key = "/hosts/" + key + "/available"
            node_data_key = "/hosts/" + key + "/hostdata"

            value, _metadata = client.get(node_available_key)
            node_availability = value.decode('utf-8')

            value, _metadata = client.get(node_data_key)
            json_nodedata = json.loads(value.decode('utf-8'))

            status, resp = client.transaction(
                compare=[
                    client.transactions.value(node_available_key) == "true",
                ],
                success=[
                    client.transactions.put(node_available_key, "false"),
                ],
                failure=[],
            )

            if (status):
                break
            else:
                json_nodedata = None

        if (json_nodedata is not None):
            return json_nodedata, 200
        else:
            return "No available node found", 404

# Create the API resource and link it up
api.add_resource(Node, "/node/<string:name>")
api.add_resource(NodeList, "/getNodes")
api.add_resource(GetNextAvailableNode, "/getNextAvailableNode")

app.run(debug=True)