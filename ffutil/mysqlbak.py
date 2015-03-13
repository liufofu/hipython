# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# mysql 备份/恢复
# 1.
# 2.
####################################
"""

import sys,os,commands,time
from optparse import OptionParser
try:
    import MySQLdb
except ImportError,e:
    print e
    sys.exit(1)


class mysqlbackup(object):
    def __init__(self,host,user,password,database,comminfo):

        self.__params=comminfo
        self.__localbakdir=self.__params["localbakdir"]
        self.__logdir=self.__params["logdir"]
        self.__mysqlbasedir=self.__params["mysqlbasedir"]
        self.__backup_status_log=self.__params["backup_status_log"]
        self.__dumpcmd=self.__params["tools"]
        self.__cfg=self.__params["cfg"]
        self.__port=self.__params["port"]
        self.__charset=self.__params["charset"]
        self.__host=host
        self.__user=user
        self.__password=password
        self.__database=database
        self.__socket=self.__params["socket"]

    def _checkmysqlconnection(self,conninfo):
        try:
            self.conn=MySQLdb.connect(
                host=self.__host,
                user=self.__user,
                passwd=self.__password,
                port=self.__port,
                db=self.__database,
                charset=self.__charset,
            )
            #print self.__host,self.__user,self.__password,self.__port,self.__database,self.__charset
            return True
        except Exception ,e:
            print "connect error %d  :  %s" %(e.args[0],e.args[1])
            return False
            sys.exit(1)
        pass
    def _mysqlbackup(self):
        curdate=time.strftime('%Y%m%d',time.localtime(time.time()))
        if self._checkargs(curdate) :
            if self._checkmysqlconnection(self.__params):
                bakcmds=self.__dumpcmd+' --defaults-file='+self.__cfg+' --host='+self.__host+' --user='+self.__user \
                +' --password='+self.__password+' -B '+self.__database+' --socket='+self.__socket \
                +' --single-transaction --opt --master-data=2 >'+os.path.join(self.__localbakdir,curdate,self.__database+'.sql')
                if os.system( bakcmds)==0:
                    print "backup successfully~"
                else:
                    print "backup faild~"
                    sys.exit(1)
            else:
                print "connect error"
        else:
            print "please check args"
            sys.exit(1)

    def _checkargs(self,curdate):
        #curdate=time.strftime('%Y%m%d',time.localtime(time.time()))
        print self.__mysqlbasedir,self.__cfg,self.__dumpcmd,self.__socket
        if not os.path.exists(os.path.join(self.__localbakdir,curdate)):
            os.makedirs(os.path.join(self.__localbakdir,curdate))
        if not os.path.isdir(self.__mysqlbasedir):
            print "Please check %s if exists." %(self.__mysqlbasedir)
            return False
        if not os.path.isfile(self.__cfg):
            print "Please check %s if exists." %(self.__cfg)
            return False
        if not os.path.isfile(self.__dumpcmd):
            print "Please check %s if exists." %(self.__dumpcmd)
            return False
        if not os.path.exists(self.__socket):
            print "Please check %s if exists." %(self.__socket)
            return False
        return True

class mysqlrestore(object):
    def __init__(self,mysqlmode="restore"):
        self.__mysqlmode=mysqlmode

    def _checkmysqlconnection(self,conninfo):
        pass

    def _mysqlrestore(self,dbname):
        print "restore"
        #commands.get/usr/local/mysql-5.6.21/bin/mysqldump -u root -S /tmp/mysql_3321.sock  liufofu > /dbbackup/liufofu.sql
        pass
   

if __name__=='__main__':
    parser=OptionParser()
    parser.add_option("--host",dest="myhost",default="localhost",help="set mysql host address")
    parser.add_option("--user",dest="myuser",default="root",help="set mysql username")
    parser.add_option("--password",dest="mypassword",default="",help="set mysql username")
    parser.add_option("--charset",dest="mycharset",default="utf8",help="set mysql connect character set ")
    parser.add_option("--port",type="int",dest="myport",default="3306",help="set mysql connect port")
    parser.add_option("--db",dest="mydbname",default="test",help="set mysql dbname")
    parser.add_option("--socket",dest="mysocket",default="/tmp/mysql.sock",help="set mysql socket")
    parser.add_option("--cfg",dest="mycfg",default="/etc/my.cnf",help="set mysql socket")
    parser.add_option("--mode",dest="mymode",default="backup",help="set mysql backup or restore")
    parser.add_option("--bakdir",dest="bakdir",default="/dbbackup",help="set mysql backup directory")
    parser.add_option("--tools",dest="baktools",default="mysqldump",help="set mysql backup/restore tools")
    (options,args)=parser.parse_args()
    comminfo={
        "bakdir":options.bakdir,
        "localbakdir":os.path.join(options.bakdir,'mysql'),
        "mysqlbasedir":"/usr/local/mysql-5.6.21/",
        "cfg":options.mycfg,
        "port":options.myport,
        "charset":options.mycharset,
        "mode":options.mymode,
        "socket":options.mysocket,
        "logdir":"/var/log/mysql",
        "tools":os.path.join("/usr/local/mysql-5.6.21/bin",options.baktools),
        "backup_status_log":os.path.join("/var/log/mysql","mysqlbak.log")
    }
    #print comminfo
    if options.mymode=='backup':
        mybk=mysqlbackup(options.myhost,options.myuser,options.mypassword,options.mydbname,comminfo)
        mybk._mysqlbackup()
    elif options.mymode=='restore':
        myre=mysqlrestore()
    else:
        print ""
        sys.exit(1)

    """
    usage:

        python mysqlbak.py --cfg=/liufofu/data/mysql_data/3320/my.cnf --host=172.24.133.5 --port=3320 --socket=/tmp/mysql_3320.sock --db=dbmonitor --user=mysqlbackup --password=mysqlbackup
    
        grant select ,show databases ,lock tables,reload ,SUPER, REPLICATION CLIENT on *.* to 'mysqlbackup'@'172.24.133.5' identified by 'mysqlbackup';

    """

