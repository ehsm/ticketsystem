#!/usr/bin/python
#
# Copyright (C) 2012 Stefan Laufmann <mail@stefanlaufmann.de>
# Licensed under GPL v3 or later

import MySQLdb		# communicate with mysql database
import sys			# access commandline parameters, execute commands
import argparse		# parse commandline arguments and print help texts
import qrtools		# encode and decode QR-Codes
import os			# access urandom for "good" random numbers
import hashlib		# provides hash functions
import ConfigParser	# parse config files to set database settings

CONF_FILE = "dbAuth.conf"
BASE_DIR = "tmp/"

def mysqlConnect(config):
	hostname = config.get('ticketSystem', 'SERVER_URL')
	username = config.get('ticketSystem', 'SERVER_USER')
	userpw = config.get('ticketSystem', 'SERVER_PASSWORD')
	database = config.get('ticketSystem', 'SERVER_DATABASE')
	conn = MySQLdb.connect(	host=hostname,
							user=username,
							passwd=userpw,
							db=database)
	return conn

"""TODO: create tickets with LaTeX per subcommand
	Thoughts:	Put it into a seperate class?
				Read the positions of the fields from a config file as well?"""
def createPrintTicket(qrCode, name):
	filepath = os.path.join(BASE_DIR, qrCode.data + ".tmp")
	file = open(filepath, 'w')
	file.write(r"""
\documentclass{article}

\usepackage[papersize={9cm,6cm}, margin=0cm]{geometry}
\usepackage[utf8]{inputenc}
\usepackage[ngerman]{babel}
\usepackage{graphicx}
\usepackage{overpic}
% use DejaVuSans as default font
\usepackage{DejaVuSans}
\renewcommand*\familydefault{\sfdefault} %% Only if the base font of the document is to be sans serif
\usepackage[T1]{fontenc}

\begin{document}
	\centering
	\begin{overpic}[width=9cm]{ticketEntwurf}
		\put(5,25){\huge{""" + name + """}}	
	\end{overpic}
\end{document}
""")

def randHashString():
	randData = os.urandom(128)
	randString = hashlib.md5(randData).hexdigest()[:16]
	return randString
	
def commandCreate(args, config):
	nameParts = args.name.split('=')
	name = nameParts[len(nameParts)-1]
	if len(name) > 32:
		print "Please choose a name that fits into 32 characters"
		quit()
	else:
		randString = randHashString()
		while checkCode(randString, config):
			randString = randHashString()
		fname = "tmp/"+randString+".png"
		dbConn = mysqlConnect(config)
		dbCursor = dbConn.cursor()
		dbCursor.execute("INSERT INTO tickets SET name=%s, code=%s, used=0;", [name, randString])
		userCode = qrtools.QR(data=randString)
		userCode.encode(filename=fname)
		createPrintTicket(userCode, name)
		dbCursor.close()
		dbConn.commit()
		dbConn.close()

def commandCheck(args, config):
	code = qrtools.QR()
	code.decode_webcam()
	dbData = checkCode(code.data, config)
	name = dbData[0]
	used = dbData[1]
	if not dbData:
		print "Sorry, there is no ticket registered with this code."
	elif used:
		print "Sorry, the ticket registered to " + name + " was already used."
	else:
		markAsUsed(code.data, config)
		print "Ticket is registered on " + name
		print "Ticket was marked as used."

def markAsUsed(code, config):
	dbConn = mysqlConnect(config)
	dbCursor = dbConn.cursor()
	dbCursor.execute("UPDATE tickets SET used=1 WHERE code=%s;", code)
	dbCursor.close()
	dbConn.commit()
	dbConn.close()

def checkCode(code, config):
	dbConn = mysqlConnect(config)
	dbCursor = dbConn.cursor()
	dbCursor.execute("SELECT name, used FROM tickets WHERE code=%s;", [code])
	rows = dbCursor.fetchall()
	dbCursor.close()
	dbConn.close()
	if (len(rows) < 1):
		return None
	else:
		return rows[0]

def parseConfig(confFile):
	config = ConfigParser.SafeConfigParser()
	config.read(confFile)
	return config

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
		there is no way to match any rules on peoples names so i'm stopping trying to find one."""
	config = parseConfig(CONF_FILE)
	args.func(args, config)		# execute the right function depending on the arguments
