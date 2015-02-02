#!/usr/bin/python3

# you can tell this program is fun
# just by looking at the modules XD
import subprocess
import threading

import traceback
import time # POC TESTER
import sys, os

# builtin imports
import importlib # to reload builtins
import imp # fallback for reloading
import pynecraft.builtins as builtins

GLOBAL_JARFILE = 'minecraft_server.1.8.1.jar'
GLOBAL_RAMALLOC = "512M"
GLOBAL_JAVAPROC = r'C:\Program Files (x86)\Java\jre7\bin\java.exe'

# TEMP: TODO: detect and add input_with_crlf function!
GLOBAL_ENDL = "\r\n"

class Logger:
	def __init__(self):
		pass
	def log_pyn(self,text):
		print("[Pynecraft] " + text)
	def log_svr(self,text):
		print("[Minecraft] " + text,end='')
	def cmdline(self):
		print("Output is ON HOLD. You may now enter a command.")
		print("\nPYN ENTRY> ", end='')
	def statement(self,text):
		print(text)

def to_bytes(val):
	return bytes(val,"ascii")
def from_bytes(val):
	return val.decode("ascii")

class OutputRelay(threading.Thread):
	def __init__(self,sproc,logger):
		threading.Thread.__init__(self)
		# set server process
		self.sproc = sproc
		self.logger = logger
		self.keepGoing = True
		self.flushOnExit = True

		self.newOutput = [] # bytes

		self._onHold = False
	def check_for_pynecmd(self,text):
		string = from_bytes(text)
		cmd = "pynecmd"
		#for i in range(len(text) - len(cmd))
		pass
	def run(self):
		sout = self.sproc.stdout
		logger = self.logger
		logger.log_pyn("Output Relay has started!")
		while self.keepGoing:
			line = sout.readline()
			if (line != b''):
				if self.check_for_pynecmd(line):
					pass
				if self._onHold:
					self.newOutput.append(line)
				else:
					logger.log_svr(from_bytes(line))
				
			#logger.cmdline()
		logger.log_pyn("Output Relay exit flush:")
		if self.flushOnExit:
			self.viewOutput()
		logger.log_pyn("Output Relay has terminated!")
	def viewOutput(self):
		count = len(self.newOutput)
		for x in range(count):
			self.logger.log_svr(from_bytes(self.newOutput.pop(0)))
	def insertIntoBuffer(self,text):
		self.newOutput.append(to_bytes(text))
	def stopIt(self):
		self.keepGoing = False
	def onHold(self):
		self._onHold = True
	def offHold(self):
		self._onHold = False

class PoCTester(threading.Thread):
	def __init__(self,sproc,logger):
		threading.Thread.__init__(self)
		# set server process
		self.sproc = sproc
		self.logger = logger
		self.keepGoing = True
	def run(self):
		sin = self.sproc.stdin
		logger = self.logger
		logger.log_pyn("PoC Tester has started!")
		while self.keepGoing:
			sin.write(to_bytes("say PoC Test Entry"+GLOBAL_ENDL))
			sin.flush()
			time.sleep(5)
			#logger.cmdline()
		logger.log_pyn("PoC Tester has terminated!")
	def stopIt(self):
		self.keepGoing = False

class InputRelay():
	def __init__(self,sproc,logger):
		# set server process
		self.sproc = sproc
		self.logger = logger
	def input_with_lf(self,cmd):
		sin = self.sproc.stdin
		sin.write(to_bytes(cmd+GLOBAL_ENDL))
		sin.flush()

class PynConsole():
	def __init__(self,sproc,logger):
		self.logger = logger
		self.sproc = sproc
		pass
	def enter_pycmd(self,cmdstr):
		cmdlis = cmdstr.split(' ')
		cmdname = cmdlis.pop(0)
		if cmdname == "genmapbytp":
			# GenMapByTP Arguments:
			# PlayerName, size=
			try:
				thread = builtins.GenMapByTP(self.sproc, self.logger)
				thread.start_with_arglist(cmdlis)
				return 0
			except:
				print(traceback.format_exc())
				return 1
		return 1 # command DNE


def main():
	print("Pynecraft Server Launcher")
	print("Copyright (C) 2015 Eric Dube, All Rights Reserved")
	print("When I'm bored I'll put this under")
	print("some good open-source license\n")

	# TODO: Make load from a config file
	#jarfile = 'minecraft_server.1.8.1.jar'
	#ramalloc = "4G"
	jarfile = GLOBAL_JARFILE
	ramalloc = GLOBAL_RAMALLOC
	javaproc = GLOBAL_JAVAPROC

	# TODO: Stop threads on exception!

	logger = Logger()

	logger.log_pyn("Starting server with " + jarfile)
	logger.log_pyn("Max RAM allocation: " + ramalloc)

	p = subprocess.Popen([
		javaproc,
		'-Xincgc',
		'-Xmx'+ramalloc,
		'-jar', jarfile
		], stdout = subprocess.PIPE, stdin = subprocess.PIPE)

	outrel = OutputRelay(p,logger)
	outrel.start()
	#poc = PoCTester(p,logger)
	#poc.start()
	inrel = InputRelay(p,logger)

	pyncon = PynConsole(p,logger)

	while True:
		logger.statement("Press ENTER at any time to start entering a command.")
		try:
			nullthing = raw_input()
		except NameError:
			nullthing = input()
		outrel.onHold()
		logger.cmdline()
		try:
			usrin = raw_input()
		except NameError:
			usrin = input()
		outrel.insertIntoBuffer("PYN RECEIVED> "+usrin+"\n")
		if usrin == 'stop':
			logger.log_pyn("Sending stop command to server!")
			inrel.input_with_lf('stop')
			outrel.stopIt()
			poc.stopIt()
			break
		elif usrin == 'refresh':
			logger.log_pyn("Updating stdout from server!")
			outrel.viewOutput()
		elif usrin == 'reloadbuiltins':
			try:
				importlib.reload(builtins)
			except AttributeError:
				imp.reload(builtins)
		else:
			if pyncon.enter_pycmd(usrin) == 1:
				logger.log_pyn("No PYN command; sending to SERVER")
				inrel.input_with_lf(usrin)
				time.sleep(0.5)
				outrel.viewOutput()
		outrel.offHold()
		outrel.viewOutput()


	logger.log_pyn("Goodbye!")


if __name__ == "__main__":
	main()