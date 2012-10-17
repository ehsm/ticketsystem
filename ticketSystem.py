#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Stefan Laufmann <mail@stefanlaufmann.de>
# Licensed under GPL v3 or later

import MySQLdb        # communicate with mysql database
import sys            # access commandline parameters, execute commands
import argparse        # parse commandline arguments and print help texts
import os            # access urandom for "good" random numbers
import hashlib        # provides hash functions
import logging
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import StringIO
import ho.pisa as pisa
import csv
from PIL import Image, ImageDraw, ImageFont
import barcode

import ticketSettings as config

class CSVRow():
    def __init__(self, row):
        self.code = row[0]
        self.name = row[1]
        self.email = row[2]
        self.ticketName = row[3]
        self.ticketPrice = row[4]
        self.ticketCurrency = row[5]

def mysqlConnect():
    conn = MySQLdb.connect(    host=config.Database.SERVER_URL,
                            user=config.Database.SERVER_USER,
                            passwd=config.Database.SERVER_PASSWORD,
                            db=config.Database.SERVER_DATABASE)
    return conn

def createPrintTicket(d, promo, **kwargs):
    canvas = Image.open(config.Ticket.TEMPLATE_FILE)

    #Generate Barcode
    code39 = barcode.get_barcode_class('code39')
    barcodeImage = code39(d.code, writer=barcode.writer.ImageWriter())
    barcodeImage = barcodeImage.render({'dpi':config.Ticket.BARCODE_DPI,'module_height':config.Ticket.BARCODE_HEIGHT})

    #Insert Barcode
    canvas.paste(barcodeImage, config.Ticket.BARCODE_POS)
    drawCanvas = ImageDraw.Draw(canvas)
    x,y = config.Ticket.BARCODE_POS
    font = ImageFont.truetype(config.Ticket.FONT,config.Ticket.BARCODE_TEXT_SIZE)
    drawCanvas.text(config.Ticket.BARCODE_TEXT_POS, d.code, (0,0,0),font=font)

    #Render Ticket Name & Price
    ticketName = d.ticketName.decode('utf8')
    ticketPrice = d.ticketPrice.decode('utf8')
    ticketCurrency = d.ticketCurrency.replace("&euro;","€").decode('utf8')
    font = ImageFont.truetype(config.Ticket.FONT, config.Ticket.FONT_SIZE)
    drawCanvas.text(config.Ticket.TICKET_NAME_POS, ticketName, (0,0,0), font=font)
    drawCanvas.text(config.Ticket.PRICE_POS, ticketPrice + " " + ticketCurrency , (0,0,0), font=font)

    #Render Name
    font = ImageFont.truetype(config.Ticket.FONT,20)
    name = d.name.decode('utf8')
    if not promo:
        printedName = name
        while True:
            (w, h) = drawCanvas.textsize(name,font=font)
            if w < config.Ticket.NAME_MAX_LENGTH:
                break
            else:
                printedName =  printedName[:-1]
        drawCanvas.text(config.Ticket.NAME_POS, printedName, (0,0,0), font=font)
    else:
        #Render Logo
        logo = Image.open(kwargs["logo"])
        if config.Ticket.LOGO_SCALE != 1:
            logo = logo.resize((int(logo.size[0] * config.Ticket.LOGO_SCALE),
                                int(logo.size[1] * config.Ticket.LOGO_SCALE)))
        canvas.paste(logo, config.Ticket.LOGO_POS)

    ticketImagePath = "%s/%s.%s" % (config.Ticket.OUTPUT_DIR,
                                    d.code,
                                    config.Ticket.OUTPUT_FORMAT)

    try:
        os.mkdir(config.Ticket.OUTPUT_DIR)
    except OSError:
        pass

    try:
        canvas.save(ticketImagePath)
    except:
        print "Cannot save ticket image to %s" % (ticketImagePath,)

    pageTicketPath = "%s/%s.pdf" % (config.TicketPage.OUTPUT_DIR, d.code)
    htmlTemplate = config.TicketPage.TEMPLATE % { 'name' : name,
                                                  'code' : d.code,
                                                  'ticket' : ticketImagePath,
                                                  'price' : ticketPrice,
                                                  'desc' : ticketName }
    try:
        os.mkdir(config.TicketPage.OUTPUT_DIR)
    except OSError:
        pass
    try:
        pisa.CreatePDF(StringIO.StringIO(htmlTemplate.encode('ascii', 'xmlcharrefreplace')),
                       open(pageTicketPath,'wb'))
    except:
       print "Cannot write PDF ticket to %s" % (pageTicketPath,)

def sendMails(args):
    csv = readCSV(args.file)
    for row in csv:
        d = CSVRow(row)
        msg = MIMEMultipart()
        msg['Subject'] = 'Your EHSM Ticket'
        msg['From'] = 'orga@ehsm.eu'
        msg['Reply-to'] = 'tickets@ehsm.eu'
        msg['To'] = d.email

        msg.preamble = 'This is a multi-part message in MIME format.\n'

        part = MIMEText(config.Mail.TEMPLATE % (d.name.decode('utf8')),'plain','utf8')
        msg.attach(part)

        ticketPath = "%s/%s.pdf" % (config.TicketPage.OUTPUT_DIR, d.code)
        try:
            ticket = open(ticketPath,'rb').read()
        except:
            print "Cannot read ticket file %s" % (ticketPath,)
        part = MIMEApplication(ticket)
        part.add_header('Content-Disposition',
                        'attachment',
                        filename="%s.pdf" % (d.code,))
        msg.attach(part)

        print msg.as_string()

