#!/usr/bin/env python
from spidev import SpiDev
from time import sleep
from threading import Thread
from time import time


class MARCSTATE:
            SLEEP, IDLE, XOFF, VCOON_MC, REGON_MC, \
            MANCAL, VCOON, REGON, STARTCAL, BWBOOST, \
            FS_LOCK, IFADCON, ENDCAL, \
            RX, RX_END, RX_RST, TXRX_SWITCH, \
            RXFIFO_OVERFLOW, FSTXON, \
            TX, TX_END, \
            RXTX_SWITCH, TXFIFO_UNDERFLOW = range(23)
    

class cc2500:

    REG_MARCSTATE = 0xC0 | 0x35
    CMD_SRES = 0x30
    CMD_SFSTXON = 0x31
    CMD_SXOFF = 0x32
    CMD_XCAL = 0x33
    CMD_SRX  = 0x34
    CMD_STX  = 0x35
    CMD_SIDLE = 0x36
    CMD_SWOR = 0x38
    CMD_SPWD = 0x39
    CMD_SFRX = 0x3A
    CMD_SFTX = 0x3B
    CMD_SWORRST = 0x3C
    CMD_SNOP = 0x3D
    CMD_PATABLE = 0x3E
    CMD_TXFIFO = 0x3F

    CMD_SINGLE_WRITE = 0x00
    CMD_BRUST_WRITE = 0x40
    CMD_SINGLE_READ  = 0x80
    CMD_BRUST_READ = 0xC0



    # get Main Radio Control State Machine State
    def __init__(self, bus = 0, channel_select = 1):
        self.bus = SpiDev()
        self.bus.open(bus,channel_select)
        self.reset()
        self.buff=[]
        self.run = True
        self.timestamp = time()

    def get_STATE(self):
        return self.bus.xfer2([self.REG_MARCSTATE,0x00])[1]

    def set_reg(self,reg, byte):
        return self.bus.xfer2([reg, byte])

    def get_reg(self, reg):
        return self.bus.xfer2([0x80 | reg, 0x00])

    def info(self):
        state = self.get_STATE()
        txbyte = self.get_TXBYTES()
        rxbyte = self.get_RXBYTES()
        print "state : %d , tx: %d , rx: %d " % (state, txbyte, rxbyte)


    ## 
    ## COMMAND  
    ##
    def STX(self):
        return self.bus.xfer2([self.CMD_STX])

    def SRX(self):
        return self.bus.xfer2([self.CMD_SRX])

    def SIDLE(self):
        return self.bus.xfer2([self.CMD_SIDLE])

    def SFRX(self):
        return self.bus.xfer2([self.CMD_SFRX])
    
    def SFTX(self):
        return self.bus.xfer2([self.CMD_SFTX])

    def SRES(self):
        return self.bus.xfer2([self.CMD_SRES])

    def reset(self):
        self.SRES()
        reg_config = [0x0B, 0x2E, 0x06, 0x07, 0xD3, 0x91, 0x61, 0x04,
                      0x45, 0x00, 0x00, 0x09, 0x00, 0x5D, 0x93, 0xB1,
                      0x2D, 0x3B, 0x73, 0x22, 0xF8, 0x01, 0x07, 0x00,
                      0x18, 0x1D, 0x1C, 0xC7, 0x00, 0xB2, 0x87, 0x6B,
                      0xF8, 0xB6, 0x10, 0xEA, 0x0A, 0x00, 0x11, 0x41,
                      0x00, 0x59, 0x7F, 0x3F, 0x88, 0x31, 0x0B ]
        for reg, val in enumerate(reg_config):
            self.bus.xfer2([reg, val])
        self.SIDLE()
        self.SFRX()
        self.SFTX()



    ## FIFO buffer 64byte
    def send(self,package):
        tmp = []
        if type(package) == str:
            tmp = [ord(i) for i in package]
        else:
            tmp = list(package)
        tmp = [self.CMD_TXFIFO | self.CMD_BRUST_WRITE ,len(tmp)] + tmp
        print "send"
        print tmp
        self.bus.xfer2(tmp)    # write package to fifo buffer (max 64byte)
        if self.get_STATE() == 22:
            self.SFTX()
            self.SIDLE()
            return -1
        self.STX()
        return 0

    def get_package_RXFIFO(self):
        len_FIFO = self.get_RXBYTES()
        p_len = self.get_byte_RXFIFO()
        data = self.bus.xfer2([self.CMD_BRUST_READ | 0x3F for i in range(len_FIFO)])
        self.buff.append(data)
            
    def get_byte_RXFIFO(self):
        return self.bus.xfer2( [ self.CMD_SINGLE_READ | 0x3F , 0x00])[1]

    def set_byte_TXFIFO(self, byte):
        return self.bus.xfer2( [ self.CMD_SINGLE_WRITE | 0x3F , byte])[1]

    def get_TXBYTES(self):
        return self.bus.xfer2([0xC0 | 0x3A, 0x00])[1]

    def get_RXBYTES(self):
        return self.bus.xfer2([0xC0 | 0x3B, 0x00])[1]

    def stop(self):
        self.run = False

    def start(self):
        self.thread = Thread(target=self.receive_loop, args=())
        self.run = True
        self.thread.start()

    def receive_loop(self):
        while self.run :
            state = self.get_STATE()
            rxbytes = self.get_RXBYTES()
            txbytes = self.get_TXBYTES()

            if(state in [13,8,9,10,11]):
                #print state
                sleep(0.1)
                continue

            elif( (state == 1) and (rxbytes > 0)):
                #print state
                self.get_package_RXFIFO()
                self.SRX()

            elif(state == 1):
                #print state
                self.SIDLE()
                self.SRX()

            elif(state == 17):
                #print state
                self.SFRX()
                self.SIDLE()
                self.SRX()

            else:
                #print state
                self.reset()
                sleep(0.1)

            if time() > (self.timestamp + 10 ):
                print "reset"
                self.timestamp = time()
                self.reset()

            sleep(0.1)
            if len(self.buff) > 0:
                data = self.buff.pop(0)[1:-2]
                msg = ''.join([chr(i) for i in data])
                print(msg)

if __name__ == '__main__':
    cc = cc2500()
    cc.start()
    while True:
        sleep(0.1)
        if len(cc.buff) > 0:
            data = cc.buff.pop(0)[1:-2]
            msg = ''.join([chr(i) for i in data])
            print(msg)
