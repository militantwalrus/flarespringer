import sys, os
import json
import requests

import config as cfg

class RunCheck():

	def __init__(self):
		self.sanity_check()
		self.run_script()

	def sanity_check(self):
		if len(sys.argv) < 1:
			# print stderr 'wrong args'
			sys.exit(1)

		# FIXME -- check execute bit

	def run_script():
		check = sys.argv[1] # shift
		os.system(check, sys.argv[1:])



if __name__ == '__main__':
	RunCheck()