"""
Printer class to print piso errors to the console.
"""
class LogPrinter(logging.Handler):
    def emit(self, record):
        print record

def readCSV(filename):
    return csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
 
def writeCSV(filename, truncate=True):
    if truncate:
        return csv.writer(open(filename, 'wb'), delimiter=',', quotechar='"')
    else:
        return csv.writer(open(filename, 'ab'), delimiter=',', quotechar='"')

def importCSV(args):
    if not args.input or not args.output:
        sys.exit(1)
    inCSV = readCSV(args.input)
    outCSV = writeCSV(args.output, args.truncate)
    for line in inCSV:
        ticketName = line[2]
        ticketPrice = line[3]
        ticketCurrency = line[4]
        email = line[6]
        name = line[7]
        code = randHashString(12)
        outCSV.writerow([code,name,email,ticketName,ticketPrice,ticketCurrency])

def createTicketFromCSV(args):
    if not args.file:
        sys.exit(0)
    csv = readCSV(args.file)
    for row in csv:
        createPrintTicket(CSVRow(row),False)

def createPromoTicketFromCSV(args):
    if not args.file:
        sys.exit(0)
    csv = readCSV(args.file)
    for row in csv:
        createPrintTicket(CSVRow(row),True, logo=args.logo)

def randHashString(length):
    randData = os.urandom(128)
    randString = hashlib.md5(randData).hexdigest()[:length]
    return randString
    
def commandInstall(args):
    dbRootPass = readfromcmdline(passwd)
    mysqlConn = MySQLdb.connect(    host=config.Database.SERVER_URL,
                                    user="root",
                                    passwd=dbRootPass)
    mysqlConn.execute('CREATE DATABASE %s ;', config.Database.SERVER_DATABASE)
    mysqlConn.execute('CREATE TABLE ticets ;')
    mysqlConn.execute('CREATE USER  %s ;', config.Database.SERVER_USER)
    mysqlConn.execute('GRANT PRIVILEGES TO %s ;', config.Database.SERVER_USER)


def commandCreate(args):
    nameParts = args.name.split('=')
    name = nameParts[len(nameParts)-1]
    if (len(name) > config.Database.NAME_LENGTH):
        print "Please choose a name that fits into %s characters" % (config.Database.NAME_LENGTH,)
        quit()
    else:
        randString = randHashString(config.Database.CODE_LENGTH)
        while checkCode(randString):
            randString = randHashString(config.Database.CODE_LENGTH)
        fname = "tmp/"+randString+".png"
        dbConn = mysqlConnect()
        dbCursor = dbConn.cursor()
        dbCursor.execute("INSERT INTO tickets SET name=%s, code=%s, used=0;", [name, randString])
        userCode = qrtools.QR(data=randString)
        userCode.encode(filename=fname)
        createPrintTicket(userCode, name)
        dbCursor.close()
        dbConn.commit()
        dbConn.close()

def commandCheck(args):
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

def markAsUsed(code):
    dbConn = mysqlConnect()
    dbCursor = dbConn.cursor()
    dbCursor.execute("UPDATE tickets SET used=1 WHERE code=%s;", code)
    dbCursor.close()
    dbConn.commit()
    dbConn.close()

def checkCode(code):
    dbConn = mysqlConnect()
    dbCursor = dbConn.cursor()
    dbCursor.execute("SELECT name, used FROM tickets WHERE code=%s;", [code])
    rows = dbCursor.fetchall()
    dbCursor.close()
    dbConn.close()
    if (len(rows) < 1):
        return None
    else:
        return rows[0]

def createParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    #Send mails with tickets
    parserSendMails = subparsers.add_parser('sendMails')
    parserSendMails.add_argument('-i', dest='file', type=str, help='csv file')
    parserSendMails.set_defaults(func=sendMails)
    #Create tickets from csv
    parserCreateCSV = subparsers.add_parser('createCSV')
    parserCreateCSV.add_argument('-i', dest='file', type=str, help='csv file')
    parserCreateCSV.set_defaults(func=createTicketFromCSV)
    #Create promotional tickets from csv
    parserPromoCreateCSV = subparsers.add_parser('createPromoCSV')
    parserPromoCreateCSV.add_argument('-i', dest='file', type=str, help='csv file')
    parserPromoCreateCSV.add_argument('-l', dest='logo', type=str, help='logo file')
    parserPromoCreateCSV.set_defaults(func=createPromoTicketFromCSV)   
    # Import data form csv
    parserImportCSV = subparsers.add_parser('importCSV')
    parserImportCSV.add_argument('-i', type=str, dest='input', help='csv file')
    parserImportCSV.add_argument('-o', type=str, dest='output', help='output csv file')
    parserImportCSV.add_argument('--truncate', action='store_true', default=False, help='truncate file instead of appending')
    parserImportCSV.set_defaults(func=importCSV)
    # create a parser for the create subcommand and add arguments and handler function
    parserCreate = subparsers.add_parser('create')
    parserCreate.add_argument('name', type=str, help="ticket owners name")
    parserCreate.set_defaults(func=commandCreate)
    # create a parser for the check subcommand and add handler function 
    parserCheck    = subparsers.add_parser('check')
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
    logging.getLogger('ho.pisa').addHandler(LogPrinter())
    """    As mentioned here: http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names
        there is no way to match any rules on peoples names so i'm stopping trying to find one."""
    args.func(args)        # execute the right function depending on the arguments
