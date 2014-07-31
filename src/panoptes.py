#!/usr/bin/env python3

import glob
import os
import hashlib
import time
import csv
from functools import partial
from colorama import init, Fore, Back, Style

def fix( my_string, size ):
	if len(my_string) > size:
		return my_string[:size]
	else:
		result = my_string
		for i in range( (size-len(my_string)) ):
			result = result + " "
		return result

def md5sum(filename):
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

outfile = "ids.db"
newfile = "ids.tmp"
of = open(newfile, 'w')
be_silent_for_passed = 1

paths = ["/bin", "/sbin"]

print("Creating current verification index.")
for path in paths:
	for root, dirs, files in os.walk(path):
		for file in files:
			f = root + "/" +file
			#print(os.path.join(root, file), md5sum(os.path.join(root, file)), time.ctime(os.path.getmtime(f)) )
			try:
				#print( fix(os.path.join(root, file)), md5sum(os.path.join(root, file)), time.ctime(os.path.getmtime(f)), os.stat(f).st_size )
				of.write( "\"" + os.path.join(root, file) + \
					"\",\"" + md5sum(os.path.join(root, file)) + \
					"\",\"" + time.ctime(os.path.getmtime(f)) + \
					"\",\"" + str(os.stat(f).st_size) + "\"\n")
			except:
				pass
			
			#print( "last modified: %s" % time.ctime(os.path.getmtime(root,file)) )

of.close()

print(check_file_size(outfile))

if check_file_size(outfile) == 0:
	print("DB not found. Creating new one.")
	of.close()
	os.rename( newfile, outfile)
else:
	print("DB found. Comparison in progress.")
	db_csv = csv.reader(open(outfile), delimiter=',', quotechar='"')
	new_csv = csv.reader(open(newfile), delimiter=',', quotechar='"')
	db_list = list(db_csv)
	new_list = list(new_csv)

	hash_error_count = 0

	for row in db_list:
		for inner in new_list:
			if row[0] == inner[0]:
				
				if row[1] == inner[1]:
					if be_silent_for_passed == 0:
						print( "Hash check for: ", fix(row[0], 30) , " Passed " )

				else:
					hash_was = "Hash was: " + row[1]
					hash_is = " Hash is: " + inner[1]
					date_was = "Mod. date was: " + row[2]
					date_is = " Mod. date is: " + inner[2]
					size_was = "Size was: " + row[3]
					size_is = " Size is: " + inner[3]
					print("\nHash check for: ", fix(row[0], 30) ,  Fore.RED +  Style.BRIGHT + " Failed " + Fore.RESET + Style.NORMAL )
					print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( hash_was, 40), fix(hash_is, 40) + Fore.RESET + Style.NORMAL )
					print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( date_was, 40), fix(date_is, 40) + Fore.RESET + Style.NORMAL )
					print("\t\t", Fore.WHITE +  Style.BRIGHT + fix( size_was, 40), fix(size_is, 40) + Fore.RESET + Style.NORMAL )

					hash_error_count = hash_error_count + 1

	print(" ")
	if hash_error_count != 0:
		print(  Fore.RED +  Style.BRIGHT + "Error. Modifications detected." + Fore.RESET + Style.NORMAL )
		override = input("Force update database? [y]es / [n]o: ")
		if override == "y":
			print("Overriding database with new one.")
		else:
			print("Override canceled.")
	else:
		print("System secure.")
		os.rename( newfile, outfile )


