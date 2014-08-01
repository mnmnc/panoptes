#!/usr/bin/env python3
import os
import sys
import time
import hashlib
import threading
from queue import Queue
from functools import partial
from colorama import init, Fore, Back, Style

lock = threading.Lock()
listlock = threading.Lock()
hashlock = threading.Lock()

def gethash(filename, hash_designation="sha256"):
	"""
		Generate hash value for file specified with a chosen hash function. 
		Available hash functions: 
			md5, sha1, sha224, sha256 (default), sha384, sha512
	"""
	with open(filename, mode='rb') as _file:
		_hash = None
		if hash_designation == "md5":
			_hash = hashlib.md5()
		elif hash_designation == "sha1":
			_hash = hashlib.sha1()
		elif hash_designation == "sha224":
			_hash = hashlib.sha224()
		elif hash_designation == "sha384":
			_hash = hashlib.sha384()
		elif hash_designation == "sha512":
			_hash = hashlib.sha512()
		# DEFAUL"
		else :
			_hash = hashlib.sha256()
		# UPDATE
		for _buffer in iter(partial(_file.read, 128), b''):
			_hash.update(_buffer)

	return _hash.hexdigest()

def getfilesize(filename):
	"""
		Gets file size. Returns 0 if file does not exists.
	"""
	_size = 0
	try:
		_size = os.stat(filename).st_size
	except FileNotFoundError:
		_size = 0
	return _size

def fixlen(givenstring, size_desired):
	"""
		Corrects a string to have exact length.
		Long strings are truncated. 
		Short ones are padded with spaces.
	"""
	if len(givenstring) > size_desired:
		return givenstring[:size_desired]
	else:
		_string = givenstring
		for i in range(size_desired-len(givenstring)):
			_string = _string + " "
	return _string

def parseargs():
	"""
		Parses arguments given to script.
	"""
	usage = " panoptes.py [-v | --verbose | -s | --silent | -p | --paths ]"
	parser = argparse.ArgumentParser(description=usage)
	parser.add_argument('-v', "--verbose", action='store_true', default=False, help='Show output for files that passed the integrity check.')
	parser.add_argument('-d', "--details", action='store_true', default=False, help='Show detailed output for files that failed integrity check.')
	parser.add_argument('-o', "--override", action='store_true', default=False, help='This forces the creation of new database if some files will generate new hash values.')
	parser.add_argument('-p', "--path", metavar='additional_paths', default=[None], nargs='*', help='Include additional paths.')
	args = parser.parse_args()
	return args

def createpaths(path):
	"""
		Creates paths variable containing selected paths.
	"""
	globals()['paths'] = []
	#global paths
	if (type(path)).__name__ == 'str':
		paths.append(path)
		return True
	elif (type(path)).__name__ == 'list':
		for _path in path:
			paths.append(_path)
		return True
	else:
		return False

def extendpaths(path):
	"""
		Extends paths variable.
	"""
	global paths
	if (type(path)).__name__ == 'str':
		paths.append(path)
		return True
	elif (type(path)).__name__ == 'list':
		for _path in path:
			paths.append(_path)
		return True
	else:
		return False

def colorstring( _string, color="normal", style="normal"):
	_color = ''
	_style = ''
	_ct = Fore.RESET + Style.NORMAL # Color Termination

	# COLOR
	if color == "red":
		_color = Fore.RED
	elif color == "green":
		_color = Fore.GREEN
	elif color == "yellow":
		_color = Fore.YELLOW
	elif color == "cyan":
		_color = Fore.CYAN
	elif color == "magenta":
		_color = Fore.MAGENTA
	elif color == "white":
		_color = Fore.WHITE
	elif color == "black":
		_color = Fore.BLACK
	elif color == "blue":
		_color = Fore.BLUE
	elif color == "normal":
		_color = Fore.RESET
	else:
		_color = Fore.RESET
	
	# STYLE
	if style == "dim":
		_style = Style.DIM
	elif style == "bright":
		_style = Style.BRIGHT
	elif style == "normal":
		_style = Style.NORMAL
	else:
		_style = Style.NORMAL
	return _color + _style + _string + _ct

