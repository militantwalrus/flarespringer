import sys, os
from HTMLParser import HTMLParser

class FSParser(HTMLParser):
	data = []

	def __init__(self):
		self.reset()
		self.data = []

	def handle_data(self, d):
	        self.data.append(d)

	def get_data(self):
		return ''.join(self.data)


class Sanitizer():

	def strip_html(self, _input):
		parser = FSParser()
		parser.feed(_input)
		return parser.get_data()



