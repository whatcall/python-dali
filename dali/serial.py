"""Absolutely untested driver for Tridonic RS-232 PS/S

Written from the description of the SCI2 protocol in the datasheet
"""

import serial
from dali import frame

class DaliSerial(object):
    def __init__(self,port):
        self._ser = serial.Serial(port, 38400)
        # Set RTS and DTR to power the device; not sure if these are
        # the right way round, if it doesn't work try swapping them!
        self._ser.rts = True
        self._ser.dtr = False
    
    def __enter__(self):
        return self

    def __exit__(self, *vpass):
        pass

    def send(self, command):
        frame_to_send = command.frame
        if len(frame_to_send) == 16:
            control = 0x03
            data = chr(0)+frame_to_send.pack
        elif len(frame_to_send) = 24:
            control = 0x04
            data = frame_to_send.pack
        else:
            raise NotImplemented
        if command._response:
            # If command expects a response, tell the device to wait
            # up to 10ms for one and reply with "NO" if none is received
            control |= 0x20
        checksum = 0
        for b in data:
            checksum ^= b
        data = data + chr(checksum)
        self._ser.write(data)

        reply = self._ser.read(size=5)
        
        status = ord(reply[0]) & 0x07

        if command._response:
            # We expect a response, either "NO" or 8-bit data
            if status == 0x1:
                return command._response(None)
            elif status == 0x2:
                return command._response(frame.BackwardFrame(ord(reply[3])))
            else:
                return command._response(frame.BackwardFrameError(ord(reply[3])))
