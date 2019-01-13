#!/usr/bin/env python
# encoding: utf-8
"""
radioline_map/serialconn.py

*radioline_map* reads network topology from master RF-module *RAD-868-IFS* (c) by Phoenix Contact
 combines it with GeoJSON metadata and generates an interactive layer on OSM (Open Street Map).

Copyright (C) 2019 Stefan Braun


changelog:
v0.0.1, January 13th 2019 -- release v0.0.1
v0.0.0, January 06th 2019 -- preparing start of project.



This program is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License as published by the Free Software Foundation, either version 2 of the License,
or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.
If not, see <http://www.gnu.org/licenses/>.
"""

import logging
import serial
import array
from radioline_map.crc16_ifs import calc_crc



# setup of logging
# (based on tutorial https://docs.python.org/2/howto/logging.html )
# create logger =>set level to DEBUG if you want to catch all log messages!
logger = logging.getLogger('radioline_map.serialconn')
logger.setLevel(logging.DEBUG)



class Serialconn(object):
    """ serial connection to IFS-dataport of master RF-module """

    # timeout [s] for reading and writing
    SERIAL_TIMEOUT = 3.0

    # byte commands on IFS-dataport
    # with expected length of response
    # (reverse engineered: using "IO Ninja" for serial monitoring "PSI-CONF" talking to this RF modules)
    IFS_GET_RSSI = '80 04 2B 02 00 20 47 E7'
    IFS_GET_RSSI_LENGTH = 69
    IFS_GET_PARENTS = '80 04 2B 01 00 20 B7 E7'
    IFS_GET_PARENTS_LENGTH = 69


    STRING_PARENTS = 'parents'
    STRING_RSSI = 'rssi'

    def __init__(self, comport):
        self._comport = comport

    def _get_data(self, request_str, resp_length):
        """ open comport, send one request, check and return frame """

        # help from https://pyserial.readthedocs.io/en/latest/shortintro.html
        # and https://pyserial.readthedocs.io/en/latest/pyserial_api.html
        ser = serial.Serial()
        ser.port = self._comport
        ser.baudrate = 115200
        ser.bytesize = serial.EIGHTBITS
        ser.parity = serial.PARITY_EVEN
        ser.stopbits = serial.STOPBITS_ONE
        ser.timeout = Serialconn.SERIAL_TIMEOUT   # timeout for reading
        ser.xonxoff = False
        ser.rtscts = False
        ser.dsrdtr = False
        ser.write_timeout = 0

        logger.debug('Trying to open serialport "' + self._comport + '" with settings "115200,8,E,1,no flow control,timeout 5s"...')
        ser.open()

        # help from https://stackoverflow.com/questions/32018993/how-can-i-send-a-byte-array-to-a-serial-port-using-python
        data = bytearray.fromhex(request_str)
        logger.debug('Sending bytes "' + request_str + '" [total ' + str(len(data)) + ' bytes] to IFS-dataport...')
        ser.write(data)

        logger.debug('Trying to receive ' + str(resp_length) + ' bytes from IFS-dataport...')
        # read() blocks until number of bytes were received or timeout is over
        frame = ser.read(resp_length)
        if not frame:
            raise Exception('RF-module did not answer after ' + str(Serialconn.SERIAL_TIMEOUT) + ' seconds')

        # debugging: log response
        # help from https://stackoverflow.com/questions/6624453/whats-the-correct-way-to-convert-bytes-to-a-hex-string-in-python-3
        # FIXME: simple solution for printing hex numbers "AABBDD" in readable format "AA BB DD"...? :-/
        mylist = []
        for idx, char in enumerate(frame.hex()):
            mylist.append(char)
            if idx % 2 == 1:
                mylist.append(' ')
        frame_string = ''.join(mylist).strip()
        logger.debug('Received "' + frame_string + '" [total ' + str(len(frame)) + ' bytes]')

        # minimal check of received frame from attached "RAD-868-IFS"
        # frame length:
        assert len(frame) == resp_length, 'wrong frame length: expected ' + str(resp_length) + ' bytes, got ' + str(len(frame)) + ' bytes'

        # frame start:
        # help from https://stackoverflow.com/questions/16414559/how-to-use-hex-without-0x-in-python
        assert frame[0] == 0x80, 'wrong frame start character: expected "80", got "' + format(frame[0], 'x') + '"'

        # CRC over all bytes in frame:
        crc = calc_crc(frame[:-1])
        assert frame[-1] == crc, 'wrong checksum: expected "{}", got "{}"'.format(format(crc, 'x'), format(frame[-1], 'x'))

        logger.debug('Response from attached RF-module seems valid. :-)')

        # convert into array of unsigned integers
        # help from https://stackoverflow.com/questions/8461798/how-can-i-struct-unpack-many-numbers-at-once
        # and https://docs.python.org/3/library/array.html
        # (I had troubles with "struct", so I use "array" now...)
        arr = array.array('B')
        arr.frombytes(frame)
        return arr


    def get_networkstatus_list(self, subject_str):
        """ grab current network status from master module (parent-node and RSSI for every module) """

        if not subject_str in (Serialconn.STRING_PARENTS, Serialconn.STRING_RSSI):
            raise ValueError('"{}" or "{}" expected'.format(Serialconn.STRING_PARENTS, Serialconn.STRING_RSSI))

        logger.debug('Trying to retrieve ' + subject_str + ' for every slave module...')

        # =>we have to send four times the SAME request,
        #   the master RF module returns the data in parts
        if subject_str == Serialconn.STRING_PARENTS:
            request_str, resp_length = Serialconn.IFS_GET_PARENTS, Serialconn.IFS_GET_PARENTS_LENGTH
        else:
            request_str, resp_length = Serialconn.IFS_GET_RSSI, Serialconn.IFS_GET_RSSI_LENGTH

        parts_list = [None] * 4
        for x in range(4):
            arr = self._get_data(request_str=request_str,
                                 resp_length=resp_length)
            part_no = arr[3]
            parts_list[part_no] = arr[4:67]
            logger.debug('Retrieved ' + subject_str + ' part [' + str(part_no) + '/4]')

        # put together all parts for simpler handling
        # (fill index for invalid RAD-ID 0 and for master RAD-ID 1 with values same as for offline modules,
        # then index matches always the slave RAD-ID)
        if subject_str == Serialconn.STRING_PARENTS:
            offline_value = 0
        else:
            offline_value = 255
        networkstatus_list = [offline_value] * 2
        for part in parts_list:
            networkstatus_list.extend(part)

        # according to serial monitoring:
        # the raw array represents always RF modules 2 .. 250
        # =>depending on chosen RF module type and network mode not all indexes are used
        # =>the unnecessary trailing data looks always like offline modules (up to RAD-ID 250)
        # =>in our list with RAD-ID == list-index we have to cut three trailing zero-bytes
        return networkstatus_list[:-3]