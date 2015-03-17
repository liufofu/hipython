#!/usr/bin/env python
#-*- coding:utf8 -*-
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# 简要说明
# 1.多进程测试
# 2.
####################################
"""

import os

print 'Process (%s) start...' %(os.getpid())
pid=os.fork()
if pid==0:
    print "I am child process (%s) and my parent is %s." %(os.getpid(),os.getppid())
else:
    print "I (%s) just created a child process(%s)." %(os.getpid(),pid)

