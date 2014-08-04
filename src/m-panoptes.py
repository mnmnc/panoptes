#!/usr/bin/env python3
import os
import csv
import sys
import time
import hashlib
import argparse
import threading
import multiprocessing
from queue import Queue
from functools import partial
from colorama import init, Fore, Back, Style

lock = threading.Lock()
csvlock = threading.Lock()
listlock = threading.Lock()
hashlock = threading.Lock()
cpucount = multiprocessing.cpu_count()

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

def fix( my_string, size ):
	"""Makes strings to be fixed in length"""
	if len(my_string) > size:
		return my_string[:size]
	else:
		result = my_string
		for i in range( (size-len(my_string)) ):
			result = result + " "
		return result

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
	if (type(path)).__name__ == 'str':
		paths.append(path)
		return True
	elif (type(path)).__name__ == 'list':
		for _path in path:
			paths.append(_path)
		return True
	else:
		return False

def extendpathsfromarg():
	global paths
	global args
	if len(args.path) > 0:
		for p in args.path:
			if p != None:
				paths.append(p)


def showpaths():
	for path in paths:
		print( "  ",notification["INFO"], "INCLUDED PATH:", colorstring(path, "blue", "bright") )

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
	chce = "[" + colorstring("CHCE", "yellow", "bright") + "]"
	info = "[" + colorstring("INFO") + "]"
	fovr = "[" + colorstring("FOVR", "white", "bright") + "]"
	faze = "[" + colorstring("FAZE", "cyan", "bright") + "]"
	globals()['notification'] = { 
		"FAIL": fail, "SUCC":succ, "WARN":warn, 
		"CHCE": chce, "INFO":info, "FOVR":fovr, "FAZE": faze
	}
	print( notification["FAZE"], "BUILDING NOTIFICATIONS" )

def marktime():
	return time.perf_counter()

def createindex(outfile, path):

	_name = ""
	_counter = 0
	with lock:
		_name = threading.current_thread().name
	_filename = outfile + _name + ".csv"
	_mylist = []

	for root, dirs, files in os.walk(path):
		for file in files:
			_file = root + "/" + file
			try:
				_mylist.append(_file)
				_counter = _counter + 1
			except:
				pass
	print("\033[K\r" + "  ", notification["INFO"] ,"FILES FOUND:", _counter, "\tIN\t", path)
	with listlock:
		addtofilelist(_mylist)

	

def getfiledetails(filename):
	_name = ""
	_csv = ""
	with lock:
		_name = threading.current_thread().name
	try:

		_hash = gethash(filename)

		_time = time.ctime(os.path.getmtime(filename))
		_size = str(os.stat(filename).st_size)
		_csv = [filename, _hash, _time, _size]
		#print("Returning details: ", _csv)
		#_csv = 	"\"" + filename + "\"," \
		#		"\"" + _hash + "\"," \
		#		"\"" + _time + "\"," \
		#		"\"" + _size + "\",\n"
		return _csv
	except:
		return None


def worker():
	while True:
		item = queue.get()
		createindex("tst", item)
		queue.task_done()

def hashworker():

	_csv = []
	_name = ""
	with lock:
		_name = threading.current_thread().name

	while True:
		item = hashqueue.get()
		print("  ",notification["INFO"], (_name).upper(), "\tASSIGNED", len(item), "FILES TO CALCULATE HASHES")
		for _file in item:
			_line = getfiledetails(_file)
			if _line != None:
				_csv.append(_line)
		hashqueue.task_done()
		with hashlock:
			for line in _csv:
				hcsv.append(line)
			_csv.clear()
	

def csvworker():
	global hash_error_count
	global files_modified
	global files_processed

	db_list = list(csv.reader(open(outfile), delimiter=',', quotechar='"'))
	with lock:
		_name = threading.current_thread().name

	while True:
		_item = csvqueue.get()

		print("  ", notification["INFO"], (_name).upper(), "\tASSIGNED", len(_item), "HASHES TO VERIFY")
		
		for row in db_list:
			_itemindex = 0
			files_processed = files_processed + 1
			for _row in _item:
				_itemindex = _itemindex + 1
				if row[0] == _row[0]:
					if row[1] == _row[1]:
						if args.verbose == True:
							print("  ",notification["SUCC"], "HASH CHCEK FOR:", fix(row[0], 100)  )

					else:
						print("  ",notification["FAIL"], "HASH CHCEK FOR:", fix(row[0], 100)  )
						hash_error_count = hash_error_count + 1
						if args.details == True:
							hash_was = "Hash was: " + row[1]
							hash_is = " Hash is: " + _row[1]
							date_was = "Mod. date was: " + row[2]
							date_is = " Mod. date is: " + _row[2]
							size_was = "Size was: " + row[3]
							size_is = " Size is: " + _row[3]

							print("\t", Fore.WHITE +  Style.BRIGHT + fix( hash_was, 40), fix(hash_is, 40) + Fore.RESET + Style.NORMAL )
							print("\t", Fore.WHITE +  Style.BRIGHT + fix( date_was, 40), fix(date_is, 40) + Fore.RESET + Style.NORMAL )
							print("\t", Fore.WHITE +  Style.BRIGHT + fix( size_was, 40), fix(size_is, 40) + Fore.RESET + Style.NORMAL )

		csvqueue.task_done()
		print( "  ", notification["INFO"], (_name).upper(), "HASH CHECK COMPLETED.")

