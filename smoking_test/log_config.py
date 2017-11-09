# coding=utf-8

import logging
import os,sys,time,re


# logging.basicConfig(filename="/root/FunctionAutomation/ekos_auto/smoking_test/smoking.log", level=logging.INFO,
#                     format='%(asctime)s %(levelname)s %(filename)s[line:%(lineno)d]: %(message)s',
#                     datefmt='%m/%d/%Y-%H:%M:%S')

# Configure the log

STYLE = {
	'fore':
		{   # 前景色
			'black'    : 30,   #  黑色
			'red'      : 31,   #  红色
			'green'    : 32,   #  绿色
			'yellow'   : 33,   #  黄色
			'blue'     : 34,   #  蓝色
			'purple'   : 35,   #  紫红色
			'cyan'     : 36,   #  青蓝色
			'white'    : 37,   #  白色
		},

	'back' :
		{   # 背景
			'black'     : 40,  #  黑色
			'red'       : 41,  #  红色
			'green'     : 42,  #  绿色
			'yellow'    : 43,  #  黄色
			'blue'      : 44,  #  蓝色
			'purple'    : 45,  #  紫红色
			'cyan'      : 46,  #  青蓝色
			'white'     : 47,  #  白色
		},

	'mode' :
		{   # 显示模式
			'mormal'    : 0,   #  终端默认设置
			'bold'      : 1,   #  高亮显示
			'underline' : 4,   #  使用下划线
			'blink'     : 5,   #  闪烁
			'invert'    : 7,   #  反白显示
			'hide'      : 8,   #  不可见
		},

	'default' :
		{
			'end' : 0,
		},
}

def UseStyle(string, mode = '', fore = '', back = ''):

	mode  = '%s' % STYLE['mode'][mode] if STYLE['mode'].has_key(mode) else ''

	fore  = '%s' % STYLE['fore'][fore] if STYLE['fore'].has_key(fore) else ''

	back  = '%s' % STYLE['back'][back] if STYLE['back'].has_key(back) else ''

	style = ';'.join([s for s in [mode, fore, back] if s])

	style = '\033[%sm' % style if style else ''

	end   = '\033[%sm' % STYLE['default']['end'] if style else ''

	return '%s%s%s' % (style, string, end)


class Logger:
	def __init__(self, path,clevel = logging.DEBUG,Flevel = logging.DEBUG):
		self.logger = logging.getLogger("test")
		self.logger.setLevel(logging.DEBUG)
		formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S')
		#设置CMD日志
		console_output = logging.StreamHandler()
		console_output.setFormatter(formatter)
		console_output.setLevel(clevel)
		#设置文件日志
		file_log = logging.FileHandler(path, mode='w')
		file_log.setFormatter(formatter)
		file_log.setLevel(Flevel)

		self.logger.addHandler(console_output)
		self.logger.addHandler(file_log)

	def debug(self,message):
		self.logger.debug(message)

	def info(self,message):
		self.logger.info(UseStyle(message,mode = 'bold', fore = 'green'))

	def war(self,message):
		self.logger.warn(message)

	def error(self,message):
		self.logger.error(UseStyle(message,mode = 'bold', fore = 'red'))

	def cri(self,message):
		self.logger.critical(message)


# if __name__ =='__main__':
#     logyyx = Logger('yyx.log',logging.WARNING,logging.DEBUG)
#     logyyx.debug('一个debug信息')
#     logyyx.info('一个info信息')
#     logyyx.war('一个warning信息')
#     logyyx.error('一个error信息')
#     logyyx.cri('一个致命critical信息')

