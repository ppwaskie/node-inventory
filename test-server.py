#!/usr/bin/python3

import json
import etcd3

host = "10.10.1.2"
port = 2379

client = etcd3.client(host=host, port=port)

for value, metadata in client.get_prefix('/hosts'):
    node = metadata.key.decode('utf-8').split('/')[2]
    #print (node)
    #print("Key: " + metadata.key.decode('utf-8'))
    json_nodedata = json.loads(value.decode('utf-8'))
    print (json.dumps(json_nodedata))

client.close()