def verifystatus():
	global hash_error_count
	global args # CHECK IF NECESSARY

	if hash_error_count != 0:
		print(  notification["WARN"], colorstring( "Modifications detected.", "yellow", "dim"))
		if args.override == True:
			print( notification["INFO"], " Force override request detected.")
			print( notification["FOVR"], " Overriding database with new one.")
			#os.rename( newfile, outfile)
		else:
			override = input( notification["CHCE"] + " Force update database? [y]es | [E]nter to cancel: ")
			if override == "y":
				print( notification["INFO"], " Overriding database with new one.")
				#os.rename( newfile, outfile)
			else:
				print( notification["INFO"], " Override canceled.")
	else:
		print( notification["SUCC"], " System uncompromized. No changes detected.")
		#os.rename( newfile, outfile )

def createqueue(number_of_threads):
	globals()['queue'] = Queue()
	print("  ",notification["INFO"], colorstring("ADDING", "red", "bright"), number_of_threads, colorstring("THREADS", "red", "bright"))
	for i in range(number_of_threads):
		
		_thread = threading.Thread(target=worker)
		_thread.daemon = True
		_thread.start()

def createhashqueue(number_of_threads):
	globals()['hashqueue'] = Queue()
	print("  ",notification["INFO"], colorstring("ADDING", "red", "bright"), number_of_threads, colorstring("THREADS", "red", "bright"))
	for i in range(number_of_threads):
		_thread = threading.Thread(target=hashworker)
		_thread.daemon = True
		_thread.start()

def createcsvqueue(number_of_threads):
	globals()['csvqueue'] = Queue()
	print("  ",notification["INFO"], colorstring("ADDING", "red", "bright"), number_of_threads, colorstring("THREADS", "red", "bright"))
	for i in range(number_of_threads):
		_thread = threading.Thread(target=csvworker)
		_thread.daemon = True
		_thread.start()

def fillthequeue():
	for path in paths:
		queue.put(path)
	queue.join()
	print("  ",notification["INFO"], colorstring("TERMINATING THREADS", "green", "bright"))

def fillhashqueue():
	for i in range(0, len(filelist),200):
		_smalllist = list(filelist[i:i+200])
		hashqueue.put(_smalllist)
	hashqueue.join()
	print("  ",notification["INFO"], colorstring("TERMINATING THREADS", "green", "bright"))

def fillcsvqueue(number_of_threads):
	total_size = len(hcsv)
	for i in range(0, len(hcsv), int(total_size/number_of_threads)):
		_smalllist = list(hcsv[i:i+(int(total_size/number_of_threads))])
		csvqueue.put(_smalllist)
		
	csvqueue.join()
	print("  ",notification["INFO"], colorstring("TERMINATING THREADS", "green", "bright"))

def createvars():
	globals()['filelist'] = []
	globals()['filehashlist'] = []
	globals()['hcsv'] = []
	globals()['outfile'] = "mids.db"
	globals()['files_modified'] = 0
	globals()['files_processed'] = 0
	globals()['hash_error_count'] = 0


def addtofilelist(_list):
	for item in _list:
		filelist.append(item)

def printfilelist():
	for item in filelist:
		print(item)

def printhashlist():
	for item in hcsv:
		print(item[:len(item)-1])

def printcsvlist():
	for item in csv:
		print(item[:len(item)-1])

def savecsvlist(filename):
	o = open(filename, mode="w")
	for i in hcsv:
		_line = ""
		for ii in i:
			_line = _line + "\"" + ii + "\","
		o.write(_line+"\n")
	o.close()

def check_file_size(filename):
	result = 0
	try:
		result = os.stat(filename).st_size
	except FileNotFoundError:
		result = 0
	return result



def validate_system():
	global args
	if check_file_size(outfile) == 0:
		print( info + " DB not found. Creating new one.")
		#os.rename( newfile, outfile)
	else:
		print( info + " DB found. Comparison in progress.")
		db_list = list(csv.reader(open(outfile), delimiter=',', quotechar='"'))

		hash_error_count = 0

		for row in db_list:
			files_processed = files_processed + 1

def main():
	global args
	args = parseargs()

	# NOTIFICATIONS
	buildnotifications()

	# MEASURING THE EXECUTION TIME
	start = marktime()

	# PATHS SELECTED BY DEFAULT
	local_paths = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/boot", "/var/log"]
	
	# PARSING CHOOSEN PATHS
	print(notification["FAZE"], "ADDING PATHS")
	createpaths(local_paths)
	extendpathsfromarg()

	# CHECK PATHS
	showpaths()

	# CREATE QUEUE | # OF THREADS AS PARAM
	print(notification["FAZE"], "CREATING FILE LIST")
	createqueue(cpucount)

	# CREATE VARS
	createvars()

	# FILL THE QUEUE WITH TASKS
	fillthequeue()

	# CREATE HASH QUEUE
	print(notification["FAZE"], "CALCULATING HASHES FOR FILES")
	createhashqueue(cpucount)

	# FILL HASH QUEUE
	fillhashqueue()

	# CREATE CSV QUEUE
	print(notification["FAZE"], "VERIFYING HASHES")
	createcsvqueue(cpucount)

	# FILL CSV QUEUE
	fillcsvqueue(cpucount)

	# STATUS
	verifystatus()

	#savecsvlist("mids.tmp")

	# PRINTING FILELIST
	#printfilelist()
	#printcsvlist()
	#printhashlist()

	# CHECKING EXECUTION TIME
	print("executed in:", marktime()-start)

if __name__ == "__main__":
	main()