# -*- coding: utf-8 -*-
#!/usr/bin/env python
"""
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# 简要说明
# 1.re模块测试
# 2.
####################################
"""


import re

class FFre(object):
    def matchtest(self,text):
        # text = "JGood is a handsome boy, he is cool, clever, and so on..."
        m = re.match(r"(\w+)\s", text)
        if m:
            print m.group(0), '\n', m.group(1)
        else:
            print 'not match'
