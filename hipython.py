#!/usr/bin/env python

from ffutil.global_func import mkrndpasswd
from ffutil.global_func import getpath
import time
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

start=time.time()
time.sleep(1)
end=time.time()
print end-start

print time.ctime()
print time.localtime()
print time.mktime(time.localtime())
