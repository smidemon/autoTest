import sys,json,time,random
sys.path.insert(0, '/root/ekos_auto/')
import ekosUtils
from log import *
my_utils = ekosUtils.Utils()

ip = sys.argv[1]
my_utils.clean_app(ip)	
my_utils.delete_all_lb(ip)
info('ok')	
