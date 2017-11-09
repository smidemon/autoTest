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

pub_id = None
pri_id = None

class TestManageImage(unittest.TestCase):
    
    def test_get_registry(self):
        value = test_utils.get_registry(ipaddr)
        if value:
            logger.info("Get registry successfully!")
        else:
            logger.error("Get registry failed!")
        self.assertTrue(value)

    def test_add_pub_registry(self):
        js = config.get("json","pub_registry")
        value = test_utils.add_registry(ipaddr,js)
        globals()['pub_id'] = value
        if value:
            logger.info("Add pub registry successfully!")
        else:
            logger.error("Add pub registry failed!")
        self.assertTrue(value)

    def test_update_auth(self):
        value = test_utils.update_auth(ipaddr,pub_id)
        if value["status"] == "ok":
            logger.info("Update registry auth successfully!")
        else:
            logger.error("Update registry auth failed!")
        self.assertEqual(value["status"], "ok")

    def test_delete_pub(self):

        value = test_utils.delete_registry(ipaddr,pub_id)
        if value == 200:
            logger.info("Delete public registry successfully!")
        else:
            logger.error("Delete public registry failed!")
        self.assertEqual(value, 200)

    def test_add_pri_registry(self):
        js = config.get("json","pri_registry")
        value = test_utils.add_registry(ipaddr,js)
        globals()['pri_id'] = value
        if value:
            logger.info("Add pub registry successfully!")
        else:
            logger.error("Add pub registry failed!")
        self.assertTrue(value)

    def test_delete_pri(self):
        value = test_utils.delete_registry(ipaddr,pri_id)
        if value == 200:
            logger.info("Delete private registry successfully!")
        else:
            logger.error("Delete private registry failed!")
        self.assertEqual(value, 200)

    def test_get_images(self):
        value = test_utils.get_images(ipaddr)
        if value:
            logger.info("Get images successfully!")
        else:
            logger.error("Get images failed!")
        self.assertTrue(value)

    def test_delete_image(self):
        image = config.get("json","image")
        value = test_utils.delete_image(ipaddr,image)
        if value["status"] == "ok":
            logger.info("Delete image successfully!")
        else:
            logger.error("Delete image failed!")
        self.assertEqual(value["status"], "ok")


if __name__ == '__main__':
    unittest.main()
