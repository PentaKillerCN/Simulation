from producer import produce_message
from sender import start_sender
import unittest                         # import unittest for unit testing
import zmq                              # import zmq for process communication
import multiprocessing                  # import multiprocessing for set up processes for producer and senders


class TestSystem(unittest.TestCase):
    # test produce_message by setting up a mock sender socket to receive messages from produce_message
    def test_produce_message(self):
        test_message_length = 1000
        test_num = 100
        test_producer_sender_port = '54321'

        # start produce_message
        test_process = multiprocessing.Process(target=produce_message,
                                               args=(test_producer_sender_port, test_num, test_message_length, ))
        test_process.start()

        # set up a mock sender socket to test produce_message
        context = zmq.Context()
        sender_socket = context.socket(zmq.PULL)
        sender_socket.RCVTIMEO = 1000
        sender_socket.bind("tcp://*:{}".format(test_producer_sender_port))

        # every time a message from produce_message received, count increment by one
        count = 0
        while True:
            try:
                message = sender_socket.recv()
            except zmq.error.Again:
                break

            if len(message) == test_message_length:
                count += 1

        context.destroy()

        # count should be equal to test_num to ensure produce_message sends enough messages
        self.assertEqual(
            count,
            test_num
        )

    # test start_sender by setting up a mock producer socket to send messages to senders and a mock monitor socket to
    # receive results from senders
    def test_start_sender(self):
        test_num = 20
        test_sender_settings = [
            [1, 0.5],
            [1, 0.5],
            [1, 0.5],
            [1, 0.5]
        ]
        test_num_of_sender = len(test_sender_settings)
        test_producer_sender_port = '11111'
        test_sender_monitor_port = '22222'

        # start start_sender
        context = zmq.Context()
        test_process = multiprocessing.Process(target=start_sender,
                                               args=(test_producer_sender_port, test_sender_monitor_port,
                                                     test_sender_settings, test_num_of_sender,))
        test_process.start()

        # set up a mock producer socket to test start_sender
        producer_socket = context.socket(zmq.PUSH)
        producer_socket.connect("tcp://localhost:{}".format(test_producer_sender_port))

        for i in range(test_num):
            producer_socket.send_string('Testing')

        # set up a mock monitor socket to test start_sender
        monitor_socket = context.socket(zmq.PULL)
        monitor_socket.RCVTIMEO = 5000
        monitor_socket.bind("tcp://*:{}".format(test_sender_monitor_port))

        # every time a result from a sender received, count increment by one
        count = 0
        while True:
            try:
                message = monitor_socket.recv()
            except zmq.error.Again:
                break

            results = message.decode("utf-8").split(' ')

            if results[0] == 'True' or results[0] == 'False':
                count += 1

        context.destroy()

        # count should be equal to test_num to ensure senders send enough results to monitor
        self.assertEqual(
            count,
            test_num
        )
