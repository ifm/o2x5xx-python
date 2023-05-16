from __future__ import (absolute_import, division, print_function, unicode_literals)
from threading import Timer
import xmlrpc.client
# from .edit import *


class Session(object):
	def __init__(self, session_url, auto_heartbeat=True, auto_heartbeat_interval=10):
		self.url = session_url
		self.rpc = xmlrpc.client.ServerProxy(self.url)
		self.connected = True
		self.edit = None
		self.session = None
		if auto_heartbeat:
			self.rpc.heartbeat(auto_heartbeat_interval)
			self.autoHeartbeatInterval = auto_heartbeat_interval
			self.autoHeartbeatTimer = Timer(auto_heartbeat_interval-1, self.doAutoHeartbeat)
			self.autoHeartbeatTimer.start()
		else:
			self.rpc.heartbeat(300)

	def __del__(self):
		self.cancelSession()

	def cancelSession(self):
		if self.autoHeartbeatTimer:
			self.autoHeartbeatTimer.cancel()
			self.autoHeartbeatTimer.join()
			self.autoHeartbeatTimer = None
		if self.connected:
			self.rpc.cancelSession()
			self.connected = False

	def setOperatingMode(self, mode):
		if mode == 0:
			self.stopEdit()
		elif mode == 1:
			return self.startEdit()
		else:
			raise ValueError("Invalid operating mode")

	# def startEdit(self):
	# 	self.rpc.setOperatingMode(1)
	# 	self.edit = Edit(self.url + 'edit/')
	# 	return self.edit

	def stopEdit(self):
		self.rpc.setOperatingMode(0)
		self.edit = None

	def doAutoHeartbeat(self):
		newHeartbeatInterval = self.rpc.heartbeat(self.autoHeartbeatInterval)
		self.autoHeartbeatInterval = newHeartbeatInterval
		# schedule event a little ahead of time
		self.autoHeartbeatTimer = Timer(self.autoHeartbeatInterval-1, self.doAutoHeartbeat)
		self.autoHeartbeatTimer.start()

	def __getattr__(self, name):
		# Forward otherwise undefined method calls to XMLRPC proxy
		return getattr(self.rpc, name)
