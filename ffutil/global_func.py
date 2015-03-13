# -*- coding: utf-8 -*-
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

import os,time,sys,random
import ConfigParser
import logging.config
from logging.handlers import RotatingFileHandler
import string,smtplib

def getconfig(filepath,section,key):
    cfg=ConfigParser.ConfigParser()
    cfg.read(filepath)
    return cfg.get(section,key)

def logger(logpath,level,format,backupcount,maxbytes):
    logger=logging.getLogger(logpath)
    Rthandler=RotatingFileHandler(logpath,maxBytes=maxbytes,backupCount=backupcount)
    #这里来设置日志的级别
    #CRITICAl    50
    #ERROR    40
    #WARNING    30
    #INFO    20
    #DEBUG    10
    #NOSET    0
    #写入日志时，小于指定级别的信息将被忽略
    logger.setLevel(level)
# %(levelno)s: 打印日志级别的数值
# %(levelname)s: 打印日志级别名称
# %(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]
# %(filename)s: 打印当前执行程序名
# %(funcName)s: 打印日志的当前函数
# %(lineno)d: 打印日志的当前行号
# %(asctime)s: 打印日志的时间
# %(thread)d: 打印线程ID
# %(threadName)s: 打印线程名称
# %(process)d: 打印进程ID
# %(message)s: 打印日志信息
    formatter = logging.Formatter(format)
    Rthandler.setFormatter(formatter)
    logger.addHandler(Rthandler)
    return logger


def fwrite(filename,msgtext,filemode='a+'):
    """
w      以写方式打开，覆盖原数据，这种方式打开要小心
a      以追加模式打开 (从 EOF 开始, 必要时创建新文件)
r+     以读写模式打开
w+     以读写模式打开 (参见 w )
a+     以读写模式打开 (参见 a )
rb     以二进制读模式打开
wb     以二进制写模式打开 (参见 w )
ab     以二进制追加模式打开 (参见 a )
rb+    以二进制读写模式打开 (参见 r+ )
wb+    以二进制读写模式打开 (参见 w+ )
ab+    以二进制读写模式打开 (参见 a+ )
    """
    fhd=open(filename,filemode)
    fhd.write(msgtext)
    fhd.close()

def fread(filename,filemode='r'):
    fhd=open(filename,filemode)

#    line=fhd.readline()
#    while line:
#        print line
#        line=fhd.readline()
#    fhd.close()
    return fhd


def mkrndpasswd(arylist=string.uppercase,rlen=16):
    """
     生成随机字符串，可以自定义传入列表
    """
    randpasswd=""
    arylist=list(arylist)
    i=0
    while i<rlen:
        rindex=int(random.random()*10000)%len(arylist)
        randpasswd=randpasswd+str(arylist[rindex])
        i=i+1
    return randpasswd
    

def sendmail(serverip,serverport,fromuser,frompassword,touser,msgtext):
    try:
        handle=smtplib.SMTP(serverip,serverport)
        handle.login(fromuser,frompassword)
        handle.sendmail(fromuser,touser,msgtext)
        handle.close()
        return True
    except Exception ,e:
        print e
        return False
       



if __name__=='__main__':
#    print getconfig("D:\\liufofu\\code\\python\\etc\\db.conf","database","dbuser")
    logformat=getconfig("D:\\liufofu\\code\\python\\etc\\db.conf","log","format").replace('@','%')
    loglevel=int(getconfig("D:\\liufofu\\code\\python\\etc\\db.conf","log","level"))
    logbackupcount=int(getconfig("D:\\liufofu\\code\\python\\etc\\db.conf","log","backupcount"))
    logmaxbytes=int(getconfig("D:\\liufofu\\code\\python\\etc\\db.conf","log","maxbytes"))

#    print logformat
#    print loglevel
#    print logbackupcount
#    print logmaxbytes

#    logw=logger("D:\\liufofu\\code\\python\\logs\\python.log",loglevel,logformat,logbackupcount,logmaxbytes)
#    logw.error("%(threadName)s: 打印线程名称")
#    logw.warning("%(funcName)s: 打印日志的当前函数")
#    logw.info("%(lineno)d: 打印日志的当前行号")
#    logw.critical("%(pathname)s: 打印当前执行程序的路径，其实就是sys.argv[0]")
#    
#    fwrite('D:\\liufofu\\code\\python\\etc\\xx.txt','yyy\n','a+')
#    fread('D:\\liufofu\\code\\python\\etc\\xx.txt','a+')

#    fhd=fread('D:\\liufofu\\code\\python\\etc\\xx.txt','r')
#    fileList=fhd.readlines()
#    for fileline in fileList:
#        print ">>",fileline.strip('\n')
#    fhd.close()
    rndlist=string.uppercase+string.lowercase+string.digits+string.punctuation
    print mkrndpasswd(rndlist)
    print mkrndpasswd(string.uppercase,10)
    print mkrndpasswd(string.lowercase)
    print mkrndpasswd(string.digits)
    print mkrndpasswd(string.punctuation)
    print mkrndpasswd('liufofutiger123567',6)
#
#    print "xxx%s".format("on")

    print "liufofu".capitalize()
    print "liufofu".endswith('u')
    print "liufofu".startswith('c')
    print "LIUFOFU".islower()
    print "LIUFOFU".isupper()
    print "liufofu".upper()
    print "LIUFOFU".lower()
    print "liufofu".split("f")
    print "liufofu".count("f")

    serverip=getconfig("D:\\liufofu\\code\\python\\etc\\config.cfg","smtp","smtpip")
    serverport=int(getconfig("D:\\liufofu\\code\\python\\etc\\config.cfg","smtp","smtpport"))
    fromuser=getconfig("D:\\liufofu\\code\\python\\etc\\config.cfg","smtp","smtpuser")
    frompassword=getconfig("D:\\liufofu\\code\\python\\etc\\config.cfg","smtp","smtppassword")
    touser="18960826681@189.cn"
    msgtext="Hello ,I am shenghuososo"
    if sendmail(serverip,serverport,fromuser,frompassword,touser,msgtext):
        print "Send Successfully~~"
    else:
        print "Send Failed~~"

