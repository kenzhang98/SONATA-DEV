#!/usr/bin/python
# Initialize coloredlogs.
# import coloredlogs

# coloredlogs.install(level='ERROR', )

import os

from sonata.query_engine.sonata_queries import *
from sonata.core.runtime import Runtime
import json

if __name__ == '__main__':
    with open('/home/vagrant/dev/sonata/config.json') as json_data_file:
        data = json.load(json_data_file)

    config = data["on_server"][data["is_on_server"]]["sonata"]

    T1 = 10
    T2 = 10
    n_conns = (PacketStream(1)
               .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
               .map(keys=('ipv4.dstIP', 'ipv4.srcIP', 'tcp.sport',))
               .distinct(keys=('ipv4.dstIP', 'ipv4.srcIP', 'tcp.sport',))
               .map(keys=('ipv4.dstIP',), map_values=('count',), func=('eq', 1,))
               .reduce(keys=('ipv4.dstIP',), func=('sum',))
               .filter(filter_vals=('count',), func=('geq', T1))
               )

    n_bytes = (PacketStream(2)
               .filter(filter_keys=('ipv4.protocol',), func=('eq', 6))
               .map(keys=('ipv4.dstIP', 'ipv4.totalLen',))
               .map(keys=('ipv4.dstIP',), map_values=('ipv4.totalLen',))
               .reduce(keys=('ipv4.dstIP',), func=('sum',))
               )

    slowloris = (n_bytes.join(window='Same', new_qid=3, query=n_conns)
                 .map(map_values=('count2',), func=('div',))
                 .filter(filter_keys=('count2',), func=('geq', T2))
                 .map(keys=('ipv4.dstIP',))
                 )

    queries = [slowloris]
    config["final_plan"] = [(1, 32, 5, 1), (2, 32, 4, 1)]
    print("*********************************************************************")
    print("*                   Receiving User Queries                          *")
    print("*********************************************************************\n\n")

    runtime = Runtime(config,
                  queries,
                  os.path.dirname(os.path.realpath(__file__))
                  )