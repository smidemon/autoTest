# coding=utf-8

import os,sys,time,json,urllib2,re
import ConfigParser
import logging
import unittest
sys.path.insert(0, '/root/FunctionAutomation/ekos_auto')
import ekosUtils


test_utils = ekosUtils.Utils()
logger = logging.getLogger("test")
config = ConfigParser.ConfigParser()
config.readfp(open('smoking_test.ini'))
ipaddr = config.get("main","ipaddr")

class TestManageHosts(unittest.TestCase):
    
    def test_get_nodes_page(self):
        value = test_utils.get_nodes_page(ipaddr)
        if value["nodes"]["listMeta"]["totalItems"] >= 2:
            logger.info("Get nodes page successfully!")
        else:
            logger.error("Get nodes page failed!")
        self.assertGreaterEqual(value["nodes"]["listMeta"]["totalItems"], 2)
    
    def test_enable_node(self):
        value = test_utils.enable_node(ipaddr)
        if value["spec"].has_key("unschedulable") == False:
            logger.info("Enable node successfully!")
        else:
            logger.error("Enable node failed!")
        self.assertEqual(value["spec"].has_key("unschedulable"), False)

    def test_disabe_node(self):
        value = test_utils.disable_node(ipaddr)
        if value["spec"]["unschedulable"] == True:
            logger.info("Disable node successfully!")
        else:
            logger.error("Disable node failed!")
        self.assertEqual(value["spec"]["unschedulable"], True) 

    def test_nodes_view_log(self):
        value = test_utils.nodes_view_log(ipaddr)
        if value:
            logger.info("View log successfully!")
        else:
            logger.error("View log failed!")
        self.assertTrue(value) 


if __name__ == '__main__':
    unittest.main()
