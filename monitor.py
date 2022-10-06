import time  # import time to set up interval between display of information
import zmq  # import zmq for process communication
import threading  # import threading for multithreading

# global variables
total_sent = 0               # total messages sent so far including ones with success and failure
total_fail = 0               # total messages failed so far
total_time_message = 0       # total time taken so far to sent the messages including ones with success and failure
average_time_message = 0     # average time taken so far to sent the messages including ones with success and failure
terminate = False            # flag to terminate monitor


# receive results from senders and process the results to collect information
def receive_request(sender_monitor_port):
    """
    :param sender_monitor_port: port address where senders communicates with monitor
    :return: None
    """
    # set up communication between senders and monitor
    context = zmq.Context()
    sender_socket = context.socket(zmq.PULL)

    # set up 10 second timeout.
    # If there are no more results sent from senders, then monitor will terminate instead of waiting infinitely
    sender_socket.RCVTIMEO = 5000
    sender_socket.bind("tcp://*:{}".format(sender_monitor_port))

    while True:
        global total_fail
        global total_sent
        global total_time_message
        global average_time_message
        global terminate

        # wait for next request from sender
        try:
            message = sender_socket.recv()
        except zmq.error.Again:
            # timeout, no more messages, and monitor terminates
            terminate = True
            return

        parsed_message = message.decode("utf-8").split(' ')

        status = parsed_message[0]
        process_time = parsed_message[1]

        # process results and collect information
        if status == 'False':
            total_fail += 1

        total_sent += 1
        total_time_message += float(process_time)
        average_time_message = total_time_message / total_sent


# display the information collected periodically
def display_info(config_interval):
    """
    :param config_interval: the time interval between each display of information
    :return: None
    """

    # initial state of information to be collected
    print('-------------------')
    print('Work started! Information below is the initial result:')
    print('Number of messages sent so far: ' + str(total_sent))
    print('Number of messages failed so far: ' + str(total_fail))
    print('Average time per message so far: ' + str(average_time_message))
    print('-------------------')

    begin_time = time.time()

    while not terminate:
        # track time and display information periodically
        cur_time = time.time()
        if cur_time - begin_time >= config_interval:
            print('Number of messages sent so far: ' + str(total_sent))
            print('Number of messages failed so far: ' + str(total_fail))
            print('Average time per message so far: ' + str(average_time_message))
            print('-------------------')
            begin_time = cur_time

    # final state of information to be collected
    print('Work done! Information below is the final results:')
    print('Number of messages sent so far: ' + str(total_sent))
    print('Number of messages failed so far: ' + str(total_fail))
    print('Average time per message so far: ' + str(average_time_message))


# start display worker and communicate worker to do their jobs
def start_monitor(sender_monitor_port, config_interval):
    """
    :param sender_monitor_port: port address where senders communicates with monitor
    :param config_interval: the time interval between each display of information
    :return: None
    """

    # spawn display worker to do its job
    display_worker = threading.Thread(target=display_info, args=(config_interval, ))
    display_worker.start()

    # spawn communicate worker to do its job
    communicate_worker = threading.Thread(target=receive_request, args=(sender_monitor_port, ))
    communicate_worker.start()
