import sys, os
import re
import json

_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dir + '/..')

from lib.postgres import PG
import lib.config as cfg

class Users():
	pg = None
	logger = None

	def __init__(self, logger=None):
		cfg.configure(self)
		self.logger = logger
		self.pg = PG()
		self.pg.connect(self.pg_db, self.pg_user, self.pg_password, self.pg_host)


	def get_all_users(self):
		ret = {}
		q = """
		SELECT * FROM users
		"""
		x = self.pg.read(q)
		for row in x:
			row['created'] = row['created'].strftime('%Y-%m-%d %H:%M:%S')
			row['modified'] = row['modified'].strftime('%Y-%m-%d %H:%M:%S')
			ret[row['id']] = row

		return ret

	def get_user(self, id):
		ret = {}
		q = """
		SELECT * FROM users WHERE id = %s
		"""
		print "ID: %d" % id
		x = self.pg.read(q, [id])
		print "GET USER read user"
		print repr(x)
		ret = x[0]
		ret['created']  = ret['created'].strftime('%Y-%m-%d %H:%M:%S')
		ret['modified'] = ret['modified'].strftime('%Y-%m-%d %H:%M:%S')
		return ret

	def get_by_username(self, username):
		ret = {}
		q = """
		SELECT * FROM users WHERE username = %s
		"""
		x = self.pg.read(q, [username])
		ret = x[0]
		ret['created']  = ret['created'].strftime('%Y-%m-%d %H:%M:%S')
		ret['modified'] = ret['modified'].strftime('%Y-%m-%d %H:%M:%S')
		return ret


	# @data  - flask request.form
	# RETURNING id trick http://www.neilconway.org/docs/sequences/
	def create_user(self, data):
		stm = """
		INSERT INTO users (
			username,
			password,
			first_name,
			last_name,
			created,
			modified,
			modified_by
		) VALUES (
			%s,
			%s,
			%s,
			%s,
			now(),
			now(),
			%s)
		RETURNING id
		"""
		args = [
			data.get('username'),
			data.get('password'),
			data.get('first_name'),
			data.get('last_name'),
			data.get('modified_by')
		]
		res = self.pg.write(stm, args)
		if res is not False:
			return res[0][0]
		return res

	def update_user(self, data):
		stm = """
		UPDATE users SET
		  username    = %s,
		  password    = %s,
		  first_name  = %s,
		  last_name   = %s,
		  modified    = now(),
		  modified_by = %s
		WHERE id = %s
		RETURNING id
		"""
		args = [
			data.get('username'),
			data.get('password'),
			data.get('first_name'),
			data.get('last_name'),
			data.get('modified_by'),
			data.get('id')
		]
		res = self.pg.write(stm, args)
		if res is not False:
			return res[0][0]
		return res


	def delete_user(self, data):
		stm = """
		DELETE FROM users
		WHERE id = %s
		"""
		return self.pg.write(stm, [data.get('id')])


