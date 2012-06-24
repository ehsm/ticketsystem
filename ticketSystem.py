#!/usr/bin/python

import MySQLdb		# communicate with mysql database
import sys			# access commandline parameters, execute commands
import re			# regular expressions, obviously
import argparse		# parse commandline arguments and print help texts
import qrtools		# encode and decode QR-Codes
import os			# access urandom for "good" random numbers
import hashlib		# provides hash functions

def mysqlConnect():
	"""TODO: Use ConfigParser for configuring the mysql server and user settings"""
	conn = MySQLdb.connect(	host="localhost",
							user="ehsm",
							passwd="exceptional",
							db="ehsmTickets")
	return conn

def createPrintTicket(qrFile):
	return True	

def randHashString():
	randData = os.urandom(128)
	randString = hashlib.md5(randData).hexdigest()[:15]
	return randString
	
def commandCreate(args):
	nameParts = args.name.split('=')
	name = nameParts[len(nameParts)-1]
	if(len(name) > 255):
		print "Please choose a name that fits into 255 characters"
		quit()
	else:
		randString = randHashString()
		userCode = qrtools.QR(data=randString)
		fname = "tmp/"+randString+".png"
		userCode.encode(filename=fname)
		createPrintTicket(userCode.filename)
		dbConn = mysqlConnect()
		dbCursor = dbConn.cursor()
		dbCursor.execute("INSERT INTO tickets SET name=%s, code=%s;", [name, randString])
		dbCursor.close()
		dbConn.commit()
		dbConn.close()

def commandCheck(args):
	code = qrtools.QR()
	code.decode_webcam()
	dbConn = mysqlConnect()
	dbCursor = dbConn.cursor()
#	code.data="9640f4432618567"
	dbCursor.execute("SELECT name FROM tickets WHERE code=%s;", [code.data])
	rows = dbCursor.fetchall()
	if (len(rows) < 1):
		print "Sorry, there is no ticket registered with this code."
	elif (len(rows) > 1):
		print "Something went wrong because there are multiple tickets with this code."
	else:
		name = rows[0][0]
		print "Ticket is registered on "+name
	dbCursor.close()
	dbConn.close()

def createParser():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	# create a parser for the create subcommand and add arguments and handler function
	parserCreate = subparsers.add_parser('create')
	parserCreate.add_argument('name', type=str, help="ticket owners name")
	parserCreate.set_defaults(func=commandCreate)
	# create a parser for the check subcommand and add handler function 
	parserCheck	= subparsers.add_parser('check')
	parserCheck.set_defaults(func=commandCheck)
	return parser

if __name__ == "__main__":
	parser = createParser()
	args = parser.parse_args()
	"""	As mentioned here: http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names
		there is no way to match any rules on peoples names so i'm stopping trying to find one.
		if (len(sys.argv) < 3 or not re.match('[a-zA-Z]+$', sys.argv[2]) or len(sys.argv[2]) > 32):"""
	args.func(args)