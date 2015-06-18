#!/usr/bin/env python
import spidev
from time import sleep
from sys import argv

spi = spidev.SpiDev()
spi.open(0,0)

signal = 1
ch = 1
cmd = (signal << 7 ) + (ch << 4)
print bin(cmd)
print spi.xfer2([0x01,cmd,0x00])

class MCP3008:

    def __init__(self,spi_bus = 0,channel_select = 0):
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, channel_select)

    def readChVal_signal(self, channel):
        cmd = (1 << 7) + (channel << 4)
        vals = spi.xfer2([0x01, cmd, 0x00])
        return ((vals[1] & 0b00000011 ) << 8) + vals[2]


if __name__ == '__main__':
    mcp = MCP3008()
    while(True):
        sleep(0.5)
        voltages = []
        for ch in range(8):
            voltages.append(mcp.readChVal_signal(ch))
        print ' '.join([str(i) for i in voltages])
