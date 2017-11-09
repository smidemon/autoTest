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

class TestStorage(unittest.TestCase):
    
    def test_add_nfs(self):
        js = config.get("json","nfs_json")
        value = test_utils.add_nfs_storage(ipaddr,js)
        if value == 200:
            logger.info("Add nfs storage successfully!")
        else:
            logger.error("Add nfs storage failed!")
        self.assertEqual(value, 200)

    def test_nfs_check(self):
        storage_name = json.loads(config.get("json","nfs_json"))["storage_name"]
        value = test_utils.storage_status_check(ipaddr, storage_name)
        if value:
            logger.info("NFS status is ok!")
        else:
            logger.error("After waiting 3 mins, nfs status is still bad!")
        self.assertTrue(value)

    def test_nfs_delete(self):
        storage_name = json.loads(config.get("json","nfs_json"))["storage_name"]
        value = test_utils.delete_storage(ipaddr, storage_name)
        if value == "ok":
            logger.info("Delete nfs successfully!")
        else:
            logger.error("Delete nfs failed!")
        self.assertEqual(value, "ok")

    def test_add_ceph(self):
        js = config.get("json","ceph_json")
        value = test_utils.add_ceph_storage(ipaddr,js)
        if value == 200:
            logger.info("Add ceph storage successfully!")
        else:
            logger.error("Add ceph storage failed!")
        self.assertEqual(value, 200)

    def test_ceph_check(self):
        storage_name = json.loads(config.get("json","ceph_json"))["storage_name"]
        value = test_utils.storage_status_check(ipaddr, storage_name)
        if value:
            logger.info("Ceph status is ok!")
        else:
            logger.error("After waiting 3mins, ceph status is still bad!")
        self.assertTrue(value)

    def test_ceph_delete(self):
        storage_name = json.loads(config.get("json","ceph_json"))["storage_name"]
        value = test_utils.delete_storage(ipaddr, storage_name)
        if value == "ok":
            logger.info("Delete ceph successfully!")
        else:
            logger.error("Delete ceph failed!")
        self.assertEqual(value, "ok")


if __name__ == '__main__':
    unittest.main()
