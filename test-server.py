#!/usr/bin/python3

import json
import etcd3

host = "10.10.1.2"
port = 2379

client = etcd3.client(host=host, port=port)
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
    print (json.dumps(json_nodedata))
else:
    print ("No available nodes found")

client.close()