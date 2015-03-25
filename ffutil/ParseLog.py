# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# 解析相应的日志 
# 1.
# 2.
####################################
"""

import os,re

class ParseLog(object):
    def parselog(self,filepath):
        result={'result':None,'message':None}
        if not os.path.exists(filepath):
            result['result']='fail'
            result['message']='%s文件不存在' %(filepath)
            return result
        with open(filepath,'r') as f:
            for line in f:
                p=re.compile(r'\[(.*)\]\s+(.*)\s+(.*)\s+(.*)')
                m=p.match(line.strip('\n'))
                print m.group(1),m.group(2),m.group(3),m.group(4)

        return result
