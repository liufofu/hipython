#!/usr/bin/env python

from ffutil.global_func import mkrndpasswd
from ffutil.global_func import getpath
print "Hi,Python."
print "Hello,Man."

print "I am liuff"

print mkrndpasswd()
print getpath()

print __file__

ipaddr='%192.168.181.15'
if ipaddr.startswith('%'):
    print "x"
elif ipaddr.startswith('1'):
    print 'y'

else:
    print 'z'