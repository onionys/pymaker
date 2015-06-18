#!/usr/bin/env python

from CC2500SPI import CC2500SPI
from QC1602A_Normal_5V import qc1602a
from time import sleep

cc = CC2500SPI()
lcd = qc1602a()
lcd.lcd_init()

cc.SIDLE()
cc.SFRX()
cc.SFTX()
print "%d bytes in TXFIFO" % cc.get_TXBYTES()
print "%d bytes in RXFIFO" % cc.get_RXBYTES()

cc.receive_loop(lcd)

#while True:
#    state = cc.get_MARCSTATE()
#    if(state == 17):
#        print "srx underflow:"
#        cc.SFRX()
#        cc.SIDLE()
#        cc.SRX()
#
#    if( state == 1):
#        cc.SIDLE()
#        cc.SRX()
#        print 'goto SRX'
#
#    if( cc.get_RXBYTES() != 0):
#        #data = cc.read_byte_RXFIFO()
#        #res = cc.get_RXBYTES()
#        #print "get %d , FIFO:%d" % (data, res)
#        print cc.recv_package()
#
#    sleep(1)
