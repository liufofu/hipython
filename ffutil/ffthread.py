#-*- coding:utf8 -*-
#!/usr/bin/env python
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# 简要说明
# 1.
# 2.
####################################
"""

import threading,time

class FFThread(threading.Thread):
    def __init__(self,num):
        threading.Thread.__init__(self)
        self._run_num=num

    def run(self):
        global count,mutex
        threadname=threading.currentThread().getName()
        for x in xrange(0,int(self._run_num)):
            mutex.acquire()
            count=count+1
            mutex.release()
            print threadname,x,count
            time.sleep(1)

if __name__=='__main__':
    global count,mutex
    threads=[]
    num=4
    count=0
    start=time.time()
    mutex=threading.Lock()
    for x in xrange(0,num):
        threads.append(FFThread(10))
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    end=time.time()

    print "Time Used: %d" %(end-start)
