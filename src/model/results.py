import sys, os
import re
import json

_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dir + '/..')

from lib.postgres import PG
import lib.config as cfg

class Results():
	pg = None
	logger = None

	def __init__(self, logger=None):
		cfg.configure(self)
		self.logger = logger
		self.pg = PG()
		self.pg.connect(self.pg_db, self.pg_user, self.pg_password, self.pg_host)


	def get_all_results(self):
		ret = {}
		q = """
		SELECT * FROM results
		"""
		x = self.pg.read(q)
		for row in x:
			row['created']  = row['created'].strftime('%Y-%m-%d %H:%M:%S')
			row['modified'] = row['modified'].strftime('%Y-%m-%d %H:%M:%S')
			ret[row['id']] = row

		return ret

	def get_result(self, id):
		ret = {}
		q = """
		SELECT * FROM results WHERE id = %s
		"""
		x = self.pg.read(q, [id])
		ret = x[0]
		ret['created']  = ret['created'].strftime('%Y-%m-%d %H:%M:%S')
		ret['modified'] = ret['modified'].strftime('%Y-%m-%d %H:%M:%S')
		return ret

	# @data  - flask request.form
	# RETURNING id trick http://www.neilconway.org/docs/sequences/
	def create_result(self, data):
		stm = """
		INSERT INTO results (check_id, results, created, modified, modified_by)
		VALUES (%s, %s, now(), now(), %s)
		RETURNING id
		"""
		args = [
			data.get('check_id'),
			data.get('results'),
			data.get('modified_by')
		]
		res = self.pg.write(stm, args)
		if res is not False:
			return res[0][0]
		return res

	def update_result(self, data):
		stm = """
		UPDATE results SET
		  check_id = %s
		  results = %s
		  modified = now()
		  modified_by = %s
		WHERE id = %s
		RETURNING id
		"""
		args = [
			data.get('check_id'),
			data.get('results'),
			data.get('modified_by'),
			data.get('id')
		]
		res = self.pg.write(stm, args)
		if res is not False:
			return res[0][0]
		return res


	def delete_result(self, data):
		stm = """
		DELETE FROM results
		WHERE id = %s
		"""
		return self.pg.write(stm, [data.get('id')])


