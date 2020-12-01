import logging
import multiprocessing
import os
import sys
import time
import zmq

POSITION_SERVER_INTERVAL = 30


def register_receiver(addresses):
    context = zmq.Context()
    receiver = context.socket(zmq.SUB)
    receiver.setsockopt(zmq.SUBSCRIBE, b'')
    for address in addresses:
        receiver.connect(address)
    return receiver


def register_publisher(address):
    context = zmq.Context()
    publisher = context.socket(zmq.PUB)
    publisher.bind(address)
    return publisher


def process_account_message(message, unprocessed_fills, current_position):
    final_position = {}
    not_impacted = [k for k in current_position if k not in unprocessed_fills.keys()]
    for key in not_impacted:
        final_position[key] = current_position[key]
    for fill_stock_ticker, fill_quantity in unprocessed_fills.items():
        current_stock_position = {}
        if fill_stock_ticker in current_position.keys():
            current_stock_position = current_position[fill_stock_ticker]
        common_accounts = [k for k in message if k in current_stock_position.keys()]

        new_stock_position = {}
        total_ratio = 100
        last_account = list(message.keys())[-1]
        for account, ratio in message.items():
            allocated_quantity = 0
            if account in common_accounts:
                allocated_quantity = current_stock_position[account]
            total_quantity = fill_quantity + allocated_quantity
            allocated_ratio = message[account]
            deserving_quantity = round(fill_quantity * allocated_ratio // 100)
            if allocated_quantity >= deserving_quantity:
                total_ratio -= allocated_ratio
                quantity = allocated_quantity
            elif account != last_account:
                quantity = round(total_quantity * ratio // total_ratio)
                new_stock_position[account] = quantity
            else:
                quantity = total_quantity - sum(new_stock_position.values())
            current_stock_position[account] = quantity
        final_position[fill_stock_ticker] = current_stock_position
    return final_position


def process_fill_message(stock_ticker, quantity, unprocessed_fills):
    # unprocessed fills should be updated
    if stock_ticker not in unprocessed_fills.keys():
        unprocessed_fills.setdefault(stock_ticker, 0)
    unprocessed_fills[stock_ticker] = unprocessed_fills[stock_ticker] + quantity
    # pprint(unprocessed_fills)
    return unprocessed_fills


def calculate_position(message, unprocessed_fills, current_position):
    if [v for k, v in message.items() if k.startswith('Account')]:
        position = process_account_message(message, unprocessed_fills, current_position)
        fills = None
    else:
        stock_ticker = message['stock_ticker']
        quantity = message['quantity']
        fills = process_fill_message(stock_ticker, quantity, unprocessed_fills)
        position = current_position
    return fills, position


def queue_positions(position_queue, position):
    burst = []
    for stock in position.keys():
        account_dict = position[stock]
        for account, quantity in account_dict.items():
            burst.append({account: str(quantity) + " " + stock})

    position_queue.put(burst)

def process_messages(message_queue, position_queue):
    logger = multiprocessing.get_logger()
    proc = os.getpid()
    fills = {}
    position = {}
    while 1:
        try:
            if not message_queue.empty():
                message = message_queue.get()
                logger.debug(message)
                fills, position = calculate_position(message, fills, position)
                if not fills:
                    queue_positions(position_queue, position)
                    fills = {}

        except Exception as e:
            logger.error(e)
        logger.info(f"Process {proc} completed successfully")
    return True


def publish_positions(address, position_queue, interval):
    publisher = register_publisher(address)
    logger = multiprocessing.get_logger()
    can_sleep = True
    while 1:
        try:
            if not position_queue.empty():
                position = position_queue.get()
                publisher.send_json(position)
                can_sleep = True
            else:
                if can_sleep:
                    time.sleep(interval)
                    can_sleep = False
        except Exception as e:
            logger.error(e)
    return True


def start(publish_to_address, listen_to_addresses, message_queue, position_queue):
    logging.info("Controller listening to {0} servers. Press 'q' key to terminate.".format(len(listen_to_addresses)))
    logging.info("Controller publishing to {0} servers. Press 'q' key to terminate.".format(publish_to_address))
    receiver = register_receiver(listen_to_addresses)

    controller_process = multiprocessing.Process(target=process_messages,
                                                 args=(message_queue, position_queue))
    controller_process.start()

    position_process = multiprocessing.Process(target=publish_positions,
                                               args=(publish_to_address, position_queue, POSITION_SERVER_INTERVAL))
    position_process.start()
    while 1:
        message = receiver.recv_json()
        message_queue.put(message)


if __name__ == "__main__":
    '''
    current_position = {'AXA': {'Account1': 33, 'Account2': 3}, 'MSFT': {'Account1': 22, 'Account2': 2}}
    message = {'Account2': 20, 'Account3': 30, 'Account4': 50}
    fills = {'MSFT': 12, 'FB': 45, 'JPM': 20}
   
    current_position = {'AXA': {'Account1': 8, 'Account2': 12}}
    message = {'Account1': 5, 'Account2': 45, 'Account3': 50}
    fills = {'AXA': 3}
    '''
    # new_position = process_account_message(message, fills, current_position)
    '''
    final_position = {'AXA': {'Account1': 33, 'Account2': 3},
                      'MSFT': {'Account1': 22, 'Account2': 2, 'Account3': 4, 'Account4': 8},
                      'FB': {'Account2': 9, 'Account3': 13, 'Account4': 23},
                      'JPM': {'Account2': 4, 'Account3': 6, 'Account4': 10}
                     }
    '''
    multiprocessing.log_to_stderr(logging.ERROR)
    messages = multiprocessing.Queue()
    positions = multiprocessing.Queue()
    start(sys.argv[1], sys.argv[2:], messages, positions)
