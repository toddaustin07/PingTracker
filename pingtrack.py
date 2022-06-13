import subprocess
import socket
import platform

import os
import errno
import sys
import _thread
import time
import re
import configparser

import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

HOME_STATES={
    2: "REACHABLE",
    8: "DELAY",
    # 4: "STALE",
} 


PORTNUMBER = 50002
BRIDGEADDR = '192.168.1.140:8088'

SCANTYPE_IP = 1
SCANTYPE_ARP = 2
SCANTYPE_NONE = -1

CONFIGFILE = 'pingtrack.cfg'
LOGFILE = 'pingtrack.log'
DEVICE_LIST = []
NOTPRESENT_RETRIES = 5
PINGINTERVAL = 12


class logger(object):
	
	def __init__(self, toconsole, tofile, fname, append):
	
		self.toconsole = toconsole
		self.savetofile = tofile

		self.os = platform.system()
		if self.os == 'Windows':
			os.system('color')
		
		if tofile:
			self.filename = fname
			if not append:
				try:
					os.remove(fname)
				except:
					pass
			
	def __savetofile(self, msg):
		
		with open(self.filename, 'a') as f:
			f.write(f'{time.strftime("%c")}  {msg}\n')
	
	def __outputmsg(self, colormsg, plainmsg):
		
		if self.toconsole:
			print (colormsg)
		if self.savetofile:
			self.__savetofile(plainmsg)
	
	def info(self, msg):
		colormsg = f'\033[33m{time.strftime("%c")}  \033[96m{msg}\033[0m'
		self.__outputmsg(colormsg, msg)
		
	def warn(self, msg):
		colormsg = f'\033[33m{time.strftime("%c")}  \033[93m{msg}\033[0m'
		self.__outputmsg(colormsg, msg)
		
	def error(self, msg):
		colormsg = f'\033[33m{time.strftime("%c")}  \033[91m{msg}\033[0m'
		self.__outputmsg(colormsg, msg)
		
	def hilite(self, msg):
		colormsg = f'\033[33m{time.strftime("%c")}  \033[97m{msg}\033[0m'
		self.__outputmsg(colormsg, msg)
		
	def debug(self, msg):
		colormsg = f'\033[33m{time.strftime("%c")}  \033[37m{msg}\033[0m'
		self.__outputmsg(colormsg, msg)
		

class pingeedevice(object):
	
	def __init__(self, ipaddr, name, count, retries):
		
		self.ipaddress = ipaddr
		self.name = name
		self.pingcount = count
		self.offline_retries = retries
		self.present = 'unknown'
		self.notpresentcounter = 0
		self.skipupdates = 0
		self.os = platform.system()

	def ping(self):

		if self.os == 'Windows':
			cmd = f"ping -n {self.pingcount} {self.ipaddress}".split()
			expectedresult = f"Sent = {self.pingcount}, Received = {self.pingcount}"
		else:
			cmd = f"ping -c {self.pingcount} {self.ipaddress}".split()
			expectedresult = f"{self.pingcount} packets transmitted, {self.pingcount} received"

		pingresult = subprocess.run(cmd, shell=False, capture_output=True, text=True)
		
		if expectedresult in pingresult.stdout:
			return True
		else:
			return False

	def update_presence(self, present):
		
		self.present = present
		
	def ispresent(self):
		return self.present
		

class SourcePortAdapter(HTTPAdapter):
	""""Transport adapter" that allows us to set the source port."""
	def __init__(self, port, *args, **kwargs):
		self._source_port = port
		super(SourcePortAdapter, self).__init__(*args, **kwargs)

	def init_poolmanager(self, connections, maxsize, block=False):
		self.poolmanager = PoolManager(
			num_pools=connections, maxsize=maxsize,
			block=block, source_address=('', self._source_port))

class httprequest(object):
	
	def __init__(self, port):
		
		self.s = requests.Session()
		self.s.mount('http://', SourcePortAdapter(port))
	
	
	def send(self, url):

		HTTP_OK = 200
		
		host = re.search('//([\d.:]+)/', url).group(1)
		
		headers = { 'Host' : host,
					'Content-Type' : 'application/json'}
		
		oksent = False
	
		while oksent == False:
		
			try:
				r = self.s.post(url, headers=headers)
				
			except OSError as error:
				if OSError != errno.EADDRINUSE:
					log.error (error)
				else:
					log.error ("Address already in use; retrying")
				
				time.sleep(.250)
			else:
				oksent = True

		if r.status_code != HTTP_OK:
			log.error (f'HTTP ERROR {r.status_code} sending: {url}')
			

#-----------------------------------------------------------------------

def presence_changed(requestor, phone):
	
	if phone.skipupdates > 150:
		log.info (f'\t\t{phone.name}: Presence refreshed to = {phone.ispresent()}')
	else:
		log.hilite (f'\t\t{phone.name}: Presence changed to = {phone.ispresent()}')
	
	BASEURL = f'http://{BRIDGEADDR}'

	state = ''
	
	if phone.ispresent():
		state = 'present'
	else:
		state = 'notpresent'
	
	requestor.send(BASEURL + '/' + phone.name + '/presence/' + state)
	

############################### MAIN ###################################


CONFIG_FILE_PATH = os.getcwd() + os.path.sep + CONFIGFILE

parser = configparser.ConfigParser()
if not parser.read(CONFIG_FILE_PATH):
	print (f'\nConfig file is missing ({CONFIG_FILE_PATH})\n')
	exit(-1)
	
if parser.get('config', 'console_output').lower() == 'yes':
	conoutp = True	
else:
	conoutp = False

if parser.get('config', 'logfile_output').lower() == 'yes':
	logoutp = True
	LOGFILE = parser.get('config', 'logfile')
else:
	logoutp = False
	LOGFILE = ''
	
log = logger(conoutp, logoutp, LOGFILE, False)

pinglist = parser.get('config', 'ping_ips')
namelist = parser.get('config', 'ping_names')
countlist = parser.get('config', 'ping_count')
retrylist = parser.get('config', 'ping_offline_retries')

PINGINTERVAL = int(parser.get('config', 'ping_interval'))

pingees = pinglist.split(',')
names = namelist.split(',')
counts = countlist.split(',')
retries = retrylist.split(',')

i = 0
for pingee in pingees:
	DEVICE_LIST.append(pingeedevice(pingee.strip(), names[i].strip(), int(counts[i].strip()), int(retries[i].strip())))
	i += 1
	
PORTNUMBER = int(parser.get('config', 'port'))
BRIDGEADDR = parser.get('config', 'bridge_address')

requestor = httprequest(PORTNUMBER)

try:

	while True:
		
		log.info ('Starting scan...')

		for device in DEVICE_LIST:
			
			log.info (f'\tPinging {device.name}')
			found = device.ping()
			
			priorstate = device.ispresent()
			
			if found:
				device.update_presence(True)
				device.notpresentcounter = 0
				if priorstate != True or device.skipupdates > 150:
					presence_changed(requestor, device)
					device.skipupdates = 0
				else:
					device.skipupdates += 1
			
			else:
				device.notpresentcounter += 1
				log.debug (f'\t\t{device.name}: Not present count = {device.notpresentcounter}')
				
				if device.notpresentcounter >= device.offline_retries:
					device.update_presence(False)
					device.notpresentcounter = 0
					if priorstate != False or device.skipupdates > 150:
						presence_changed(requestor, device)
						device.skipupdates = 0
					else:
						device.skipupdates += 1
				
		time.sleep(PINGINTERVAL-.5)
		
except KeyboardInterrupt:
	log.warn ('\nAction interrupted by user...ending thread')
		
