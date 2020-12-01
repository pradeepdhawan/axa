import sys
from datetime import datetime
from pprint import pprint
import zmq


class PositionServer:

    def __init__(self, address):
        print("Position server {0} started.".format(address))
        self.receiver = self.register_receiver(address)

    @staticmethod
    def register_receiver(address):
        context = zmq.Context()
        receiver = context.socket(zmq.SUB)
        receiver.setsockopt(zmq.SUBSCRIBE, b'')
        receiver.connect(address)
        return receiver

    def start(self):

        while 1:
            message = self.receiver.recv_json()
            print("Position Server received at {0}:".format(datetime.now()))
            pprint(message)


if __name__ == "__main__":
    PositionServer = PositionServer(sys.argv[1])
    PositionServer.start()
