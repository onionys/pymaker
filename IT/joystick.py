#!/usr/bin/env python

import serial
from time import sleep

class joystick_serial:
    joy_x1 = 0
    joy_y1 = 0
    joy_x2 = 0
    joy_y2 = 0

    def __init__(self, tty='/dev/ttyUSB0', baudrate = 9600):
        self.tty = tty
        self.baudrate = baudrate
        self.serial = serial.Serial(self.tty ,self.baudrate ,timeout = 0.1)

    def getXY(self):
        self.serial.write('J')
        res = self.serial.readline().strip().split()
        if((res.__len__() == 4)):
            try:
                return tuple([int(i) for i in res])
            except:
                pass
        return ()
        

    def close(self):
        self.serial.close()

if __name__ == '__main__':
    joy = joystick_serial()
    while(1):
        sleep(0.1)
        values = joy.getXY()
        if(values.__len__() == 4):
            print "x1:%d y1:%d x2:%d y2:%d" % joy.getXY()
        else:
            print "values error"
    joy.close()

