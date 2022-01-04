import struct
import codecs


class Segment:
    def __init__(self):
        self.header_size = 20

    def make_segment(self, sender_port, recv_port, sequence_number, ack_number, ack, fin, win_size, payload):

        header_size = self.header_size

        if fin:
            flags = 1  # flag field:0000 0001
        else:
            flags = 0  # flag field:0000 0000
        if ack:
            flags += 16 # flag field:0001 0000
        checksum = 0
        urgent = 0

        # format string: 'H' means transforming 2-byte int in python to unsigned short in C
        # 'I' means transforming 4-byte int in Python to unsigned int in C
        # 'B' means transforming 1-byte int in Python to unsigned char in C
        raw_header = struct.pack('!HHIIBBHHH', sender_port, recv_port, sequence_number, ack_number, header_size, flags,
                                 win_size, checksum, urgent)
        raw_segment = raw_header + codecs.encode(payload, encoding="utf-16")

        # calculate checksum (checksum = 0)
        decoded_msg = codecs.decode(raw_segment, encoding="UTF-16")
        checksum = self.calculateCheckSum(decoded_msg)

        # reassemble raw segment (checksum is calculated above)
        full_header = struct.pack("!HHIIBBHHH", sender_port, recv_port, sequence_number, ack_number, header_size, flags,
                                  win_size, checksum, urgent)
        full_segment = full_header + codecs.encode(payload, encoding="utf-16")

        return full_segment

    def unpack_segment(self, segment):

        header = segment[:self.header_size]
        payload = segment[self.header_size:]

        # unpack the package
        sender_port, recv_port, sequence_number, ack_number, header_size, flags, win_size, checkSum, urgent = struct.unpack(
            "!HHIIBBHHH", header)

        if (flags >> 4) == 1:
            ack = 1  # if flag = 16, then this segment will be an ACK
        else:
            ack = 0

        if int(flags % 2 == 1):
            fin = 1  # if flag = 1 or 17, then fin field will be '1'
        else:
            fin = 0

        # get the payload from the segment
        payload = codecs.decode(payload, encoding="UTF-16")
        return sender_port, recv_port, sequence_number, ack_number, header_size, ack, fin, win_size, checkSum, payload

    # calculate the total summation of 16-bit(2 bytes) values
    def total_2_bytes_sum(self, entire_segment):

        payload_len = len(entire_segment)
        # solve the problem where the length is odd
        if payload_len & 1:
            payload_len -= 1
            sum = ord(entire_segment[payload_len])
        else:
            sum = 0

        # iterate through chars two by two and sum their byte values
        while payload_len > 0:
            payload_len -= 2
            sum += (ord(entire_segment[payload_len + 1]) << 8) + ord(entire_segment[payload_len])
        # wrap overflow around
        sum = (sum >> 16) + (sum & 0xffff)
        return sum

    # calculate the checksum
    def calculateCheckSum(self, entire_segment):

        sum = self.total_2_bytes_sum(entire_segment)
        ones_complement_result = (~ sum) & 0xffff  # One's complement
        return ones_complement_result


