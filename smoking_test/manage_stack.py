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

class TestManageStack(unittest.TestCase):
    
    def test_add_stack(self):
        js = config.get("json","stack")
        value = test_utils.add_stack(ipaddr,js)
        if value["status"] == "success":
            logger.info("Add stack successfully!")
        else:
            logger.error("Add stack failed!")
        self.assertEqual(value["status"], "success")
    
    def test_add_app(self):
        js = config.get("json","app")
        value = test_utils.add_app(ipaddr,js)
        if value["status"] == "success":
            logger.info("Add stack successfully!")
        else:
            logger.error("Add stack failed!")
        self.assertEqual(value["status"], "success")

    def test_check_app(self):
        appname = json.loads(config.get("json","app"))["name"]
        value = test_utils.app_status_check(ipaddr, appname)
        if value:
            logger.info("App status is running!")
        else:
            logger.error("After waiting 5mins, the app is still not running!")
        self.assertTrue(value)

    def test_add_port(self):
        js = config.get("json","add_port")
        value = test_utils.add_port_mapping(ipaddr,js)
        if value["status"] == "success":
            logger.info("Add port mapping successfully!")
        else:
            logger.error("Add port mapping failed!")
        self.assertEqual(value["status"], "success")

    def test_update_port(self):
        js = config.get("json","update_port")
        value = test_utils.update_port_mapping(ipaddr,js)
        if value["status"] == "success":
            logger.info("Update port mapping successfully!")
        else:
            logger.error("Update port mapping failed!")
        self.assertEqual(value["status"], "success")

    def test_config_autoscale(self):
        js = config.get("json","autoscale")
        value = test_utils.config_autoscale(ipaddr,js)
        if value["status"] == "success":
            logger.info("Configure autoscale successfully!")
        else:
            logger.error("Configure autoscale failed!")
        self.assertEqual(value["status"], "success")

    def test_disable_autoscale(self):
        js = config.get("json","disable_as")
        value = test_utils.disable_autoscale(ipaddr,js)
        if value["status"] == "success":
            logger.info("Disable autoscale successfully!")
        else:
            logger.error("Disable autoscale failed!")
        self.assertEqual(value["status"], "success")

    def test_add_tcp_lb(self):
        js = config.get("json","tcp_lb")
        value = test_utils.add_tcp_lb(ipaddr,js)
        if value["status"] == "success":
            logger.info("Add tcp_lb successfully!")
        else:
            logger.error("Add tcp_lb failed!")
        self.assertEqual(value["status"], "success")

    def test_add_tcp_lb_rule(self):
        js = config.get("json","tcp_lb_rule")
        value = test_utils.add_tcp_lb_rule(ipaddr,js)
        if value["status"] == "success":
            logger.info("Add tcp_lb rule successfully!")
        else:
            logger.error("Add tcp_lb rule failed!")
        self.assertEqual(value["status"], "success")

    def test_check_lb(self):
        lbname = json.loads(config.get("json","tcp_lb"))["name"]
        value = test_utils.lb_status_check(ipaddr, lbname)
        if value:
            logger.info("LB status is running!")
        else:
            logger.error("After waiting 5mins, the lb is still not running!")
        self.assertTrue(value)

    def test_app_delete(self):
        appname = json.loads(config.get("json","app"))["name"]
        value = test_utils.app_delete(ipaddr, appname)
        if value:
            logger.info("Delete app successfully!")
        else:
            logger.error("Delete app failed!")
        self.assertTrue(value)

    def test_lb_delete(self):
        lbname = json.loads(config.get("json","tcp_lb"))["name"]
        value = test_utils.app_delete(ipaddr, lbname)
        if value:
            logger.info("Delete lb successfully!")
        else:
            logger.error("Delete lb failed!")
        self.assertTrue(value)

    def test_stack_delete(self):
        stackname = json.loads(config.get("json","stack"))["name"]
        value = test_utils.stack_delete(ipaddr, stackname)
        if value:
            logger.info("Delete lb successfully!")
        else:
            logger.error("Delete lb failed!")
        self.assertTrue(value)


if __name__ == '__main__':
    unittest.main()
