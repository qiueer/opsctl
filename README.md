# opsctl, Ops Control
=========================================

##  功能说明
```
运维常用工具，包括应用启停、监控拉起、状态检测及配置管理等
```

## 使用方法
```
（1）默认配置文件
etc/opsctl.conf，如果该文件不存在，则读取/etc/opsctl.conf，或者用户通过参数-c或--conf指定。另在etc/下有名为opsctl_example.conf的示例配置文件，里面对各个参数均有说明，对于配置文件，如果不是非常清楚每个参数代表的意思，最好通过本工具进行配置，手动配置可能会引起未知的错误。
（2）帮助信息，python opsctl.py -h  
Usage: opsctl.py [options]  

Options:  
  -h, --help            show this help message and exit  
  -c ${backup_conf_file}, --conf=${backup_conf_file}  configure file  
  -l, --list            list all the configure  
  -a, --add             add configure to config file  
  -m, --modify          modify backup configure to config file  
  -d, --delete          delete backup configure from config file  
  -D, --debug           if open debug module  
  -i ${id}, --id=${id}  which id's configure to be loaded to execute  
  -s ${signal}, --signal=${signal} signal like: start, stop, restart, status, monitor  
  
（3）功能包括三大块：应用启动、停止、重启；应用监控与拉起；应用配置管理，使用示例：  
I）列出所有的应用配置  
python opsctl.py -l  

II）列出指定section_id的应用配置，如：  
python opsctl.py -l -i nginx

III）启动or停止or重启or检测状态or监控section_id为nginx的应用  
python opsctl.py -i nginx -s [start|stop|restart|status|monitor]

IV）删除or修改section_id为nginx的应用管理配置
python opsctl.py -i nginx [-d|-m]

V）增加配置
python opsctl.py -a

VI）监控所有应用，注意，监控包括两个动作：检测、启动，如果检测不到应用（或应用不可用）则会执行启动命令
python opsctl.py -s monitor
```

## 其他要点：
```
（1）日志
路径：/tmp/opsctl.log，按大小为10M滚动，保留5份
（2）debug模式
使用的过程中可以加-D参数打开，该工具会将执行过程中关键的操作输出到console中
```
