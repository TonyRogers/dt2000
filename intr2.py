#!/usr/bin/env python
from __future__ import print_function
from binascii import hexlify
from binascii import b2a_qp
import pigpio
import signal
import sys

def handler(signum,frame):
  #print 'You pressed CTRL+C! Exiting...'
  pi.bb_serial_read_close(RXD)
  pi.stop()
  sys.exit(0)

TXD=24
RXD=23

pi = pigpio.pi()
#print "pigpio Connected!"

pi.set_mode(TXD, pigpio.OUTPUT)
pi.bb_serial_read_close(RXD)
status = pi.bb_serial_read_open(RXD, 4800)
status = pi.bb_serial_invert(RXD, 1)
signal.signal(signal.SIGINT, handler)

count = 0
while True:
  while count == 0:
    (count, data) = pi.bb_serial_read(RXD)
  print (hexlify(data), sep='', end='')
  sys.stdout.flush()
  count = 0
#  print 'x'.join(format(x, '02x') for x in data),
#  for char in data:
#    print '%(c)02x' % ("c": char}
#    #sys.stdout.write(chr(char))
#    sys.stdout.write((char))
#  print "Count was: " + str(count)
#print "Done\n"

status = pi.bb_serial_read_close(23)
pi.stop
