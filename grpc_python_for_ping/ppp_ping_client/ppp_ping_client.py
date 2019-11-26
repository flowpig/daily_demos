#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../ping_proto/mid_tool')
import grpc
import ppp_ping_pb2
import ppp_ping_pb2_grpc
import json

_HOST = '127.0.0.1'
_PORT = '19999'


def run(with_data):
    data = json.loads(with_data)
    with grpc.insecure_channel("{0}:{1}".format(_HOST, _PORT)) as channel:
        client = ppp_ping_pb2_grpc.PPPsubPingServeStub(channel=channel)
        #response = client.SubmitWillPing(ppp_ping_pb2.DoPingRequest(schema=1, users=200, hostids=[10010, 10011, 10086]))
        response = client.SubmitWillPing(ppp_ping_pb2.DoPingRequest(schema=data["schema"], users=data["users"], hostids=data["hostids"]))
    print("received: " + str(response.key))


if __name__ == '__main__':
    #mess = {"schema": 1, "users": 200, "hostids": [10010, 10011, 10086]}
    #t = json.dumps(mess)
    #print(t)
    run(sys.argv[1])    
