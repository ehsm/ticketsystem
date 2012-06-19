#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Sebastian Lohff <seba@seba-geek.de>
# Licensed under GPL v3 or later

import opencv
from opencv import highgui, adaptors
from PIL import Image
import sys
import zbar


class CamReader():
	""" Captures images from a webcam and decode them.

	Captures images from the first webcam it can find, decodes them
	and writes them to stdout.
	"""
	def __init__(self, camnum=0):
		self.frame = 0

		self.reader = highgui.cvCreateCameraCapture(camnum)
		self.scanner = zbar.ImageScanner()
		self.scanner.parse_config('enable')
	
	def run(self):
		try:
			while True:
				self.frame += 1
				frame = highgui.cvQueryFrame(self.reader)
				
				frame = opencv.cvGetMat(frame)
				img = adaptors.Ipl2PIL(frame)
				width, height = img.size
				zimg = zbar.Image(width, height, 'Y800', img.convert("L").tostring())
				self.scanner.scan(zimg)
				data = None
				for symbol in zimg:
					print symbol.data
		except KeyboardInterrupt:
			print "Good bye..."

if __name__ == '__main__':
	x = CamReader(0)
	x.run()
