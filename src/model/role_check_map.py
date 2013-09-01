import sys, os
import re
import json

_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dir + '/..')

from lib.postgres import PG
import lib.config as cfg

class RoleCheckMap():
	pg = None
	logger = None

	def __init__(self, logger=None):
		cfg.configure(self)
		self.logger = logger
		self.pg = PG()
		self.pg.connect(self.pg_db, self.pg_user, self.pg_password, self.pg_host)


	def get_all(self):
		ret = {}
		q = """
		SELECT * FROM role_check_map
		"""
		x = self.pg.read(q)
		for row in x:
			ret[row['id']] = row

		return ret

	def get_by_role_id(self, id):
		ret = {}
		q = """
		SELECT * FROM role_check_map WHERE role_id = %s
		"""
		x = self.pg.read(q, [id])
		for row in x:
			ret[row['id']] = row

		return ret

	# WRITE approach is to do the whole batch
	def update_by_role(self, role_id, check_ids):
		statements = [
			"DELETE FROM role_check_map WHERE role_id = %s",
		]
		args = []
		for c in check_ids:
			statements.append(
				"INSERT INTO role_check_map (role_id, check_id) VALUES (%s, %s) RETURNING role_id"
			)
			args.append([role_id, c])

		x = self.pg.multi_write(statements, args)
		return x # role_id on success, False on failure



