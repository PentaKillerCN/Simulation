import time  # import time to use wait to simulate sending messages
import random  # import random for implementing failure rate for messages sent
import zmq  # import zmq for process communication
import threading  # import threading for multithreading


# simulate sending message by waiting
def send_message(wait_time, config_failure_rate):
    """
    :param wait_time: the wait time needed to simulate sending message
    :param config_failure_rate: the failure rate needed to simulate sending message
    :return: None
    """
    # simulate sending messages by waiting
    time.sleep(wait_time)

    if random.randint(1, 10) / 10 <= config_failure_rate:
        # handle failure
        return [False, wait_time]
    else:
        # handle success
        return [True, wait_time]


# send to monitor the results of sending messages
def send_request(results, sender_monitor_port):
    """
    :param results: the first element results[0] represents success or failure
                    the second element results[1] represents time spent sending a message
    :param sender_monitor_port: port address where senders communicates with monitor
    :return: None
    """
    # set up communication between sender and monitor
    context = zmq.Context()
    monitor_socket = context.socket(zmq.PUSH)
    monitor_socket.connect("tcp://localhost:{}".format(sender_monitor_port))

    monitor_socket.send_string(str(results[0]) + ' ' + str(results[1]))


# this is where a sender in sub thread receives messages from producer and starts doing its jobs
def receive_request(producer_socket, sender_monitor_port, wait_time, config_failure_rate):
    """
    :param producer_socket: communication socket between producer and sender
    :param sender_monitor_port: port address where senders communicates with monitor
    :param wait_time: the wait time needed to simulate sending message
    :param config_failure_rate: the failure rate needed to simulate sending message
    :return: None
    """
    while True:
        # receive messages from producer
        try:
            producer_socket.recv()
        except zmq.error.Again:
            # timeout, no more messages, and sender terminates
            return

        # simulate sending message and get results
        results = send_message(wait_time, config_failure_rate)

        # send results to monitor
        send_request(results, sender_monitor_port)


# start senders do their jobs
def start_sender(producer_sender_port, sender_monitor_port, config_sender_settings, config_num_of_sender):
    """
    :param producer_sender_port: port address where senders communicates with producer
    :param sender_monitor_port: port address where senders communicates with monitor
    :param config_sender_settings: a list of settings that denotes the wait time and failure rate for every sender
    :param config_num_of_sender: the maximum number of senders that can be spawned
    :return: None
    """
    # set up communication between producer and senders
    context = zmq.Context()
    producer_socket = context.socket(zmq.PULL)

    # set up 10 second timeout.
    # If there are no more messages received, then senders will terminate instead of waiting infinitely
    producer_socket.RCVTIMEO = 5000
    producer_socket.bind("tcp://*:{}".format(producer_sender_port))

    # spawn senders in sub threads to do their jobs
    for i in range(config_num_of_sender):
        worker = threading.Thread(target=receive_request,
                                  args=(producer_socket, sender_monitor_port,
                                        config_sender_settings[i][0], config_sender_settings[i][1],))
        worker.start()
