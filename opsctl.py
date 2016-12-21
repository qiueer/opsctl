#!/usr/bin/env python
# -*- encoding=utf-8 -*-
###
###

import sys
import os
import re
import codecs
import ConfigParser
import readline
import atexit
import traceback
from optparse import OptionParser

from lib.base.slog import slog
from lib.base.scolor import scolor
from lib.base.sdate import sdate
from lib.base.cmds import cmds
from lib.base.sstr import sstr
from lib.helper.conf_helper import conf_helper


reload(sys) 
sys.setdefaultencoding('utf8')
histfile = os.path.join(os.environ["HOME"], ".opsctl")

def get_realpath():
    return os.path.split(os.path.realpath(__file__))[0]

def get_binname():
    return os.path.split(os.path.realpath(__file__))[1]

class Work(object):
    def __init__(self, chp=None, debug=False):
        self._chp = chp  ## conf_helper instance
        self._debug = debug
        self._logger = slog("/tmp/opsctl.log", debug=debug)
    
    def start(self, section_id=None):
        itemconf = self._chp.get_section_dict(section_id)
        appname = itemconf.get("appname", None)
        start_cmd = itemconf.get("start_cmd", None)
        self._logger.dictlog(level="info", width=20, **itemconf)

        scolor.info(u"#### [%s] 启动应用【%s】 ####" % (sdate().datetime_human(), appname))
        if str(start_cmd).strip() == None:
            scolor.warn(u"应用【%s】启动命令为空"% (appname))
            return
        c2 = cmds(start_cmd)
        stdo = c2.stdo()
        stde = c2.stde()
        retcode = c2.code()
        #exeop = str("%s\n%s" % (stdo,stde)).strip()

        if retcode == 0 and str(stde).strip() == "":
            scolor.info(u"启动应用【%s】成功！" % (appname))
        else:
            scolor.error(u"启动应用【%s】失败！" % (appname))

        logobj = {
                  u"命令": start_cmd,
                  u"标准输出": stdo,
                  u"错误输出": stde,
                  u"返回码": retcode,
                  u"orders": [u"命令", u"标准输出", u"错误输出", u"返回码"]
        }
        self._logger.dictlog(level="info", width=12, **logobj)

        
    def stop(self, section_id=None):
        itemconf = self._chp.get_section_dict(section_id)
        appname = itemconf.get("appname", None)
        stop_cmd = itemconf.get("stop_cmd", None)
        self._logger.dictlog(level="info", width=20, **itemconf)

        scolor.info(u"#### [%s] 停止应用【%s】 ####" % (sdate().datetime_human(), appname))
        if str(stop_cmd).strip() == None:
            scolor.warn(u"应用【%s】停止命令为空" % (appname))
            return
        
        c2 = cmds(stop_cmd)
        stdo = c2.stdo()
        stde = c2.stde()
        retcode = c2.code()

        #exeop = str("%s\n%s" % (stdo,stde)).strip()
        if retcode == 0 and str(stde).strip() == "":
            scolor.info(u"停止应用【%s】成功！"% (appname))
        else:
            scolor.error(u"停止应用【%s】失败！"% (appname))

        logobj = {
                  u"命令": stop_cmd,
                  u"标准输出": stdo,
                  u"错误输出": stde,
                  u"返回码": retcode,
                  u"orders": [u"命令", u"标准输出", u"错误输出", u"返回码"]
        }
        self._logger.dictlog(level="info", width=12, **logobj)

    def restart(self, section_id=None):
        self.stop(section_id=section_id)
        self.start(section_id=section_id)
        
    def status(self, section_id=None):
        itemconf = self._chp.get_section_dict(section_id)
        appname = itemconf.get("appname", None)
        process_uniq_flag = itemconf.get("process_uniq_flag", None)
        process_port = itemconf.get("process_port", None)
        status_cmd = itemconf.get("status_cmd", None)
        self._logger.dictlog(level="info", width=20, **itemconf)

        scolor.info(u"#### [%s] 检测应用【%s】状态 ####" % (sdate().datetime_human(), appname))
        if status_cmd and str(status_cmd).strip():
            c2 = cmds(status_cmd, timeout=10)
            stdo,stde, retcode = c2.stdo(), c2.stde(), c2.code()
            logdict = {
                "命令": status_cmd,
                "标准输出": stdo,
                "标准错误输出": stde,
                "返回码": retcode,
                "orders": ["命令","标准输出", "标准错误输出", "返回码"],
            }
            self._logger.dictlog(level="info", width=10, **logdict)
            scolor.info(u"-> 根据用户指定的状态命令检测应用状态" )
            print "    命令：%s" % (status_cmd)
            print "执行结果："
            print "========="
            print str(str(stdo).strip()+"\n"+str(stde).strip()).strip()

        if process_uniq_flag and str(process_uniq_flag).strip():
            (flag,cmdstr,stdo,stde,retcode) = self.is_process_exist(process_uniq_flag)
            scolor.info(u"-> 根据应用进程唯一标识检测")
            print "    命令：%s" % (cmdstr)
            print "执行结果："
            print "========="
            print str(str(stdo).strip()+"\n"+str(stde).strip()).strip()

        if process_port:
            (flag,cmdstr,stdo,stde,retcode)  = self.is_port_exist(process_port)
            scolor.info(u"-> 根据应用进程端口检测")
            print "    命令：%s" % (cmdstr)
            print "执行结果："
            print "========="
            print str(str(stdo).strip()+"\n"+str(stde).strip()).strip()

    def is_check_ok(self, check_cmd, check_str):
        if not check_cmd or not check_str or str(check_cmd).strip()=="" or str(check_str).strip()=="":
            return True,None,None,None,None
        c1 = cmds(check_cmd)
        stdo,stde,retcode = c1.stdo(), c1.stde(), c1.code()
        logdict = {
            "命令": check_cmd,
            "标准输出": stdo,
            "标准错误输出": stde,
            "返回码": retcode,
            "检测结果": "OK" if retcode == 0 and str(stdo).strip() == str(check_str) else "BAD",
            "orders": ["命令","标准输出", "标准错误输出", "返回码", "检测结果"],
        }
        self._logger.dictlog(level="info", width=10, **logdict)
        if retcode == 0 and str(stdo).strip() == str(check_str):
            return (True,check_cmd,stdo,stde,retcode)
        return (False,check_cmd,stdo,stde,retcode)
    
    def is_process_exist(self, process_uniq_flag):
        ## check process
        if not process_uniq_flag or str(process_uniq_flag).strip() == "":
            return True,None,None,None,None
        proc_flag_ary = re.split("[ ,;]+", str(process_uniq_flag).strip())
        grep_str = ""
        for proc_chk_str in proc_flag_ary:
            if str(proc_chk_str).strip() == None:continue
            grep_str += "grep -E '%s' | " % (proc_chk_str)
        grep_str = str(grep_str).strip()[:-1].strip()

        self_script_name = sys.argv[0]
        cmdstr = "ps -ef | %s | grep -v grep | grep -v '%s' | wc -l" % (grep_str, self_script_name) 
        c1 = cmds(cmdstr)
        stdo,stde,retcode = c1.stdo(), c1.stde(), c1.code()
        logdict = {
            "命令": cmdstr,
            "标准输出": stdo,
            "标准错误输出": stde,
            "返回码": retcode,
            "orders": ["命令","标准输出", "标准错误输出", "返回码", "检测结果"],
        }
        self._logger.dictlog(level="info", width=10, **logdict)
        if retcode == 0 and int(str(stdo).strip()) > 0:
            return (True,cmdstr,stdo,stde,retcode)
        return (False,cmdstr,stdo,stde,retcode)
    
    def is_port_exist(self, process_port):
        if not process_port or str(process_port).strip() == "":
            return (True,None,None,None,None)
        cmdstr = "ss -anlt | grep ':%s ' | wc -l " % (str(process_port).strip())
        c1 = cmds(cmdstr)
        stdo,stde,retcode = c1.stdo(), c1.stde(), c1.code()
        logdict = {
            "命令": cmdstr,
            "标准输出": stdo,
            "标准错误输出": stde,
            "返回码": retcode,
            "orders": ["命令","标准输出", "标准错误输出", "返回码", "检测结果"],
        }
        self._logger.dictlog(level="info", width=10, **logdict)
        if retcode == 0 and int(str(stdo).strip()) > 0:
            return (True,cmdstr,stdo,stde,retcode)
        return (False,cmdstr,stdo,stde,retcode)
                
    def check(self, section_id=None):
        itemconf = self._chp.get_section_dict(section_id)
        appname = itemconf.get("appname", None)
        process_uniq_flag = itemconf.get("process_uniq_flag", None)
        process_port = itemconf.get("process_port", None)
        check_cmd = itemconf.get("check_cmd", None)
        check_str = itemconf.get("check_str", None)
        self._logger.dictlog(level="info", width=20, **itemconf)

        scolor.info(u"#### [%s] 检测应用【%s】运行状态 ####" % (sdate().datetime_human(), appname))
        
        is_ok = True
        mt_method = {"False": scolor.error, "True": scolor.info}
        if check_cmd and check_str:
            check_flag,cmdstr,stdo,stde,retcode = self.is_check_ok(check_cmd, check_str)
            is_ok = is_ok and check_flag
            scolor.info(u"-> 根据检测命令检测")
            mt_method[str(check_flag)](str(check_flag))

        if process_uniq_flag:
            chk_proc_flag,cmdstr,stdo,stde,retcode = self.is_process_exist(process_uniq_flag)
            is_ok = is_ok and chk_proc_flag
            scolor.info(u"-> 根据应用进程唯一标识检测")
            mt_method[str(chk_proc_flag)](str(chk_proc_flag))
            
        if process_port:
            chk_proc_port_flag,cmdstr,stdo,stde,retcode = self.is_port_exist(process_port)
            is_ok = is_ok and chk_proc_port_flag
            scolor.info(u"-> 根据应用进程端口检测")
            mt_method[str(chk_proc_port_flag)](str(chk_proc_port_flag))

        return is_ok

    def monitor(self, section_id=None):
        if self.check(section_id=section_id) == False:
            self.start(section_id=section_id)

