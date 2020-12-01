from random import randint
import zmq
import sys
import time
import logging

STOCKS = ['AXA', 'AAPL', 'GOOG', 'MSFT',
          'FB', 'AMZN', 'JNJ', 'XOM',
          'JPM', 'TSLA']


class FillServer:

    def __init__(self, address):
        logging.info("Fill Server {0} started. Press any key to terminate.".format(address))
        self.address = address
        self.publisher = self.register_publisher(address)

    @staticmethod
    def register_publisher(address):
        context = zmq.Context()
        publisher = context.socket(zmq.PUB)
        publisher.bind(address)
        return publisher

    def start(self):
        while True:
            fill = {
                'stock_ticker': STOCKS[randint(0, len(STOCKS) - 1)],
                'price': randint(1, 100),
                'quantity': randint(1, 100)
            }
            self.publisher.send_json(fill)
            sleep_interval = randint(1, 10)
            logging.info("Fill Server {0} in sleep for {1}".format(self.address, sleep_interval))
            time.sleep(sleep_interval)


if __name__ == "__main__":
    FillServer = FillServer(sys.argv[1])
    FillServer.start()