def buildnotifications():
	globals()['notification'] = {}
	fail = "[" + colorstring("FAIL", "red", "bright") + "]"
	succ = "[" + colorstring("SUCC", "green", "bright") + "]"
	warn = "[" + colorstring("WARN", "yellow", "dim") + "]"
	chce = "[" + colorstring("CHCE", "red", "bright") + "]"
	info = "[" + colorstring("INFO") + "]"
	fovr = "[" + colorstring("FOVR", "white", "bright") + "]"
	globals()['notification'] = { 
		"FAIL": fail, "SUCC":succ, "WARN":warn, 
		"CHCE": chce, "INFO":info, "FOVR":fovr
	}

def marktime():
	return time.perf_counter()

def createindex(outfile, path):

	_name = ""
	with lock:
		_name = threading.current_thread().name
	_filename = outfile + _name + ".csv"
	_mylist = []

	for root, dirs, files in os.walk(path):
		for file in files:
			_file = root + "/" + file
			try:
				#print(_filename + "\t", _file, "\t", gethash(_file))
				_mylist.append(_file)
			except:
				pass
	with listlock:
		addtofilelist(_mylist)

	print("\t\t\t\t", _name, "FINISHED", path)

def getfiledetails(filename):
	_name = ""
	with lock:
		_name = threading.current_thread().name
	try:
		_hash = gethash(filename)
		_time = time.ctime(os.path.getmtime(filename))
		_size = str(os.stat(filename).st_size)
		print( _name, filename , _hash, _time, _size)
	except:
		pass


def worker():
	print("invoking worker")
	while True:
		item = queue.get()
		print("Got item", item)
		createindex("tst", item)
		queue.task_done()

def hashworker():
	print("invoking hashworker")
	_name = ""
	with lock:
		_name = threading.current_thread().name

	while True:
		item = hashqueue.get()
		#print("Got list", item)
		for _file in item:
			getfiledetails(_file)
		hashqueue.task_done()
		print("\t\t\t\t-", _name, "FINISHED")

	

def createqueue(number_of_threads):
	globals()['queue'] = Queue()
	for i in range(number_of_threads):
		print("adding thread", i)
		_thread = threading.Thread(target=worker)
		_thread.daemon = True
		_thread.start()

def createhashqueue(number_of_threads):
	globals()['hashqueue'] = Queue()
	for i in range(number_of_threads):
		print("adding hashthread", i)
		_thread = threading.Thread(target=hashworker)
		_thread.daemon = True
		_thread.start()

def fillthequeue():
	print("filling")
	for path in paths:
		print("add", path)
		queue.put(path)
	queue.join()

def fillhashqueue():
	print("filling hashes")
	for i in range(0, len(filelist),10):
		_smalllist = list(filelist[i:i+10])
		#print("add hash", _smalllist)
		hashqueue.put(_smalllist)
	hashqueue.join()

def createlists():
	globals()['filelist'] = []
	globals()['filehashlist'] = []
	globals()['filepointer'] = 0

def addtofilelist(_list):
	for item in _list:
		filelist.append(item)

def printfilelist():
	for item in filelist:
		print(item)

def main():
	# MEASURING THE EXECUTION TIME
	start = marktime()

	local_paths = ["/bin", "/var", "/usr", "/usr/sbin", "/boot"]
	
	createpaths(local_paths)
	# CHECK PATHS
	for path in paths:
		print(path)

	buildnotifications()
	# CHECK NOTIFICATIONS
	for i in notification.keys():
		print(i, notification[i])

	# CREATE QUEUE | # OF THREADS AS PARAM
	createqueue(1)

	# CREATE LISTS
	createlists()

	# FILL THE QUEUE WITH TASKS
	fillthequeue()

	# CREATE HASH QUEUE
	createhashqueue(1)

	# FILL HASH QUEUE
	fillhashqueue()


	# PRINTING FILELIST
	#printfilelist()

	# CHECKING EXECUTION TIME
	print("executed in:", marktime()-start)

if __name__ == "__main__":
	main()