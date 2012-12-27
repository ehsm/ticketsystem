#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 Stefan Laufmann <mail@stefanlaufmann.de>
# Licensed under GPL v3 or later

import sys            # access commandline parameters, execute commands
import argparse        # parse commandline arguments and print help texts
import os            # access urandom for "good" random numbers:
import hashlib        # provides hash functions
import re
import logging
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
from time import sleep
import StringIO
import ho.pisa as pisa
import csv
from PIL import Image, ImageDraw, ImageFont
import barcode
import popen2

import ticketSettings as config
import ticketSettingsEmail as emailconfig

class CSVRow():
    def __init__(self, row):
        self.code = row[0]
        self.name = row[1]
        self.email = row[2]
        self.ticketName = row[3]
        self.ticketPrice = row[4]
        self.ticketCurrency = row[5]

    def __str__(self):
        return self.__unicode__()

    def __unicode__(self):
        return "name: %s, email: %s, ticket: %s for %s %s" % (self.name,
                                                              self.email,
                                                              self.ticketName,
                                                              self.ticketPrice,
                                                              self.ticketCurrency)

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
    font = ImageFont.truetype(config.Ticket.FONT,config.Ticket.FONT_SIZE)
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
    if os.path.exists(pageTicketPath):
        print "File already exist %s" % (pageTicketPath)
        try:
            os.remove(pageTicketPath)
        except Exception as e:
            print e
            exit(1)
    try:
        print "Create ticket %s for %s" % (d.code, name)
        pisa.CreatePDF(StringIO.StringIO(htmlTemplate.encode('ascii', 'xmlcharrefreplace')),
                       open(pageTicketPath,'wb'))
    except:
        print "Cannot write PDF ticket to %s" % (pageTicketPath,)

def sendMails(args):
    csv = readCSV(args.file)
    try:
        server = SMTP(emailconfig.Account.HOST,emailconfig.Account.PORT,emailconfig.Account.LOCALHOST)
    except Exception as e:
        print e
        exit(1)
    #try:
    #    server.login(emailconfig.Account.USER, emailconfig.Account.PASS)
    #except Exception as e:
    #    print e
    #    exit(1)
    for row in csv:
        d = CSVRow(row)
        msg = MIMEMultipart()
        msg['Subject'] = 'Your EHSM Ticket'
        msg['From'] = 'ehsm@streibelt.net'
        msg['Reply-to'] = 'orga@ehsm.eu'
        msg['To'] = d.email

        msg.preamble = 'This is a multi-part message in MIME format.\n'

        part = MIMEText(config.Mail.TEMPLATE % (d.name.decode('utf8')),'plain','utf8')
        msg.attach(part)

        ticketPath = "%s/%s.pdf" % (config.TicketPage.OUTPUT_DIR, d.code)
        try:
            ticket = open(ticketPath,'rb').read()
        except:
            print "Cannot read ticket file %s continue" % (ticketPath,)
            continue
        part = MIMEApplication(ticket)
        part.add_header('Content-Disposition',
                        'attachment',
                        filename="%s.pdf" % (d.code,))
        msg.attach(part)

        print "send mail to %s - attachment: %s.pdf" % (d.email,d.code)
        try:
            server.sendmail(emailconfig.Account.SENDER,d.email,msg.as_string())
        except Exception as e:
            print e
            exit(1) #fail and fix the errror
        sleep(1)

    server.quit()

"""
Printer class to print piso errors to the console.
"""
class LogPrinter(logging.Handler):
    def __init__(self):
        try:
            self.file = open("log","wa")
        except Exception as e:
            print e
            exit(1)

    def emit(self, record):
        self.file.write(record + "\n")

    def __del__(self):
        self.file.close()

def readCSV(filename):
    return csv.reader(open(filename, 'rb'), delimiter=',', quotechar='"')
 
def writeCSV(filename, truncate=True):
    if truncate:
        return csv.writer(open(filename, 'wb'), delimiter=',', quotechar='"')
    else:
        return csv.writer(open(filename, 'ab'), delimiter=',', quotechar='"')

def writeCSVfile(file):
    return csv.writer(file, delimiter=',', quotechar='"')


def importCSVWireTransfer(args):
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

def importCSVGoogle(args):
    if not args.input or not args.output:
        sys.exit(1)
    inCSV = readCSV(args.input)
    outCSV = writeCSV(args.output, args.truncate)
    for line in inCSV:
        ticketName = line[28]
        ticketPrice = line[4]
        ticketCurrency = line[3]
        email = line[16]
        name = line[17]
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

def selection(kargs):
    while True:
        for k in kargs:
            print "%s -> %s" % (k,kargs[k])
        print "0  -> free form"
        sel = sys.stdin.readline().lower().strip("\n\t ")

        try:
            if int(sel) in kargs:
                return kargs[int(sel)]
            else:
                print "enter ticket name"
                ticketname = sys.stdin.readline().lower().strip("\n\t ")
                print "enter amount in euro"
                amount = ""
                while True:
                    amount = sys.stdin.readline().lower().strip("\n\t ")
                    if re.match("^[0-9]+$",amount) != None:
                        break
                    else:
                        print "not a number"
                return (ticketname,amount)
        except Exception:
            continue

