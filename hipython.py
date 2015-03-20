#!/usr/bin/env python

from ffutil.global_func import mkrndpasswd
from ffutil.global_func import getpath
import string
import time
print "Hi,Python."
print "Hello,Man."

print "I am liuff"

print mkrndpasswd()
print mkrndpasswd(string.digits,4)
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

if 1:
    print '1'
if 0:
    print '0'
