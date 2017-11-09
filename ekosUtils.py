import sys,urllib2,json,subprocess,time,cookielib,re,pysphere,paramiko,progressbar
#from pysphere.resources import VimService_services as VI
#from pysphere.vi_virtual_machine import VIVirtualMachine
import ConfigParser
from log import *

config = ConfigParser.ConfigParser()
config.readfp(open('smoking_test.ini'))

class Utils:
	def __init__(self):
		pass

	def call_rest_api(self,url,req_type,params=None,cookies=None,json=None):
		retry_num = 10
		retry_interval_time = 10
		cnt = 0
		while cnt < retry_num:
			if params != None:
				newurl = url + "?" + params
			else:
				newurl = url
			req = urllib2.Request(newurl)
			req.add_header('Content-Type','application/json')
			req.add_header('Accept','application/json')
			if cookies is not None:
				req.add_header('Cookie',cookies)
			req.get_method = lambda: req_type
			try:
				if json != None:
					response = urllib2.urlopen(req,json)
				else:
					response = urllib2.urlopen(req)
			except Exception,e:
				error('============Exception===========')
				error(e)
				cnt += 1
				error('Exception caught, retry count: %d' % cnt)
				time.sleep(retry_interval_time)
				if 'HTTP Error 401' in str(e):
					pattern = '\d+\.\d+\.\d+\.\d+'
					m = re.search(pattern, newurl)
					ipaddr = m.group()
					cookies = self._get_cookie(ipaddr)
					info("new cookies created %s" %ipaddr)	
				continue
			return response.read()
		return None

	def call_rest_api_second(self,url,req_type,params=None,cookies=None,json=None):
		retry_num = 10
		retry_interval_time = 10
		cnt = 0
		while cnt < retry_num:
			if params != None:
				newurl = url + "?" + params
			else:
				newurl = url
			req = urllib2.Request(newurl)
			req.add_header('Content-Type','application/json')
			req.add_header('Accept','application/json')
			if cookies is not None:
				req.add_header('Cookie',cookies)
			req.get_method = lambda: req_type
			try:
				if json != None:
					response = urllib2.urlopen(req,json)
				else:
					response = urllib2.urlopen(req)
			except Exception,e:
				error('============Exception===========')
				error(e)
				cnt += 1
				error('Exception caught, retry count: %d' % cnt)
				time.sleep(retry_interval_time)
				if 'HTTP Error 401' in str(e):
					pattern = '\d+\.\d+\.\d+\.\d+'
					m = re.search(pattern, newurl)
					ipaddr = m.group()
					cookies = self._get_cookie(ipaddr)
					info("new cookies created %s" %ipaddr)	
				continue
			return response.getcode()
		return None


	def _get_cookie(self,ipaddr): 
		all_cookie = ""
		url = "http://" + ipaddr + ":30000/login"
		cj = cookielib.CookieJar()
		opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
		urllib2.install_opener(opener)
		response = self.call_rest_api(url,"POST",params="username=admin&password=admin12345")
		for index,cookie in enumerate(cj):
			tmp = cookie.name + "=" + cookie.value + "; "
			all_cookie += tmp
		return all_cookie

	
	def runcmd(self,cmd,print_ret = True,lines = False):
		if print_ret:
			info('Running: %s' % cmd)
		try:
			rtn_tmp = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			rtn_tmp.wait()
			if print_ret:
				rtn = rtn_tmp.stdout.read()
				if lines:
					rtn_n = [ line for line in rtn.split('\n') if line != '' ]
					#print rtn_n
					return rtn_n
				
				else:
					return rtn
		except OSError:
			info('Exception caught in running %s' % cmd)
			return (127, 'OSError')
		return

	def ssh_cmd(self, ip, username, password, cmd, sync_run=True, timeout=None,lines=False):
		info('running: %s' % cmd)
		rtn_dict = {}
		ssh = paramiko.SSHClient()
		ssh.load_system_host_keys()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		retry_cnt = 10
		cnt = 1
		while cnt < retry_cnt:
			try:
				ssh.connect(ip, 22, username, password, timeout=timeout)
			except Exception as e:
				info('got exception: %s' % e)
				info('retry number: %d ' % cnt)
				cnt = cnt + 1
				time.sleep(10)
				continue
			try:	
				stdin, stdout, stderr = ssh.exec_command(cmd, timeout=timeout)
			except Exception as e:
				info('got exception: %s' % e)
				info('retry number: %d ' % cnt)
				cnt = cnt + 1
				ssh.close()
				time.sleep(10)
				continue
			if sync_run != True:
				time.sleep(30)
				return True
			rtn_dict['stdout'] = stdout.read()
			rtn_dict['stderr'] = stderr.read()
			ssh.close()
			if lines:
				return [line for line in rtn_dict['stdout'].split("\n") if line != ""]
			return rtn_dict

	def bar_sleep(self,sleep_time):

		widgets = ['<sleep time: ', str(sleep_time), '> ', progressbar.Percentage(), ' ', progressbar.Bar(marker=progressbar.RotatingMarker('>-=#')),' ', progressbar.ETA()]
		bar = progressbar.ProgressBar(widgets=widgets, maxval=50).start()
		for i in bar(range(sleep_time)):
			time.sleep(1)
		bar.finish()


	def sendmail(self,obj,content,namelist):
		cmd = "echo " + content + " | mail -s " + obj + " " + namelist  
		self.runcmd(cmd)



	def connect_vcenter(self,server):
		ip = "192.168.1.246"
		username = "administrator@vcenter.local"
		password = "P@ssw0rd"
		try:
			server.connect(ip,username,password)
		except Exception,e:
			error("connect to vcenter failed: %s" % str(e))
			return False
		return True

	def disconnect_vcenter(self,server):
		server.disconnect()

	def get_vm_status(self,vm_name,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			return False
		try:
			rtn = vm.get_status()
		except Exception,e:
			error('Can not get vm %s status!' % vm_name)
		self.disconnect_vcenter(server)
		return rtn	
	


	def reset_vm(self,vm_name,sync_run=True,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			return False
		try:
			vm.reset(sync_run)
		except Exception,e:
			error('%s reset failed!' % vm_name)
		info('%s reset successfully!' %vm_name)
		self.disconnect_vcenter(server)
		return True

	def reboot_vm(self,vm_name,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			return False
		try:
			vm.reboot_guest()
		except Exception,e:
			error('%s reboot failed!' % vm_name)
			return False
		info('%s reboot successfully!' % vm_name)
		self.disconnect_vcenter(server)
		return True	

	def shutdown_vm(self,vm_name,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			return False
		try:
			vm.shutdown_guest()
		except Exception,e:
			error('%s shutdown failed!' % vm_name)
			return False
		time_flag = 0
		while True:
			if time_flag > 10:
				error('%s shutdown time out' % vm_name)
				return False
			rtn = self.get_vm_status(vm_name)
			if rtn =='POWERED OFF':
				info('%s has been shutdown!' %vm_name)
				break
			else:
				time.sleep(5)
				time_flag = time_flag + 1

		self.disconnect_vcenter(server)
		return True	

	def poweroff_vm(self,vm_name,sync_run=True,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			return False
		try:
			vm.power_off(sync_run)
		except Exception,e:
			error('%s power off failed!' % vm_name)
			return False
		info('%s power off successfully!' % vm_name)
		self.disconnect_vcenter(server)
		return True	

	def poweron_vm(self,vm_name,sync_run=True,datacenter=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name, datacenter)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			self.disconnect_vcenter(server)
			return False
		try:
			vm.power_on(sync_run)
		except Exception,e:
			self.disconnect_vcenter(server)
			error('%s power on failed!' % vm_name)
			return False
		info('%s power on successfully!' % vm_name)
		self.disconnect_vcenter(server)
		return True
#------------------------------deploy related-------------------------------------------
	def rollback_snapshot(self,vm_name,sync_run=True,Host=None):
		server = pysphere.VIServer()
		self.connect_vcenter(server)
		try:
			vm = server.get_vm_by_name(vm_name)
		except Exception,e:
			error("Can not find the vm,vm name: %s" % vm_name)
			error(e)
			self.disconnect_vcenter(server)
			return False
		try:
			vm.revert_to_snapshot(sync_run,Host)
		except Exception,e:
			self.disconnect_vcenter(server)
			error('%s revert to snapshot failed!' % vm_name)
			return False
		info('%s revert to snapshot successfully!' % vm_name)
		self.disconnect_vcenter(server)
		return True

	#must give the vip is master HA is enabled
	def deploy_ekos(self,build_name,inventory,node_name_list,ceph_list,ceph_vip,vip=None,username="root",password="password"):
		build_url = "http://192.168.1.234:8080/ekos/Build_Backup/" + build_name
		if "deploy" not in inventory:
			error("No deploy node!")
		#rollback snapshot and power on
		for node in node_name_list:
			self.rollback_snapshot(node)
			node_powerstate = self.get_vm_status(node)
			if node_powerstate != "POWERED ON":
				self.poweron_vm(node)
			else:
				info('reset node!')
				self.reset_vm(node)
		self.bar_sleep(200)


		#download package and tar
		
		deploy_ip = inventory['deploy']
		#tar -zxvf 
		info('downloading and tar...')
		cmd = "curl -O " + build_url
		
		#cmd = cmd1 + ';' + cmd2 + ';'
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		time.sleep(5)

		cmd = 'tar -zxvf ' + build_name
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		info('execute ./deploy.sh')
		cmd = "cd deploy;./deploy.sh"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		#check if need config master HA
		if "-" in inventory['master'] or "," in inventory['master']:
			time_str = time.strftime('%Y%m%d',time.localtime())
			cmd = "ekoslet cluster set apiserver_loadbalancer_domain_name " + time_str + ".local"
			rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
			if rtn:
				if not rtn.has_key('stdout'):
					error('ssh command failed!')
					error(rtn)
					return False

			cmd = "ekoslet cluster set loadbalancer_apiserver:port 9600"
			rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
			if rtn:
				if not rtn.has_key('stdout'):
					error('ssh command failed!')
					error(rtn)
					return False

			if not vip:
				error('No vip was set!')
				return False
			cmd = "ekoslet cluster set loadbalancer_apiserver:address " +  vip
			rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
			if rtn:
				if not rtn.has_key('stdout'):
					error('ssh command failed!')
					error(rtn)
					return False

		#add inventory
		cmd = "ekoslet inventory init master:" + inventory['master'] + ":etcd:" + inventory['etcd'] + ":node:" + inventory['node']
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False
		#install ceph cluster
		cmd = "ekoslet ceph init rgw:" + ceph_list['rgw'] + ":mon:" + ceph_list['mon'] + ":osd:" + ceph_list['osd']
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False
		#set ceph port
		cmd = "ekoslet cluster set rgwvip:port 7580"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		#set ceph vip
		cmd = "ekoslet cluster set rgwvip:address " + ceph_vip
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		#keygen
		info("generate keygen")
		cmd = "ekoslet keygen " + password
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False
		#install ceph
		cmd = "ekoslet ceph install >>/var/log/install_ceph.log"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		cmd ="sed -n '$'p /var/log/install_ceph.log"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False
		if "success" in rtn['stdout']:
			info('install ceph succesfully~')
		else:
			error(rtn)
			error('install ceph failed! Please check /var/log/install_ceph.log for more detail!')
			return False
		info('installing,please wait...')
		cmd = "ekoslet install >>/var/log/install_ekos.log"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False

		#check success or failed
		cmd = "sed -n '$'p /var/log/install_ekos.log"
		rtn = self.ssh_cmd(deploy_ip,username,password,cmd)
		if rtn:
			if not rtn.has_key('stdout'):
				error('ssh command failed!')
				error(rtn)
				return False
		if "success" in rtn['stdout']:
			info('install EKOS succesfully~')
			return True
		else:
			error(rtn)
			error('install EKOS failed! Please check /var/log/install_ekos.log for more detail!')
			return False

	def get_latest_build(self):
		build_server = "192.168.1.234"
		build_uername = "root"
		build_password = "P@ssw0rd1357"
		cmd = "ls -l /var/lib/docker/apps/www/ekos/Build_Backup -rt  | grep 'deploy-offline.*.tgz' | sed -n '$p' |awk '{print $9}'"
		#cmd = "ls -l /var/lib/docker/apps/www/ekos/offline -rt  | grep 'deploy-offline.*.tgz' | sed -n '$p' |awk '{print $9}'"
		rtn = self.ssh_cmd(build_server,build_uername,build_password,cmd)
		if rtn['stdout'] == None:
			error('Can not find the latest build!')
			return False
		info(rtn['stdout'])
		return rtn['stdout']

	def active_plugin(self,ip):
		#appstore
		url = "http://" + ip + ":30000/api/plugin"
		json_appstore = {"name":"appstore"}
		_ci = {"name":"ci"}
		json_network = {"name":"network"}
		json_node = {"name":"node"}
		json_registry = {"name":"registry"}
		json_stack = {"name":"stack"}
		json_storage = {"name":"storage"}
		json_tenant = {"name":"tenant"}

		plugin_lists = ["json_appstore","json_ci","json_network","json_node","json_registry","json_stack","json_storage","json_tenant"]
		for plugin in plugin_lists:
			rtn = self.call_rest_api(url,"POST",json=json.dumps(eval(plugin)))
			if json.loads(rtn)['status'] == "ok":
				info("active plugin %s successfully" % plugin)
				time.sleep(2)
			else:
				error('active plugin %s failed' % plugin)
		return True

	def active_plugin_tenant(self,ip):
		# active the tenant plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"tenant"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_image_manage(self,ip):
		# active the image_manage plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"ci"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_node(self,ip):
		# active the node plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"node"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_stack(self,ip):
		# active the stack plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"stack"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_storage(self,ip):
		# active the storage plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"storage"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_registry(self,ip):
		# active the registry plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"registry"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_network(self,ip):
		# active the network plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"network"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_appstore(self,ip):
		# active the appstore plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"appstore"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def active_plugin_logging(self,ip):
		# active the logging plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"logging"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value
	def active_plugin_monitor(self,ip):
		# active the monitor plugin
		url = "http://" + ip + ":30000/api/plugin"
		plugin = {"name":"monitor"}
		rtn = self.call_rest_api(url,"POST",json=json.dumps(plugin))
		value = json.loads(rtn)
		return value

	def admin_off(self,ip):
		# tenant console on
		url = "http://" + ip + ":30000/profile/?admin=off&current=default"
		rtn = self.call_rest_api(url, "GET")
		value = json.loads(rtn)
		return value

	def admin_on(self,ip):
		# admin console on
		url = "http://" + ip + ":30000/profile/?admin=on&current=default"
		rtn = self.call_rest_api(url, "GET")
		value = json.loads(rtn)
		return value

#-------------------------------nodes related-----------------------------------------
	
	def get_nodes_page(self,ip):
		url = "http://" + ip + ":30000/service/node/api/node"
		rtn = self.call_rest_api(url, "GET")
		value = json.loads(rtn)
		return value

	def enable_node(self,ip):
		url = "http://" + ip + ":30000/service/node/api/node/node1/schedule/enable"
		rtn = self.call_rest_api(url, "POST")
		value = json.loads(rtn)
		return value

	def disable_node(self,ip):
		url = "http://" + ip + ":30000/service/node/api/node/node1/schedule/disable"
		rtn = self.call_rest_api(url, "POST")
		value = json.loads(rtn)
		return value

	def nodes_view_log(self,ip):
		url = "http://" + ip + ":30000/service/node/api/node/install/log"
		rtn = self.call_rest_api(url, "GET")
		value = json.loads(rtn)
		return value
#-------------------------------stack related-----------------------------------------
	def add_stack(self,ip,js):
		url = "http://" + ip + ":30000/service/stack/api/stack"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value 

	def add_app(self,ip,js):
		url = "http://" + ip + ":30000/service/stack/api/app"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value 

	def app_status(self,ip,appname,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/app/detail"
		params = "namespace=" + namespace + "&name=" + appname
		cookies = self._get_cookie(ip)
		rtn = self.call_rest_api(url,"GET",params=params,cookies=cookies)
		if rtn == None:
			info('get application %s status failed!' % appname)
			return None
		else:
			return json.loads(rtn)['status'] 

	def app_status_check(self,ip,appname,namespace="default"):
		for num in range(1,7):
			rtn = self.app_status(ip, appname, namespace="default")
			if rtn == "running":
				return True
				break
			elif num == 6:
				return False
				break
			time.sleep(60)

	def add_port_mapping(self, ip,js):
		url = "http://" + ip + ":30000/service/stack/api/app/service"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value

	def update_port_mapping(self, ip,js):
		url = "http://" + ip + ":30000/service/stack/api/app/service"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value

	def config_autoscale(self, ip,js):
		url = "http://" + ip + ":30000/service/stack/api/app/autoscale"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value

	def disable_autoscale(self, ip,js):
		url = "http://" + ip + ":30000/service/stack/api/app/autoscale"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value

	def app_delete(self,ip,appname,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/app/del"
		js = {"namespace":"default"}
		js['name'] = appname
		rtn = self.call_rest_api(url,"POST",json=json.dumps(js))
		if rtn != None:
			print "delete application %s successfully!" % appname
			return True
		else:
			print "delete application %s failed" % appname
			return False

	def stack_delete(self,ip,stackname,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/stack/delete"
		js = {"namespace":"default"}
		js['name'] = stackname
		rtn = self.call_rest_api(url,"POST",json=json.dumps(js))
		if rtn != None:
			print "delete stack %s successfully!" % stackname
			return True
		else:
			print "delete stack %s failed" % stackname
			return False

#-------------------------------loadbanace related-----------------------------------------

	def add_tcp_lb(self,ip,js):
		url = "http://" + ip + ":30000/service/stack/api/balance"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value 

	def add_tcp_lb_rule(self,ip,js):
		url = "http://" + ip + ":30000/service/stack/api/balance/add/rule"
		rtn = self.call_rest_api(url,"POST",json=js)
		value = json.loads(rtn)
		return value

	def lb_status(self,ip,lb_name,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/balance/detail"
		params = "namespace=" + namespace + "&name=" + lb_name
		cookies = self._get_cookie(ip)
		rtn = self.call_rest_api(url,"GET",params=params,cookies=cookies)
		if rtn == None:
			info('get loadbanlance %s status failed!' % lb_name)
			return None
		else:
			return json.loads(rtn)['status'] 

	def lb_status_check(self,ip,lb_name,namespace="default"):
		for num in range(1,7):
			rtn = self.lb_status(ip, lb_name, namespace="default")
			if rtn == "running":
				return True
				break
			elif num == 6:
				return False
				break
			time.sleep(60)

	def lb_delete(self,ip,lb_name,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/balance/del"
		js = {}
		js['name'] = lb_name
		js['namespace'] = namespace
		rtn = self.call_rest_api(url,"POST",json=json.dumps(js))
		if rtn != None:
			if json.loads(rtn)['status'] == "success":
				info('loadbanlance %s delete successfully!' % lb_name)
				return True
			else:
				return False
		error('loadbanlance %s delete failed!' % lb_name)
		return False

#-------------------------------storage related-----------------------------------------
	def add_nfs_storage(self,ip,js,read_only= "false"):
		url = "http://" + ip + ":30000/service/storage/api/storage"
		params = "pluginname=storage"
		rtn = self.call_rest_api_second(url,"POST",params=params,json=js)
		return rtn

	def storage_status(self,ip,storage_name):
		url = "http://" + ip + ":30000/service/storage/api/storage/" + storage_name
		params = "&pluginname=storage"
		rtn = self.call_rest_api(url,"GET",params=params)
		if rtn == None:
			error("get nfs status failed")
			return False
		return json.loads(rtn)['status']

	def storage_status_check(self,ip,storage_name):
		for num in range(1,7):
			rtn = self.storage_status(ip, storage_name)
			if rtn == "ok":
				return True
				break
			elif num == 6:
				return False
				break
			time.sleep(30)

	def delete_storage(self,ip,storage_name):
		url = "http://" + ip + ":30000/service/storage/api/storage/" + storage_name
		params = "pluginname=storage"
		info('removing nfs: %s' % storage_name)
		rtn = self.call_rest_api(url,"DELETE",params=params)
		return json.loads(rtn)['result']

	def add_ceph_storage(self,ip,js,read_only= "false"):
		url = "http://" + ip + ":30000/service/storage/api/storage"
		params = "pluginname=storage"
		rtn = self.call_rest_api_second(url,"POST",params=params,json=js)
		return rtn

#-------------------------------image related-----------------------------------------

	def get_registry(self,ip):
		url = "http://" + ip + ":30000/service/registry/api/projects"
		cookies = self._get_cookie(ip)
		rtn = self.call_rest_api(url,"GET",cookies=cookies)
		if rtn != None:
			return json.loads(rtn)
		else:
			return False

	def add_registry(self,ip,js):
		url = "http://" + ip + ":30000/service/registry/api/projects"
		rtn = self.call_rest_api(url,"POST",json=js)
		if rtn == None:
			return False
		else:
			return json.loads(rtn)['project_id']

	def update_auth(self,ip,project_id):
		obj_json = {"owner_id":10000}
		url = "http://" + ip + ":30000/service/auth/api/projects/" + str(project_id)
		rtn = self.call_rest_api(url,"PUT",json=json.dumps(obj_json))
		return json.loads(rtn)

	def delete_registry(self,ip,project_id):
		url = "http://" + ip + ":30000/service/auth/api/projects/" + str(project_id)
		rtn = self.call_rest_api_second(url,"DELETE")
		return rtn

	def get_images(self,ip):
		url = "http://" + ip + ":30000/service/registry/api/repositories"
		cookies = self._get_cookie(ip)
		params = "project_id=0&q=&detail=1"
		rtn = self.call_rest_api(url,"GET",params=params,cookies=cookies)
		if rtn != None:
			return json.loads(rtn)
		else:
			return False

	def delete_image(self,ip,image):
		url = "http://" + ip + ":30000/service/registry/api/repositories" + image
		print url
		rtn = self.call_rest_api(url,"DELETE")
		if rtn != None:
			return json.loads(rtn)
		else:
			return False


#-------------------------------app related-----------------------------------------


	def create_app(self):
		pass		
	

	def delete_app(self,ip,appname,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/app/del"
		js = {"namespace":"default"}
		js['name'] = appname
		rtn = self.call_rest_api(url,"POST",json=json.dumps(js))
		if rtn != None:
			print "delete application %s successfully!" % appname
			return True
		else:
			print "delete application %s failed" % appname
			return False

	def get_app_status(self,ip,appname,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/app/detail"
		params = "namespace=" + namespace + "&name=" + appname
		cookies = self._get_cookie(ip)
		rtn = self.call_rest_api(url,"GET",params=params,cookies=cookies)
		if rtn == None:
			info('get application %s status failed!' % appname)
			return None
		else:
			return json.loads(rtn)['status']

	def check_app_status(self,ip,appname_list,namespace="default"):
		for appname in appname_list:
			rtn = self.get_app_status(ip,appname)
			if rtn != "running":
				error('application %s is in %s state!' % (appname, rtn))
				return False
		info('check app status pass!')
		return True		




	def get_nodes(self,ip,username,password):
		cmd = "kubectl get nodes |grep node* | awk '{print $1}'"
		rtn = self.ssh_cmd(ip,username,password,cmd,lines=True)
		return rtn

	def check_node_ready(self,ip,username,password):
		node_list = self.get_nodes(ip,username,password)
		for node in node_list:
			cmd = "kubectl get nodes | grep " + node + "|grep Ready"
			rtn = self.ssh_cmd(ip,username,password,cmd)
			if rtn['stdout'] == "":
				error("%s is not ready!" % node)
				return False
			info("Check %s pass" % node)
		return True

	def get_all_app(self,ip):
		node_list = []
		url = "http://" + ip + ":30000/service/stack/api/app"
		params = "namespace=default&page=1&itemsPerPage=1000"
		rtn = self.call_rest_api(url,"GET",params=params)
		for node_name in json.loads(rtn)['apps']:
			node_list.append(node_name['name'])
		if not node_list:
			info('no app running!')
			return None
		return node_list

	def get_app_service_port(self,ip,app_name):
		url = "http://" + ip + ":30000/service/stack/api/app/detail"
		params = "namespace=default&name=" + app_name
		rtn = self.call_rest_api(url,"GET",params=params)
		if rtn == None:
			return None
		service_port = json.loads(rtn)['service']['ports'][0]['servicePort']
		return service_port

	def clean_app(self,ip):
		node_list = self.get_all_app(ip)
		if node_list == None:
			return True
		for node in node_list:
			self.delete_app(ip,node)
		return True

	def download_upload_img(self,ip):
		cmd = "curl -O http://192.168.1.234:8080/ekos/stressImages/stress_centos.tgz"
		self.ssh_cmd(ip,"root","password",cmd)

		cmd = "docker load -i stress_centos.tgz"
		self.ssh_cmd(ip,"root","password",cmd)

		cmd = "docker login registry.ekos.local -uadmin -padmin12345"
		self.ssh_cmd(ip,"root","password",cmd)

		cmd = "docker push registry.ekos.local/library/stress_centos:latest"
		self.ssh_cmd(ip,"root","password",cmd)
		return True

	def change_app_replica(self,ip,app_name,replica,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/app/scale"
		obj_json = {}
		obj_json['name'] = app_name
		obj_json['namespace'] = namespace
		obj_json['replicas'] = int(replica)
		rtn = self.call_rest_api(url,"POST",json=json.dumps(obj_json))
		if rtn != None:
			if json.loads(rtn)['status'] == "success":
				info('change app %s replica to %d number successfully!' % (app_name,int(replica)))
				return True
		error('change app %s replica to %d number failed!' % (app_name,int(replica)))
		return False
	def get_app_replica(self,ip,app_name):
		url = "http://" + ip + ":30000/service/stack/api/app/detail"
		params = "namespace=default&name=" + app_name
		rtn = self.call_rest_api(url,"GET",params=params)
		if rtn == None:
			return None
		service_port = json.loads(rtn)['replicas']
		return service_port

	def k8s_pod_health_check(self,ip,user='root',pwd='password'):
		cmd = "kubectl get po --all-namespaces |grep -v 'RESTARTS'| grep -v Running"
		rtn = self.ssh_cmd(ip,user,pwd,cmd)
		if rtn.has_key('stdout'):
			if rtn['stdout'] != "":
				error('k8s pod health check failed,info:\n %s' % rtn['stdout'])
				return False
		info('k8s pod health check pass...')
		return True


#----------------------------------------lb related-----------------------------------------------------------
	def create_tcp_lb(self,ip,lb_name,listen_port,app_name,app_service_port):
		obj_json = {"name":"lb-default","namespace":"default","desc":"","tcpRules":[{"port":None,"serviceName":None,"servicePort":None}],"httpRules":[]}
		obj_json['name'] = lb_name
		obj_json['tcpRules'][0]['port'] = int(listen_port)
		obj_json['tcpRules'][0]['serviceName'] = app_name
		obj_json['tcpRules'][0]['servicePort'] = int(app_service_port)
		url = "http://" + ip + ":30000/service/stack/api/balance"
		rtn = self.call_rest_api(url,"POST",json=json.dumps(obj_json))
		if json.loads(rtn)['status'] == "success":
			info('create tcp loadbalance %s successfully!' % lb_name)
			return True
		else:
			error('create tcp loadbalance %s failed!' % lb_name)
			return False 

	def create_tcp_lb_for_each_app(self,ip,listen_port_start):
		app_list = self.get_all_app(ip)
		for app in app_list:
			lb_name = "lb-auto-" + app
			service_port = self.get_app_service_port(ip,app)
			self.create_tcp_lb(ip,lb_name,listen_port_start,app,service_port)
			listen_port_start = listen_port_start + 1
		return True

	def delete_lb(self,ip,lb_name,namespace="default"):
		url = "http://" + ip + ":30000/service/stack/api/balance/del"
		obj_json = {}
		obj_json['name'] = lb_name
		obj_json['namespace'] = namespace
		rtn = self.call_rest_api(url,"POST",json=json.dumps(obj_json))
		if rtn != None:
			if json.loads(rtn)['status'] == "success":
				info('loadbanlance %s delete successfully!' % lb_name)
				return True
		error('loadbanlance %s delete failed!' % lb_name)
		return False

	def get_all_lb_list(self,ip):
		lb_list = []
		url = "http://" + ip + ":30000/service/stack/api/balance"
		params = "namespace=default&page=1&itemsPerPage=1000"
		rtn = self.call_rest_api(url,"GET",params=params)
		for lb in json.loads(rtn)['balances']:
			lb_name = lb['name']
			lb_list.append(lb_name)
		if not lb_list:
			info('load balance is emputy!')
			return None
		return lb_list

	def delete_all_lb(self,ip):
		lb_list = self.get_all_lb_list(ip)
		if lb_list:
			for lb_name in lb_list:
				self.delete_lb(ip,lb_name)
			return True
		return False


	def check_lb_status(self,ip):
		url = "http://" + ip + ":30000/service/stack/api/balance"
		params = "namespace=default&page=1&itemsPerPage=1000"
		rtn = self.call_rest_api(url,"GET",params=params)
		for lb in json.loads(rtn)['balances']:
			lb_name = lb['name']
			lb_status = lb['status']
			if lb_status != "Running":
				error('load balance %s is in %s state' % (lb_name,lb_status))
				return False
		return True

	def clean_testbed(self,ip):
		info('cleaning testbed...')
		self.delete_all_lb(ip)
		time.sleep(5)

		self.clean_app(ip)
		time.sleep(5)

		self.remove_all_volume(ip)
		time.sleep(5)
		self.remove_all_nfs(ip)
		return True

#-----------------------------storage related-----------------------------
	def create_nfs_storage(self,ip,nfsname,nfs_server,nfs_path,read_only= "false"):
		obj_json = {}
		obj_json["storage_type"] = "nfs"
		obj_json["storage_name"] = nfsname
		obj_json["nfs_server"] = nfs_server
		obj_json["nfs_path"] = nfs_path
		obj_json["read_only"] = read_only

		url = "http://" + ip + ":30000/service/storage/api/storage"
		params = "pluginname=storage"

		rtn = self.call_rest_api(url,"POST",params=params,json=json.dumps(obj_json))
		if rtn == None:
			error("create storage failed!")
			return False
		info("create storage successfully")
		return True

	def get_nfs_status(self,ip,storage_name):
		url = "http://" + ip + ":30000/service/storage/api/storage/" + storage_name
		params = "&pluginname=storage"
		rtn = self.call_rest_api(url,"GET",params=params)
		if rtn == None:
			error("get nfs status failed")
			return False
		return json.loads(rtn)['status']

	def get_nfs_list(self,ip):
		nfs_list = []
		url = "http://" + ip + ":30000/service/storage/api/storage"
		params = "page=1&itemsPerPage=1000&pluginname=storage"
		rtn = self.call_rest_api(url,"GET",params=params)
		if rtn == None:
			error('get nfs list failed!')
			return None
		for nfs_name in json.loads(rtn)['items']:
			nfs_list.append(nfs_name['name']) 		
		if not nfs_list:
			error("there is no nfs!")
			return None
		return nfs_list

	def check_nfs_status(self,ip,name_list):
		for storage in name_list:
			rtn = self.get_nfs_status(ip,storage)
			if rtn != "ok":
				error("nfs storage %s is in %s state!" % (storage,rtn))
				return False
			info("nfs storage %s check pass!" % storage)
		return True

	def remove_nfs(self,ip,nfs_name):
		url = "http://" + ip + ":30000/service/storage/api/storage/" + nfs_name
		params = "pluginname=storage"
		info('removing nfs: %s' % nfs_name)
		self.call_rest_api(url,"DELETE",params=params)
		return True


	def create_nfs_volume(self,ip,nfs_name,volume_name,access_modes="ReadWriteMany",quantity="5Gi"):
		url = "http://" + ip + ":30000/service/storage/api/storage/pvc"
		params = "pluginname=storage"
		obj_json = {}
		obj_json['storage_name'] = nfs_name
		obj_json['pvc_name'] = volume_name
		obj_json['access_modes'] = access_modes
		obj_json['quantity'] = quantity
		rtn = self.call_rest_api(url,"POST",params=params,json=json.dumps(obj_json))
		if rtn == None:
			error('create nfs volume %s failed' % volume_name)
			return False
		info('create nfs volume %s successfully' % volume_name)
		return True

	def get_nfs_volume_name(self,ip,nfs_name):
		volume_name = []
		url = "http://" + ip + ":30000/service/storage/api/storage/" + nfs_name
		params = "&pluginname=storage"
		rtn = self.call_rest_api(url,"GET",params=params)
		if json.loads(rtn)['pvclist']['items'] == None:
			info('No volume in nfs: %s' % nfs_name)
			return None
		for volume in json.loads(rtn)['pvclist']['items']:
			volume_name.append(volume['metadata']['name'])
		if not volume_name:
			error('no volume in nfs: %s' % nfs_name)
			return None
		return volume_name

	def remove_nfs_volume(self,ip,volume_name):
		url = "http://" + ip + ":30000/service/storage/api/storage/pvc/" + volume_name
		params = "pluginname=storage"
		info('removing nfs volume: %s' % volume_name)
		rtn = self.call_rest_api(url,"DELETE",params=params)
		return True


	def remove_all_volume_per_nfs(self,ip,nfs_name):
		volume_list = self.get_nfs_volume_name(ip,nfs_name)
		if volume_list:
			for volume in volume_list:
				self.remove_nfs_volume(ip,volume)
			return True
		else:
			return False
	def remove_all_volume(self,ip):
		nfs_list = self.get_nfs_list(ip)
		if nfs_list:
			for nfs in nfs_list:
				self.remove_all_volume_per_nfs(ip,nfs)

	def remove_all_nfs(self,ip):
		nfs_list = self.get_nfs_list(ip)
		if nfs_list:
			for nfs in nfs_list:
				self.remove_nfs_volume(ip,nfs)
		return True