def newTicket(args):
    row = []
    row.append(randHashString(12))
    print "enter name"
    name = ""
    while True:
        name = sys.stdin.readline().lower().strip("\n\t ")
        if len(name) > 0:
           break
        print "please enter name"
    row.append(name)
    print "enter mail address"
    email = ""
    while True:
        email = sys.stdin.readline().lower().strip("\n\t ")
        if re.match("[^@]+@[^@]+\.[^@]+",email) != None or len(email) == 0:
            break
        else:
            print "wrong format"
    row.append(email)
    print "enter ticket"
    ticketname,amount = selection({1:("3 day pass","100"),
               2:("3 day pass student", "50"),
               3:("day ticket", "35"),
               4:("volunteer ticket","0")})
    row.append(ticketname)
    row.append(amount)
    row.append("&euro;")

    print CSVRow(row)
    print "okay (y/n)"
    answer = sys.stdin.readline().lower().strip("\n\t ")
    if answer == "y":
        f = open(args.new,"ab")
        CSVWriter = writeCSVfile(f)
        CSVWriter.writerow(row)
        f.close()
#        createPrintTicket(CSVRow(row),False)
#        popen2.popen4("evince Ticket/%s.pdf" % row[0])
        checkTicket(row[0],args)
    else:
        print "no Ticket Created"

def checkTicket(code,args):
    if re.match("^[a-f0-9]{12}.?$",code) == None:
        print "wrong format"
        exit(1)
    if len(code) == 13: #remove parity
        code = code[:-1]

    #check if ticket is valid
    tickets = readCSV(args.input)
    invalidated_tickets = readCSV(args.output)
    ticket_exists = False
    saved_row = []
    for row in tickets:
        if row[0] == code:
            ticket_exists = True
            saved_row = row

    tickets = readCSV(args.new)
    for row in tickets:
        if row[0] == code:
            ticket_exists = True
            saved_row = row
    if not ticket_exists:
        print "Invalid Ticket"
        return


    #check if already invalidated
    invalidated = False
    for row in invalidated_tickets:
        if row[0] == code:
            invalidated = True
    if invalidated:
        print "Ticket ALREADY INVALIDATED"
        return

    r = CSVRow(saved_row)
    print(r)
    if r.ticketName == "Student Ticket":
        print "This is a STUDENT TICKET, please check id (y/n)"
        answer = sys.stdin.readline().lower().strip("\n\t ")
        if answer == "y":
            pass
        else:
            print "Ticket NOT INVALIDATED"
            return

    #write to file of invalidated tickets
    writer = writeCSV(args.output, False)
    writer.writerow(saved_row)
    print "SUCCESSFULLY INVALIDATED ticket"

def cashdesk(args):
    while True:
        print ""
        print "select option:"
        print "1 -> create new ticket"
        print "0 -> exit"
        print "or enter Ticket code"
        code = sys.stdin.readline().lower().strip("\n\t ")
        if code == "1":
            newTicket(args)
        elif code == "0":
            break
        else:
            checkTicket(code, args)


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
    parserImportCSV = subparsers.add_parser('importCSVWireTransfer')
    parserImportCSV.add_argument('-i', type=str, dest='input', help='csv file')
    parserImportCSV.add_argument('-o', type=str, dest='output', help='output csv file')
    parserImportCSV.add_argument('--truncate', action='store_true', default=False, help='truncate file instead of appending')
    parserImportCSV.set_defaults(func=importCSVWireTransfer)

    parserImportCSVGoogle = subparsers.add_parser('importCSVGoogle')
    parserImportCSVGoogle.add_argument('-i', type=str, dest='input', help='csv file')
    parserImportCSVGoogle.add_argument('-o', type=str, dest='output', help='output csv file')
    parserImportCSVGoogle.set_defaults(func=importCSVGoogle)

    parserCheckTicket = subparsers.add_parser('checkTicket')
    parserCheckTicket.add_argument('-i', type=str, dest='input', help='csv file of valid tickets')
    parserCheckTicket.add_argument('-o', type=str, dest='output', help='csv file of checked tickets')
    parserCheckTicket.add_argument('-n', type=str, dest='new', help='csv file with new tickets')
    parserCheckTicket.set_defaults(func=checkTicket)

    parserCashdesk = subparsers.add_parser('cashdesk')
    parserCashdesk.add_argument('-i', type=str, dest='input', help='csv file of valid tickets')
    parserCashdesk.add_argument('-o', type=str, dest='output', help='csv file of checked tickets')
    parserCashdesk.add_argument('-n', type=str, dest='new', help='csv file with new tickets')
    parserCashdesk.set_defaults(func=cashdesk)

    return parser

if __name__ == "__main__": 
    parser = createParser()
    args = parser.parse_args()
    logging.getLogger('ho.pisa').addHandler(LogPrinter())
    """    As mentioned here: http://www.kalzumeus.com/2010/06/17/falsehoods-programmers-believe-about-names
        there is no way to match any rules on peoples names so i'm stopping trying to find one."""
    args.func(args)        # execute the right function depending on the arguments
