## Design of the Simulation

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; There is one producer, one monitor, and variable number of senders based on configuration. The first part is to use producer to produce random messages and send those messages to senders. The second part is to use senders to read the messages, simulate sending the messages by waiting, and send results to monitor. The third part is to use monitor to receive the results sent by the senders, process the results to collect information, and display the information collected. All the three parts run in parallel processes.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; All the senders are spawned in sub threads, and they pick up messages from producer as soon as they are idle. The rule of picking up messages is that the senders that send faster pick up more messages.

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; The communication between producer and sender is one-to-many because producer is communicating with the all the senders, and the communication between sender and monitor is many to one becasue every sender sends its results to monitor after it finishes.

## Tradeoff of the Design

### Pros

1. Because of the rule of picking up messages, the messages can be sent at the fastest speed.

2. The design is linear, easy to understand.

3. There is no single point of failure in senders because there are numbers of senders that are ready to pick up messages and do their jobs.

### Cons

1. Producer is the bottleneck of the system because it determines the data flow of messages.

2. Producer and monitor are single points of failure.

## Explanation of Implementation

1. Producer

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Producer creates random messages and sends those messages to the senders through the zmq socket.

2. Sender

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Sender has multiple threads, and each thread is a sender which is ready to receive messages from the producer through the zmq socket and does its job. After receiving messages from producer, the senders in sub threads stimulate sending the messages by waiting, and send results to monitor through the zmq socket. Each result is stored in a list where the first element represents whether the sending process fails or succeeds and the second element represents the wait time taken to send the message.

3. Monitor

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Monitor has two threads: one for displaying information collected, and the other for receiving the results from senders and processing the results into information needed to be displayed.

4. Start

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Start is the starter code for running the whole program. It first takes user inputs to configure variables needed for simulation, and then it initiates three processes for producer, sender, and monitor, respectively.


## Possible Improvement

1. Although the three processes are tightly coupled by the starter code for demonstration purpose, they can be separated and work independently.

2. A problem with Python is that it does not support multithreading because of Global Interpreter Lock, so even though I used multithreading for the senders in my code, it is pseudo multithreading. To achieve real concurrency for performance, languages like Java or C/C++ could be used for future improvement.

## Instruction to Run Program
    1. Install dependencies by typing "pipenv install"
    2. Activate virtualenv by typing "pipenv shell"
    3. Type "python3 start.py" to run the whole program
    4. Follow the instructions on the console to enter inputs to set up configuration
    5. After the configuration is set, the simulation will start

## Instruction to Run Unit Test on Program
    1. Install dependencies by typing "pipenv install"
    2. Activate virtualenv by typing "pipenv shell"
    3. Type "python3 -m unittest unit_testing" to run the unit test
