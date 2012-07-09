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

CONF_FILE = "ticketSystem.conf"
BASE_DIR = "tmp/"

def mysqlConnect(config):
	hostname = config.get('database', 'SERVER_URL')
	username = config.get('database', 'SERVER_USER')
	userpw = config.get('database', 'SERVER_PASSWORD')
	database = config.get('database', 'SERVER_DATABASE')
	conn = MySQLdb.connect(	host=hostname,
							user=username,
							passwd=userpw,
							db=database)
	return conn

"""TODO: create tickets with LaTeX per subcommand
	Thoughts:	Put it into a seperate class?
				Read the positions of the fields from a config file as well?"""
def createPrintTicket(qrCode, name):
	return True

def randHashString(length):
	randData = os.urandom(128)
	randString = hashlib.md5(randData).hexdigest()[:length]
	return randString
	
def commandInstall(args, config):
	config = parseConfig(args.config)
	dbRootPass = readfromcmdline(passwd)
	hostname = config.get('database', 'SERVER_URL')
	mysqlConn = MySQLdb.connect(	host=hostname,
									user="root",
									passwd=dbRootPass)
	dbName = config.get('database', 'SERVER_DATABASE')
	mysqlConn.execute('CREATE DATABASE %s ;', dbName)
	mysqlConn.execute('CREATE TABLE ticets ;')
	dbUser = config.get('datbase', 'SERVER_USER')
	mysqlConn.execute('CREATE USER  %s ;', sbUser)
	mysqlConn.execute('GRANT PRIVILEGES TO %s ;', dbUser)


def commandCreate(args, config):
	nameLength = config.getint('database', 'NAME_LENGTH')
	codeLength = config.getint('database', 'CODE_LENGTH')
	nameParts = args.name.split('=')
	name = nameParts[len(nameParts)-1]
	if (len(name) > nameLength):
		print "Please choose a name that fits into "+ str(nameLength) +" characters"
		quit()
	else:
		randString = randHashString(codeLength)
		while checkCode(randString, config):
			randString = randHashString(codeLength)
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
	if not args.code:
		code = qrtools.QR()
		code.decode_webcam()
		data = code.data
	else:
		data = args.code
	dbData = checkCode(data, config)
	name = dbData[0]
	used = dbData[1]
	if not dbData:
		print "Sorry, there is no ticket registered with this code."
	elif used:
		print "Sorry, the ticket registered to " + name + " was already used."
	else:
		markAsUsed(data, config)
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
	parserCheck.add_argument("--code", help="manually give the ticket code to check for")
	parserCheck.set_defaults(func=commandCheck)
	# create a parser for an install routine
	parserInstall = subparsers.add_parser('install')
	parserInstall.add_argument('config', help="specifiy the config file to use for setting up the database")
	parserInstall.set_defaults(func=commandInstall)
	return parser

if __name__ == "__main__":
	parser = createParser()
	args = parser.parse_args()
	"""	As mentioned here: http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names
		there is no way to match any rules on peoples names so i'm stopping trying to find one."""
	config = parseConfig(CONF_FILE)	# parse the config file
	args.func(args, config)		# execute the right function depending on the arguments
