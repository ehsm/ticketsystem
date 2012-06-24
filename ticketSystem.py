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
	"""cursor.execute("SELECT * FROM tickets;")
	row = cursor.fetchall()
	print row[0]
	cursor.close()
	quit()"""

def createPrintTicket(qrFile):
	return True

def randHashString():
	randData = os.urandom(128)
	return hashlib.md5(randData).hexdigest()[:15]
	
def commandCreate(args):
	if(len(args.name) > 255):
		print "Please choose a name that fits into 255 characters"
		quit()
	else:
		randString = randHashString
#		userCode = qrtools.QR(data=randString)
#		userCode.encode(filename="tmp/test2.png")
#		createPrintTicket(userCode.filename)
		dbConn = mysqlConnect()
		dbCursor = dbConn.cursor()
		print args.name
		dbCursor.execute("INSERT INTO tickets SET name=%s, code=%s;", [args.name, randString])
		dbCursor.close()
		dbConn.commit()
		dbConn.close()

def commandCheck(code):
	dbCursor = mysqlConnect()
	dbCursor.execute("SELECT name FROM tickets WHERE code="+code+";")
	rows = cursor.fetchall()
	if (len(rows) < 1):
		print "Sorry, there is no ticket registered with this code."
	elif (len(rows) > 1):
		print "Something went wrong because there are multiple tickets with this code."
	else:
		name = rows[0].name
		print "Ticket is registered on "+name
	cursor.close()

def createParser():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	# create a parser for the create subcommand and add arguments
	parserCreate = subparsers.add_parser('create')
	parserCreate.add_argument('name', type=str, help="ticket owners name")
	parserCreate.set_defaults(func=commandCreate)
	# create a parser for the check subcommand and add arguments
	parserCheck	= subparsers.add_parser('check')
	parserCheck.add_argument('code', type=str, help="identification code of the ticket")
	parserCheck.set_defaults(func=commandCheck)
	return parser

if __name__ == "__main__":
	parser = createParser()
	args = parser.parse_args()
	"""	As mentioned here: http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names
		there is no way to match any rules on peoples names so i'm stopping trying to find one.
		if (len(sys.argv) < 3 or not re.match('[a-zA-Z]+$', sys.argv[2]) or len(sys.argv[2]) > 32):"""
	args.func(args)
"""	if (args):
		if (len(parserCreate.name) > 255):
			print "Please choose a name that fits into 255 characters"
		else:
			commandCreate(parserCreate.name)
	elif (parserCheck):
		commandCheck(parserCheck.code)
	quit()"""
