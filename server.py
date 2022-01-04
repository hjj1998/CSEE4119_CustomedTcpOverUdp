import codecs
import struct
import sys
import datetime
from socket import *
from Segment import Segment


class CustomServer:
    def __init__(self, dest_file, listening_port, ack_address, ack_port):
        self.dest_file = dest_file
        self.log_file = "server_log.txt"
        self.listening_port = listening_port
        self.ack_address = ack_address
        self.ack_port = ack_port

    def write_log(self, log, status, source_port, dest_port, sequence_number, ack_number, header_length, ack, fin,
                  window_size,
                  checkSum):
        content = "[" + status + " - " + "Time: " + str(datetime.datetime.now()) + " - source port: " + str(
            source_port) + \
                  " - dest port: " + str(dest_port) + " - sequence number: " + str(sequence_number) + \
                  " - ack number: " + str(ack_number) + " - header length: " + str(header_length) + \
                  " - ACK: " + str(ack) + " - FIN: " + str(fin) + " - window size: " + str(window_size) + \
                  " - checksum: " + str(checkSum) + "]\n"
        log.write(content)


# Main Method ---------------------------------------------

if __name__ == '__main__':
    # read from the command line
    try:
        dest_file = sys.argv[1]
        listening_port = int(sys.argv[2])
        ack_address = str(sys.argv[3])
        ack_port = int(sys.argv[4])

    except IndexError:
        exit(
            "Please enter as follows: python3 server.py [filename] [listening_port] [address_for_acks] [port_for_acks]")

    server = CustomServer(dest_file, listening_port, ack_address, ack_port)

    # Initiate sockets
    receiveSocket = socket(AF_INET, SOCK_DGRAM)
    receiveSocket.bind(('localhost', server.listening_port))
    ackSocket = socket(AF_INET, SOCK_DGRAM)

    # create destination file descriptor
    try:
        file = open(server.dest_file, 'w')
    except IOError:
        print("Destination file does not exist")
        receiveSocket.close()
        ackSocket.close()
        sys.exit()

    # create sever log file file descriptor
    try:
        log = open(server.log_file, 'w')
    except IOError:
        print("Server log does not exist")
        sys.exit()

    # receive segments and send ACK
    segment_handler = Segment()
    largest_inorder_sequence_number = -1
    flag = True

    while flag:
        segment, clientAddress = receiveSocket.recvfrom(2048)

        if segment:
            # Unpack the received segment
            source_port, dest_port, sequence_number, ack_number, header_length, ack, fin, window_size, checkSum, data = segment_handler.unpack_segment(
                segment)

            # Prepare to check if segment has been corrupted and received in order
            header_length = 20
            flags = (ack << 4) + fin
            urgent = 0
            raw_header = struct.pack('!HHIIBBHHH', source_port, dest_port, sequence_number, ack_number, header_length,
                                     flags, window_size, 0, urgent)
            raw_segment = raw_header + codecs.encode(data, encoding="utf-16")
            decoded_msg = codecs.decode(raw_segment, encoding="utf-16")

            # If no error introduced, then the sum should be 0xffff (65535 in decimal)
            if (segment_handler.total_2_bytes_sum(
                    decoded_msg) + checkSum == 65535 and sequence_number == largest_inorder_sequence_number + 1):
                if fin:
                    file.write(data.rstrip())
                    flag = False
                else:
                    file.write(data)

                # Send ack to client
                largest_inorder_sequence_number += 1
                ackSegment = segment_handler.make_segment(server.listening_port, server.ack_port,
                                                          largest_inorder_sequence_number,
                                                          largest_inorder_sequence_number + 1, 1, 0, window_size, "")
                ackSocket.sendto(ackSegment, (server.ack_address, server.ack_port))

                # Write server log
                server.write_log(log, "RECEIVE", source_port, dest_port, sequence_number, ack_number, header_length,
                                 ack,
                                 fin, window_size, checkSum)

                send_source_port, send_dest_port, send_sequence_number, send_ack_number, send_header_length, send_ack, send_fin, send_window_size, send_checkSum, send_data = segment_handler.unpack_segment(
                    ackSegment)
                server.write_log(log, "SEND", send_source_port, send_dest_port, send_sequence_number, send_ack_number,
                                 send_header_length, send_ack, send_fin, send_window_size, send_checkSum)

    receiveSocket.close()
    ackSocket.close()
