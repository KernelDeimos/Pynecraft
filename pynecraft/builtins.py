#!/usr/bin/python3

import threading
import time

# redundant and temporary
GLOBAL_ENDL = "\r\n"
def to_bytes(val):
	return bytes(val,"ascii")
def from_bytes(val):
	return val.decode("ascii")
class InputRelay():
	def __init__(self,sproc,logger):
		# set server process
		self.sproc = sproc
		self.logger = logger
	def input_with_lf(self,cmd):
		sin = self.sproc.stdin
		sin.write(to_bytes(cmd+GLOBAL_ENDL))
		sin.flush()
# END OF TEMP STUFF

class GenMapByTP(threading.Thread):
	def __init__(self,sproc,logger):
		threading.Thread.__init__(self)
		self.logger = logger
		self.sproc = sproc
	def log(self,text):
		self.logger.log_pyn("GenMapByTP: "+text)
	def start_with_arglist(self,arglist):
		if len(arglist) < 3:
			self.log("Usage:\ngenmapbytp <PlayerName> <Size> <delay>\nExample:\ngenmapbytp ZeroCrash16 64 2\n")
			return 1
		try:
			player = str(arglist[0])
			size = int(arglist[1])
			delay = float(arglist[2])
		except ValueError:
			self.log("Problem! Arguments must be PlayerName (TEXT) Size (INTEGER) Delay (DECIMAL)")
			return 1

		self.player = player
		self.size = size
		self.delay = delay
		self.start()
	def run(self):
		size = self.size
		player = self.player
		delay = self.delay
		self.log("Running GenMapByTP... "+self.player+","+str(self.size))
		L = 100
		xVals = int(size/L)
		zVals = int(size/L)
		runs = xVals*zVals
		r = 0
		ir = InputRelay(self.sproc,self.logger)
		for x in range(xVals):
			for z in range(zVals):
				r+=1
				self.log("Run "+str(r)+"/"+str(runs))
				posX = str(int(L*x))
				posZ = str(int(L*z))
				self.log("teleporting to "+posX+","+posZ)
				command = "tp "+self.player+" "+posX+" 255 "+posZ
				ir.input_with_lf(command)
				time.sleep(delay)
				self.log("teleporting to -"+posX+",-"+posZ)
				command = "tp "+self.player+" -"+posX+" 255 -"+posZ
				ir.input_with_lf(command)
				time.sleep(delay)