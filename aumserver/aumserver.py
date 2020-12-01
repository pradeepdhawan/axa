from random import randint
import zmq
import sys
import time
import numpy as np
import logging

ACCOUNTS = ['Account1', 'Account2', 'Account3', 'Account4',
            'Account5', 'Account6', 'Account7', 'Account8',
            'Account9', 'Account10']

AUM_SERVER_INTERVAL = 30


class AUMServer:
    def __init__(self, address):
        logging.info("AUMServer {0} started. Press any key to terminate.".format(address))
        self.address = address
        self.publisher = self.register_publisher(address)

    @staticmethod
    def register_publisher(address):
        context = zmq.Context()
        publisher = context.socket(zmq.PUB)
        publisher.bind(address)
        return publisher

    def get_random_percentages(self,size):
        numbers = np.random.randint(0, 100, size=size)
        percentages = np.true_divide(numbers, numbers.sum())
        percentages = np.around(percentages * 100)
        return percentages

    def start(self):
        sleep_interval = int(AUM_SERVER_INTERVAL)
        while True:
            accounts = {}
            number_of_accounts = randint(1, len(ACCOUNTS) - 1)
            random_percentages = self.get_random_percentages(number_of_accounts)
            for i in range(0, number_of_accounts):
                account = ACCOUNTS[randint(0, len(ACCOUNTS) - 1)]
                accounts[account] = random_percentages[i]

            self.publisher.send_json(accounts)
            logging.info("AUM Server {0} in sleep for {1}".format(self.address, sleep_interval))
            time.sleep(sleep_interval)


if __name__ == "__main__":
    aumServer = AUMServer(sys.argv[1])
    aumServer.start()
