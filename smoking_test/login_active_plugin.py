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


class TestLogin(unittest.TestCase):
    
    # test login
    def test_login(self):
        url = "http://" + ipaddr + ":30000/login"
        response_json = test_utils.call_rest_api(url,"POST",params="username=admin&password=admin12345")
        response = json.loads(response_json)
        value = response["status"]
        if value == "success":
            logger.info("Login UI successfully!")
        else:
            logger.error("Login UI failed!")
        self.assertEqual(value, "success")
        
    # test logout
    def test_logout(self):
        url = "http://" + ipaddr + ":30000/login?referer=/ui/"
        response_code = test_utils.call_rest_api_second(url,"GET")
        if response_code == 200:
            logger.info("Logout UI successfully!")
        else:
            logger.error("Logout UI failed!")
        self.assertEqual(response_code, 200)

    # active plugin
    def test_active_tenant(self):
        value = test_utils.active_plugin_tenant(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Tenant successfully!")
        else:
            logger.error("Active Tenant failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_image_manage(self):
        value = test_utils.active_plugin_image_manage(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Image_manage successfully!")
        else:
            logger.error("Active Image_manage failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_node(self):
        value = test_utils.active_plugin_node(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Node successfully!")
        else:
            logger.error("Active Node failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_stack(self):
        value = test_utils.active_plugin_stack(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Stack successfully!")
        else:
            logger.error("Activ Stack failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_storage(self):
        value = test_utils.active_plugin_storage(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Storage successfully!")
        else:
            logger.error("Activ Storage failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_registry(self):
        value = test_utils.active_plugin_registry(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Registry successfully!")
        else:
            logger.error("Activ Registry failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_network(self):
        value = test_utils.active_plugin_network(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Network successfully!")
        else:
            logger.error("Activ Network failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_appstore(self):
        value = test_utils.active_plugin_appstore(ipaddr)
        if value["status"] == "ok":
            logger.info("Active Appstore successfully!")
        else:
            logger.error("Activ Appstore failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_logging(self):
        value = test_utils.active_plugin_logging(ipaddr)
        time.sleep(60)
        if value["status"] == "ok":
            logger.info("Active Logging successfully!")
        else:
            logger.error("Activ Logging failed!")
        self.assertEqual(value["status"], "ok")

    def test_active_monitor(self):
        value = test_utils.active_plugin_monitor(ipaddr)
        time.sleep(180)
        if value["status"] == "ok":
            logger.info("Active Monitor successfully!")
        else:
            logger.error("Activ Monitor failed!")
        self.assertEqual(value["status"], "ok")

    # admin console off
    def test_admin_off(self):
        value = test_utils.admin_off(ipaddr)
        if value["admin"] == False:
            logger.info("Start with tenant console!")
        else:
            logger.error("Start with tenant console failed!")
        self.assertEqual(value["admin"], False)

    # admin console on
    def test_admin_on(self):
        value = test_utils.admin_on(ipaddr)
        if value["admin"]:
            logger.info("Start with admin console!")
        else:
            logger.error("Start with admin console failed!")
        self.assertEqual(value["admin"], True)

if __name__ == '__main__':
    unittest.main()
