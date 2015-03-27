from unittest import TestCase

__author__ = 'root'

from ffutil.ParseLog import ParseLog
import os
class TestParseLog(TestCase):
    def test_parselog(self):
        '''l
        sta.log
        -------------
        [2015-03-09 15:30:31] sta-000.bat dongfang 192.168.1.1
        [2015-03-09 15:52:33] sta-000.bat cctv8 192.168.1.3
        [2015-03-09 15:52:33] sta-000.bat cctv8 192.168.1.3
        [2015-03-09 16:01:02] sta-000.bat cctv8 192.168.1.3
        [2015-03-09 16:30:31] sta-000.bat dongfang 192.168.1.1
        :return:
        '''
        filepath=os.path.join(os.path.dirname(os.getcwd()),'data','sta.log')
        pl=ParseLog()
        pl.parselog(filepath)
