#!/usr/bin/env python3

import glob
import os
import hashlib
import time
import csv
from optparse import OptionParser
import argparse
from functools import partial
from colorama import init, Fore, Back, Style

# VARIABLES
#paths = ["/bin", "/sbin", "/usr/bin", "/usr/sbin", "/boot"]
paths = ["/bin"]
outfile = "ids.db"
newfile = "ids.tmp"
files_modified = 0
files_processed = 0
fail = "["+ Fore.RED+Style.BRIGHT+" FAIL "+ Fore.RESET + Style.NORMAL + "]"
succ = "["+ Fore.GREEN+Style.BRIGHT+" SUCC "+ Fore.RESET + Style.NORMAL + "]"
info = "["+ Style.BRIGHT+" INFO " + Style.NORMAL + "]"
warn = "["+ Fore.YELLOW+Style.DIM+" WARN "+ Fore.RESET + Style.NORMAL + "]"
chce = "["+ Fore.YELLOW+Style.BRIGHT+" CHCE "+ Fore.RESET + Style.NORMAL + "]"
fovr = "["+ Fore.WHITE+Style.BRIGHT+" FOVR "+ Fore.RESET + Style.NORMAL + "]"

def nparse():
	"""Parses arguments"""
	usage = " panoptes.py [-v | --verbose | -s | --silent | -p | --paths ]"
	parser = argparse.ArgumentParser(description=usage)
	parser.add_argument('-v', "--verbose", action='store_true', default=False, help='Show output for files that passed the integrity check.')
	parser.add_argument('-d', "--details", action='store_true', default=False, help='Show detailed output for files that failed integrity check.')
	parser.add_argument('-o', "--override", action='store_true', default=False, help='This forces the creation of new database if some files will generate new hash values.')
	parser.add_argument('-p', "--path", metavar='additional_paths', default=[None], nargs='*', help='Include additional paths.')
	args = parser.parse_args()
	return args

def summary():
	print(info + " Files modified: " + str(files_modified))
	print(info + " Files analyzed: " + str(files_processed))

def fix( my_string, size ):
	"""Makes strings to be fixed in length"""
	if len(my_string) > size:
		return my_string[:size]
	else:
		result = my_string
		for i in range( (size-len(my_string)) ):
			result = result + " "
		return result

def md5sum(filename):
	"""Calculating hash."""
	with open(filename, mode='rb') as f:
		d = hashlib.sha256()
		for buf in iter(partial(f.read, 128), b''):
			d.update(buf)
	return d.hexdigest()

def check_file_size(filename):
	result = 0
	try:
		result = os.stat(filename).st_size
	except FileNotFoundError:
		result = 0
	return result

def open_file(filename):
	of = open(filename, 'w')
	return of

def create_index():
	global args
	
	of = open_file(newfile)

	if len(args.path) > 0:
		for p in args.path:
			if p != None:
				paths.append(p)

	print( info + " Creating current verification index.")
	for path in paths:
		print( info + " Processing path ", path)
		for root, dirs, files in os.walk(path):
			for file in files:
				f = root + "/" +file
				
				try:
					of.write( "\"" + os.path.join(root, file) + \
						"\",\"" + md5sum(os.path.join(root, file)) + \
						"\",\"" + time.ctime(os.path.getmtime(f)) + \
						"\",\"" + str(os.stat(f).st_size) + "\"\n")
				except:
					pass

	of.close()

def validate_index():
	global args
	global files_modified 
	global files_processed

	if check_file_size(outfile) == 0:
		print( info + " DB not found. Creating new one.")
		os.rename( newfile, outfile)
	else:
		print( info + " DB found. Comparison in progress.")

		db_list = list(csv.reader(open(outfile), delimiter=',', quotechar='"'))
		new_list = list(csv.reader(open(newfile), delimiter=',', quotechar='"'))

		hash_error_count = 0

		for row in db_list:
			files_processed = files_processed + 1
			for inner in new_list:
				if row[0] == inner[0]:
					if row[1] == inner[1]:
						if args.verbose == True:
							print( succ + " Hash check for: ", fix(row[0], 30) )

					else:
						files_modified = files_modified + 1
						if args.details == True:
							hash_was = "Hash was: " + row[1]
							hash_is = " Hash is: " + inner[1]
							date_was = "Mod. date was: " + row[2]
							date_is = " Mod. date is: " + inner[2]
							size_was = "Size was: " + row[3]
							size_is = " Size is: " + inner[3]
							print("\n" +fail+ " Hash check for: ", fix(row[0], 30)  )
							print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( hash_was, 40), fix(hash_is, 40) + Fore.RESET + Style.NORMAL )
							print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( date_was, 40), fix(date_is, 40) + Fore.RESET + Style.NORMAL )
							print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( size_was, 40), fix(size_is, 40) + Fore.RESET + Style.NORMAL )
						else:
							print( fail + " Hash check for: ", fix(row[0], 30) )

						hash_error_count = hash_error_count + 1

		print( info + " Hash check completed.")
		if hash_error_count != 0:
			print(  warn + Fore.YELLOW +  Style.DIM + " Modifications detected." + Fore.RESET + Style.NORMAL )
			if args.override == True:
				print( info + " Force override request detected.")
				print( fovr + " Overriding database with new one.")
				os.rename( newfile, outfile)
			else:
				override = input( chce + " Force update database? [y]es | [E]nter to cancel: ")
				if override == "y":
					print( info + " Overriding database with new one.")
					os.rename( newfile, outfile)
				else:
					print( info + " Override canceled.")
		else:
			print( succ + " System uncompromized. No changes detected.")
			os.rename( newfile, outfile )

def main():
	global args
	args = nparse()
	create_index()
	validate_index()
	summary()

if __name__ == "__main__":
	main()