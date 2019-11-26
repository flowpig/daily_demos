#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('../ping_proto/mid_tool')
import grpc
import time
from concurrent import futures
import ppp_ping_pb2
import ppp_ping_pb2_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24
_HOST = "127.0.0.1"
_PORT = "19999"

class PPPSubPing(ppp_ping_pb2_grpc.PPPsubPingServeServicer):
    def SubmitWillPing(self, request, context):
        print("request: " + str(request))
        print('%s, %s, %s' % (request.schema, request.users, request.hostids))
        return ppp_ping_pb2.DoPingReply(key=123123)

def server():
    grpcServer = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    ppp_ping_pb2_grpc.add_PPPsubPingServeServicer_to_server(PPPSubPing(), grpcServer)
    grpcServer.add_insecure_port("{0}:{1}".format(_HOST, _PORT))
    grpcServer.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        grpcServer.stop(0)


if __name__ == '__main__':
    server()
