from producer import produce_message
from sender import start_sender
from monitor import start_monitor
import multiprocessing  # import multiprocessing for set up processes for producer, senders, and monitor
import numpy as np  # import numpy for statistical setup


# helper function for getting user inputs to set up configuration
def get_argument(input_message, error_message, typing, condition):
    while True:
        try:
            res = typing(input(input_message))
        except ValueError:
            print(error_message)
        else:
            if condition(res):
                print(error_message)
            else:
                break
    return res


if __name__ == "__main__":
    config_sender_settings = []     # a list of settings that denotes the wait time and failure rate for every sender
    producer_sender_port = '54321'  # port address where senders communicates with producer
    sender_monitor_port = '12345'   # port address where senders communicates with monitor

    # get parameters from user inputs

    # the total number of messages to be sent
    config_num = get_argument(
        "Enter the integer number of messages to be generated: ",
        "The number of messages should be a positive integer",
        int,
        lambda x: x <= 0
    )

    # the total length of each message
    config_message_length = get_argument(
        "Enter the integer length of each message: ",
        "The length of each message should be a positive integer",
        int,
        lambda x: x <= 0
    )

    # the maximum number of senders that can be spawned
    config_num_of_sender = get_argument(
        "Enter the integer number of senders to be created: ",
        "The number of senders should be a positive integer",
        int,
        lambda x: x <= 0
    )

    # the time interval between each display of information
    config_interval = get_argument(
        "Enter the time interval between each display in monitor: ",
        "The time interval should be a positive number",
        float,
        lambda x: x <= 0
    )

    for i in range(config_num_of_sender):
        # setting[0] : wait time according to the distribution given
        # setting[1] : configurable failure rate
        setting = []

        config_mean = get_argument(
            "Enter the mean processing time for sender {}: ".format(i + 1),
            "The mean processing time should be a positive number",
            float,
            lambda x: x <= 0
        )

        config_std = get_argument(
            "Enter the standard deviation for sender {}: ".format(i + 1),
            "The standard deviation should be a non negative number",
            float,
            lambda x: x < 0
        )

        # set up sender's wait time according to the distribution given
        wait_time = np.random.normal(config_mean, config_std)

        # since it is a distribution, it is possible that wait time is negative
        if wait_time < 0:
            wait_time = 0

        setting.append(wait_time)

        config_failure_rate = get_argument(
            "Enter the failure rate for sender {}: ".format(i + 1),
            "The failure rate should be a non negative number",
            float,
            lambda x: x < 0
        )

        setting.append(config_failure_rate)

        config_sender_settings.append(setting)

    # start producer
    producer = multiprocessing.Process(target=produce_message,
                                       args=(producer_sender_port, config_num, config_message_length, ))
    producer.start()

    # start senders
    sender = multiprocessing.Process(target=start_sender,
                                     args=(producer_sender_port, sender_monitor_port,
                                           config_sender_settings, config_num_of_sender, ))
    sender.start()

    # start monitor
    monitor = multiprocessing.Process(target=start_monitor,
                                      args=(sender_monitor_port, config_interval, ))
    monitor.start()
