#!/usr/bin/env python

import spidev

spi = spidev.SpiDev()
spi.open(0,1)
print spi.xfer2( [0x90,0x90,0x90,00,00,00] )