def main():
    try:
        parser = OptionParser()
        parser.add_option("-c", "--conf",  
                  action="store", dest="conf", default=None,  
                  help="configure file", metavar="${backup_conf_file}")
        parser.add_option("-l", "--list", dest="list", default=False,
                  action="store_true", help="list all the configure")
        parser.add_option("-a", "--add", dest="add", default=False,
                  action="store_true", help="add configure to config file")
        parser.add_option("-m", "--modify", dest="modify", default=False,
                  action="store_true", help="modify backup configure to config file")
        parser.add_option("-d", "--delete", dest="delete", default=False,
                  action="store_true", help="delete backup configure from config file")
        parser.add_option("-D", "--debug", dest="debug", default=False,
                  action="store_true", help="if open debug module")
        parser.add_option("-i", "--id",  
                          action="store", dest="id", default=None,  
                          help="which id's configure to be loaded to execute", metavar="${id}")
        parser.add_option("-s", "--signal",  
                          action="store", dest="signal", default=None,  
                          help="signal like: start, stop, restart, status, monitor", metavar="${signal}")

        (options, args) = parser.parse_args()
        list_flag = options.list
        conffile = options.conf
        add_flag = options.add
        modify_flag = options.modify
        delete_flag = options.delete
        debug_flag = options.debug
        section_id = options.id
        signal = options.signal
        
        if not conffile:
            conffile = get_realpath() + "/etc/opsctl.conf"

        if os.path.exists(conffile) == False:
            conffile = "/etc/opsctl.conf"
            if os.path.exists(conffile) == False:
                parser.print_help()
                sys.exit(1)
                
        tmp_list = [list_flag, add_flag, modify_flag, delete_flag]
        cnt = 0
        for a in tmp_list:
            if a == True: cnt += 1
            
        if cnt > 1:
            parser.print_help()
            sys.exit(1)

        key_map = {
                   "appname": u"应用名称", 
                   "process_uniq_flag": u"进程唯一标识", 
                   "process_port": u"进程端口", 
                   "start_cmd":u"启动命令",
                   "stop_cmd":u"停止命令",
                   "status_cmd":u"状态命令",
                   "check_cmd":u"检测命令",
                   "check_str":u"检测字符串",
        }
        key_order = ["appname", "process_uniq_flag", "process_port", "start_cmd", "stop_cmd", "status_cmd", "check_cmd", "check_str"]
        chp = conf_helper(conffile, key_map=key_map, key_order=key_order, max_key_len=12)
        
        wk = Work(chp=chp, debug=debug_flag)
        ## backup the input section
        method_map = {
            "start": wk.start,
            "stop": wk.stop,
            "restart": wk.restart,
            "status": wk.status,
            "monitor": wk.monitor,
        }
        
        if signal and signal not in method_map.keys():
            parser.print_help()
            sys.exit(1)
            
        ## action
        if signal and section_id:
            if chp.has_section(section_id) == False:
                scolor.error(u"不存在Section: %s" %(section_id))
                return
            method_map[signal](section_id)
            return

        ## list all
        if list_flag == True and not section_id:
            chp.list()
            return
        
        ## list one
        if  list_flag == True and section_id and not signal:
            chp.list_one(section_id)
            return
        
        ## delete one
        if delete_flag and section_id and not signal:
            chp.delete(section_id)
            return
        
        ## modify one
        if modify_flag and section_id and not signal:
            chp.modify(section_id)
            return

        ## add one
        if add_flag and not section_id and not signal:
            chp.add()
            return

        ## monitor all
        if signal == "monitor" and not section_id:
            secs = chp.sections()
            for sid in secs:
                method_map["monitor"](sid)
            return
            
        parser.print_help()

    except Exception as expt:
        print traceback.format_exc()
        
if __name__ == "__main__":
    main()
