#-*- encoding:utf-8 -*-
'''
author: qiueer
date: 20161217
'''

import ConfigParser
import traceback
from lib.base.scolor import scolor
from lib.base.sstr import sstr

class conf_helper(ConfigParser.SafeConfigParser):
    
    def __init__(self, conffile, key_map=dict(), key_order=[], max_key_len=12):
        #super(BUpConfig,self).__init__()
        ConfigParser.SafeConfigParser.__init__(self)
        self._conffile = conffile
        self._key_map = key_map if key_map else dict()
        self._key_order = key_order if key_order else []
        self._max_key_len = max_key_len
        self.read(self._conffile)
        
    def get_section_dict(self, section):
        if self.has_section(section) == False: return dict()
        items = self.items(section)
        conf = dict()
        for k,v in items:
            conf[k] = v
        return conf
    
    def save(self):
        self.write(open(self._conffile, "w"))
            
    def list_one(self, section):
        if self.has_section(section) == False:return False
        shper = sstr()
        conf = self.get_section_dict(section)
        scolor.info("################# [ section: %s ]" % (section))
        keymap = self._key_map
        max_key_len = self._max_key_len if self._max_key_len else 12
        for k in self._key_order:
            key_cn = keymap.get(k, "None")
            val = conf.get(k, None)
            print shper.str_rpad(key_cn, width=max_key_len) + ": " + str(val)

    def list(self):
        sections = self.sections()
        for sec in sections:
            self.list_one(sec)
    
    def delete(self, section, tip=""):
        if self.has_section(section) == False:
            scolor.warn(u"SECTION不存在: %s"%(section))
            return False
        self.list_one(section)

        try:
            while True:
                resp = raw_input(u"是否确认删除SECTION为:%s的配置? (y or n) " % (section))
                if str(resp).strip().lower() in ["n","no"]:
                    break
                elif str(resp).strip().lower() in ["y","yes"]:
                    self.remove_section(section)
                    self.save()
                    break
        except:
            pass
        
    def modify(self, section):
        if self.has_section(section) == False:
            scolor.info("SECTION不存在: %s"%(section))
            return
        self.list_one(section)
    
        try:
            keymap = self._key_map
            val_map = dict()
            for k in self._key_order:
                key_cn = keymap.get(k, "None")
                val_map[k] = raw_input(key_cn+": ")
            while True:
                resp = raw_input(u"是否确认修改? (y or n) ")
                if str(resp).strip().lower() in ["n","no"]:
                    break
                elif str(resp).strip().lower() in ["y","yes"]:
                    for k in self._key_order:
                        if val_map[k]:self.set(section, k, val_map[k])
                    self.save()
                    break
        except:
            print traceback.format_exc()

    def add(self):
        try:
            section = raw_input(u"SECTION名(英文唯一标识): ")
            
            if self.has_section(section) == True:
                scolor.error("SECTION名已存在: %s"%(section))
                self.list_one(section)
                return False
                
            keymap = self._key_map
            val_map = dict()
            for k in self._key_order:
                key_cn = keymap.get(k, "None")
                val_map[k] = raw_input(key_cn+": ")
                
            while True:
                resp = raw_input(u"是否确认增加? (y or n) ")
                if str(resp).strip().lower() in ["n","no"]: break
                if str(resp).strip().lower() in ["y","yes"]:
                    self.add_section(section)
                    for k in self._key_order: self.set(section, k, val_map[k])
                    self.save()
                    break
        except:
            print traceback.format_exc()
