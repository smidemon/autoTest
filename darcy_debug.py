import os,sys,time,json
sys.path.insert(0, '/root/ekos_auto')
from log import *
import ekosUtils
my_utils = ekosUtils.Utils()
ip = sys.argv[1]
rtn = my_utils.ssh_cmd(ip,"root","password","ls",lines=True)
print rtn