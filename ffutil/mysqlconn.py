# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# mysql连接类 
# 1.
# 2.
####################################
"""
import sys

try:
    import MySQLdb
except ImportError,e:
    print e
    sys.exit(1)

try:
    import MySQLdb.cursors
except ImportError,e:
    print e
    sys.exit(1)

STORE_RESULT_MODE = 0
USE_RESULT_MODE = 1

CURSOR_MODE = 0
DICTCURSOR_MODE = 1
SSCURSOR_MODE = 2
SSDICTCURSOR_MODE = 3

FETCH_ONE = 0
FETCH_MANY = 1
FETCH_ALL = 2

class mysqldb:
    conndict={"dbhost":"localhost",
        "dbuser":"root",
        "dbpasswd":"123456",
        "dbport":"3306",
        "dbname":"test",
        "dbcharset":"utf8"}
    def __init__(self,conndict):
        self.conndict=conndict
        self.myconnect(self.conndict)

    def myconnect(self,conndict):
        try:
            self.conn=MySQLdb.connect(
                host=self.conndict["dbhost"],
                user=self.conndict["dbuser"],
                passwd=self.conndict["dbpasswd"],
                port=self.conndict["dbport"],
                db=self.conndict["dbname"],
                charset=self.conndict["dbcharset"],             
            )
        except Exception ,e:
            print "connect error %d  :  %s" %(e.args[0],e.args[1])
            sys.exit()

    def query(self,sqlstr,mode=STORE_RESULT_MODE):
        if self.conn==None or self.conn.open==False:
            return -1
        self.conn.query(sqlstr)
        if mode==0:
            result=self.conn.store_result()
        elif mode==1:
            result=self.conn.use_result()
        else:
            raise Exception("mode value is wrong.")
        return (self.conn.affected_rows(),result)



    def fetch_queryresult(self,result,maxrows=1,how=0,moreinfo=False):
        if result==None:
            return None
        dataset=result.fetch_row(maxrows,how)
        if moreinfo is False:
            return  dataset
        else:
            num_fields = result.num_fields()
            num_rows = result.num_rows()
            field_flags = result.field_flags()
            info = (num_fields,num_rows,field_flags)
            return (dataset,info)



    def version(self):
        line,cur=self.execute("show variables like 'version';",mode=CURSOR_MODE)
        data=self.fetch_executeresult(cur,mode=FETCH_ONE,rows=1)
        return data[0]

    def closeconn(self):
        self.conn.close()

    def execute(self,sqlstr,args=None,mode=CURSOR_MODE,many=False):
        if mode==CURSOR_MODE:
            curclass=MySQLdb.cursors.Cursor
        elif mode==DICTCURSOR_MODE:
            curclass=MySQLdb.cursors.DictCursor
        elif mode==SSCURSOR_MODE:
            curclass=MySQLdb.cursors.SSCursor
        elif mode==SSDICTCURSOR_MODE:
            curclass=MySQLdb.cursors.SSDictCursor
        else:
            raise Exception("mode value is wrong.")
        cur=self.conn.cursor(cursorclass=curclass)
        line=0
        if many==False:
            if args==None:
                line=cur.execute(sqlstr)
            else:
                line=cur.execute(sqlstr,args)
        else:
            if args==None:
                line=cur.executemany(sqlstr)
            else:
                line=cur.executemany(sqlstr,args)
        self.conn.commit()
        return (line,cur)

    def fetch_executeresult(self,cursor,mode=FETCH_ONE,rows=1):
        if cursor==None:
            return 
        elif mode==FETCH_ONE:
            return cursor.fetchone()
        elif mode==FETCH_MANY:
            return cursor.fetchmany(rows)
        elif mode==FETCH_ALL:
            return cursor.fetchall()


if __name__=='__main__':
    from optparse import OptionParser
    parser=OptionParser()
    parser.add_option("-H","--host",dest="myhost",default="localhost",help="set mysql host address")
    parser.add_option("-u","--user",dest="myuser",default="root",help="set mysql username")
    parser.add_option("-p","--password",dest="mypassword",default="",help="set mysql password")
    parser.add_option("-c","--charset",dest="mycharset",default="utf8",help="set mysql connect character set ")
    parser.add_option("-P","--port",type="int",dest="myport",default="3306",help="set mysql connect port")
    parser.add_option("-d","--db",dest="mydbname",default="test",help="set mysql dbname")
    (options,args)=parser.parse_args()
    print "host=%s,user=%s,password=%s,charset=%s,port=%s,db=%s" %(options.myhost,options.myuser,options.mypassword,options.mycharset,options.myport,options.mydbname)
    conndict={
        "dbhost":options.myhost,
        "dbuser":options.myuser,
        "dbpasswd":options.mypassword,
        "dbport":options.myport,
        "dbname":options.mydbname,
        "dbcharset":options.mycharset
    }
    myconn=mysqldb(conndict)
    line,res=myconn.query("show variables like 'version';")
    data=myconn.fetch_queryresult(res,1,0,True)
    print "line=%d" % line
    print data

    line ,cur=myconn.execute("show variables ;",mode=DICTCURSOR_MODE)
    data=myconn.fetch_executeresult(cur,mode=FETCH_MANY,rows=20)
    print data
    line ,cur=myconn.execute("insert into student(id,username,comment) values(1,'liufofu','tiger')",mode=DICTCURSOR_MODE)
    print myconn.version()

    myconn.closeconn() 
