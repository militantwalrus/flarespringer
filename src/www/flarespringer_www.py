import sys, os
import re
import json
from flask import Flask, g, request, Response, render_template, flash, redirect, url_for, make_response

_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dir + '/..')

import lib.config as cfg
from lib.auth import Auth
from model.roles import Roles
from model.users import Users

class FlarespringerWWW():
	logger = None

	def __init__(self, logger=None):
		cfg.configure(self)
		self.logger = logger


	def login(self, form):
		u, p = form.get('username'), form.get('password')
		user = Users().get_by_username(u)
		print repr(user)
		if not user or not Auth().authorize_user(user, p):
			return False
		return user

	def validate_user_properties(self, form):
		if not form.get('username'):
			return [False, 'empty username']

		if form.get('password'):
			if form.get('password') != form.get('confirm_password'):
				return [False, 'passwords did not match']

		return [True, '']


	def validate_role_properties(self, form):
		if not form.get('name'):
			return [False, 'empty role name']

		return [True, '']


	def validate_rule_properties(self, form):
		if not form.get('name'):
			return [False, 'empty rule name']

		if not re.search('^\d+$', form.get('lookback')):
			return [False, 'invalid lookback - must be an integer']

		if form.get('lookback') > 100:
			return [False, 'lookback too long - limit is 100']

		if not re.search('^\d+$', form.get('rule')):
			return [False, 'invalid rule']

		return [True, '']


	def validate_check_properties(self, form):
		if not form.get('check'):
			return [False, 'empty check name']

		if not form.get('script'):
			return [False, 'empty script name']

		return [True, '']



