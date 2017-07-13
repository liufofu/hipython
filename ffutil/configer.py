# -*- coding: utf-8 -*-
'''
 author:www.liufofu.com
 email:14158286@qq.com
#######descprition################
# 规范输出配置文件读写接口
# 1、配置文件读取
# 2、配置文件修改后，自动保存
# 3、
####################################
'''
import os
import codecs

# python 3
try:
    import ConfigParser as cp
except Exception:
    import configparser as cp


class Configer():
    def __init__(self, filename):
        self.filename = filename
        # 允许value为空
        self.configparser = cp.ConfigParser(allow_no_value=True)
        self._read()

    def set(self, section='DEFAULT', name=None, value=None):
        if section != 'DEFAULT':
            if section not in self.configparser.sections():
                self.configparser.add_section(section)
        self.configparser.set(section=section, option=name, value=value)
        self._save()

    def get(self, section='DEFAULT', name=None):
        try:
            return self.configparser.get(section=section, option=name)
        except cp.NoOptionError:
            return None

    def del_key(self, section='DEFAULT', name=None):
        self.configparser.remove_option(section=section, option=name)
        self._save()

    def del_section(self, section='DEFAULT'):
        self.configparser.remove_section(section=section)
        self._save()

    def sections(self):
        return self.configparser.sections()

    def keys(self, section='DEFAULT'):
        return self.configparser.options(section)

    def _read(self):
        if os.path.exists(self.filename):
            self.configparser.readfp(codecs.open(self.filename,
                                                 "r", "utf-8"))

    def _save(self):
        with codecs.open(self.filename, "w", "utf-8") as fhd:
            self.configparser.write(fhd)

if __name__ == '__main__':
    myconfig = Configer('/root/my.cnf')
    print myconfig.get('mysqld','user')
    myconfig.del_key('mysqld','skip_name_resolve')
    myconfig.set('mysqld','skip_name_resove',None)
