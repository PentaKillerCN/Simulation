import random  # import random for generating random strings
import string  # import string for generating random strings
import zmq  # import zmq for process communication


# produce input number of messages and send messages to senders
def produce_message(producer_sender_port, config_num=1000, config_message_length=100):
    """
    :param producer_sender_port: port address where senders communicates with producer
    :param config_num: the total number of messages to be sent
    :param config_message_length: the total length of each message
    :return: None
    """
    # set up communication between producer and senders
    context = zmq.Context()
    sender_socket = context.socket(zmq.PUSH)
    sender_socket.connect("tcp://localhost:{}".format(producer_sender_port))

    for request in range(config_num):
        # generate random messages
        message = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=config_message_length))

        # send messages to senders
        sender_socket.send_string(message)
