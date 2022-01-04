 FILE LISTS
- client.py: TCP client side that sends segments with pipelining and timeout mechanism. 
   Read from the file and sends the packets to the designated receiver. Maintain the sending window and timeout mechanism for packet corruption, disorder and loss Recovery mechanism. And update timeout interval as per the TCP protocol.
- server.py: TCP server side that receives inorder segments without buffering mechanism. 
   Receive the sender's datagram packet, check whether the delivered packets are uncorrupted and in order. Send ACK to the sender if nothing wrong with the received packets.
- Segment.py: Implement several handy utility functions in this file.   
   make_segment() is used to assemble the segment, including the header and payload; unpack_segment() is responsible for extracting each fields from the segment, and also total_2_bytes_sum() is used to calculate the total 16-bit sum of the segment. Finally, calculateCheckSum() is used for checksum fields in TCP header.
- source_file.txt: Stores t  I checked my code in my local machine (Mac OSX with Apple Silicon), however I am unsure whether my code works elsewhere, like on other OS. Beyond that the code should work as expected. Please make sure to follow the instructions that I wrote for the sample run to make sure you are running the code appropriately.he source Unicode texts to be sent by the client
- received_file.txt: Stores the Unicode texts received and then parsed by the server
- client_log.txt: Stores the client side action during transmission
- server_log.txt: Stores the server side action during transmission
__________________________________________________________________________________________________________________________________________________________
COMMAND GUIDELINE
- WARNINGS
  1. My program runs locally and I checked my code in my local machine (Mac OSX with Apple Silicon), however I am unsure whether my code works elsewhere, like on other OS's. Beyond that the code should work as expected. Please make sure to follow the instructions that I wrote for the sample run to make sure you are running the code appropriately.
  2. (IMPORTANT) My program will double the timeout interval once packet timeout occurs but I have not implemented fast retransmission. Thus, the timeout interval might be large(dozens of seconds or more if worse) if the delay is greater than 1 second, and hence the waiting time to resend packets might be very long. I have tried to reduce the time by setting a relevant small delay in emulator(like 0.3 seconds), so it could run at a relatively fast speed. (But sometimes if timeout occurs again and again, it still would take a relatively long time to successfully transmit the whole file.) 
  3. Please make sure to use Python 3 to run the program, some syntax are specific in python 3, I use python 3.9 particularly

- STEP1: start the NEWUDPL emulator
  FORMAT: ./newudpl [-i source_host:port/*] [-o dest_host:port/*] [-L random_pack_loss_rate] [-B bit_error_rate] [-O out_of_order_rate] [-d delay]
  COMMAND: ./newudpl -i 'localhost':'*' -o 'localhost':41194 -L 12 -B 3 -O 20 -d 0.3 -vv

- STEP2: Start the receiver.py with the port number that you want to use, and also other parameters:
  FORMAT: python3 [tcpserver] [file] [listening_port] [address_for_acks] [port_for_acks]
  COMMAND: python3 server.py received_file.txt 41194 localhost 40000

- STEP3: Start the client.py
  FORMAT: python3 [tcpclient] [file] [address_of_udpl] [port_number_of_udpl] [windowsize] [ack_port_number]
  COMMAND: python3 client.py source_file.txt localhost 41192 1728 40000

  BTW: The window size is measured in byte, I set MSS as 576 internally, so the window size I set in count is 3.
__________________________________________________________________________________________________________________________________________________________
POTENTIAL BUGS AND FEATURES
- BUGS
  As I said above, I have not implemented fast retransmission. Thus, the timeout interval might be large(dozens of seconds or more if worse) if the delay is greater than 1 second, and hence the waiting time to resend packets might be very long. The total transmission might varies a lot based on different values set for emulator. So I just to choose a small delay to ensure a relatively fast transmission. So please don't change the emulator options if it is not necessary to avoid too much waiting time before retransmission.
- FEATURES
  Add logging module into this program, such as the client_log.txt and server_log.txt for recording the action of client and server. It helps me to easily debugg the whole program and find the bug if there is something wrong.

__________________________________________________________________________________________________________________________________________________________