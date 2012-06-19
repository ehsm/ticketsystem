#!/usr/bin/python

import MySQLdb		# communicate with mysql database
import sys			# access commandline parameters, execute commands
import re			# regular expressions, obviously
import argparse		# parse commandline arguments and print help texts

def mysqlConnect():
	conn = MySQLdb.connect(	host="localhost",
							user="ehsm",
							passwd="exceptional",
							db="ehsmTickets")
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM tickets")
	row = cursor.fetchall()
	print row[0]
	cursor.close()
	quit()

def createParser():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers()
	# create a parser for the create subcommand and add arguments
	parserCreate	= subparsers.add_parser('create')
	parserCreate.add_argument('name', type=str, help="ticket owners name")
	# create a parser for the check subcommand and add arguments
	parserCheck		= subparsers.add_parser('check')
	parserCheck.add_argument('code', type=str, help="identification code of the ticket")
	return parser

if __name__ == "__main__":
	parser = createParser()
	parser.parse_args()
	"""if (len(sys.argv) < 3 or not re.match('[a-zA-Z]+$', sys.argv[2]) or len(sys.argv[2]) > 32):"""
	quit()
