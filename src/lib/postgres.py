import sys, os
import psycopg2
import psycopg2.extras

class PG():

	logger = None

	def __init__(self, logger=None):
		self.logger = logger
		pass

	def connect(self, db, user, password, host):
		dsn = "dbname=%s user=%s password=%s host=%s" % (db, user, password, host)
		try:
			self.connection = psycopg2.connect(dsn)
		except Exception as e:
			print repr(e)
			#self.logger.error(e)
			sys.exit(1)

	def read(self, query, args=None):
		ret = []
		try:
			cur = self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
			cur.execute(query, args)
			ret = cur.fetchall()
		except Exception as e:
			print "POSTGRES: READ ERROR"
			print repr(e)
			#self.logger.error(e)
		finally:
			cur.close()
		return ret


	def write(self, stm, args):
		ret = True
		try:
			cur = self.connection.cursor()
			cur.execute(stm, args)
			self.connection.commit()
			ret = cur.fetchall() # get the id
		except Exception as e:
			self.connection.rollback()
			print "POSTGRES: WRITE ERROR"
			print repr(e)
			ret = False
		finally:
			cur.close()
		return ret


	# @param stmts - array of dict [{"dml": "INSERT...", "args": [...,...] }, {...}]
	# to be done in transction
	# returns FETCHALL of last statement in stms
	def multi_write(self, stmts):
		ret = [True, []]
		try:
			cur = self.connection.cursor()
			for s in enumerate(stms):
				cur.execute(s['dml'], s['args'])
				ret[1].append(cur.fetchall())
		except Exception as e:
			self.connection.rollback()
			print "POSTGRES: MULTI WRITE ERROR"
			print repr(e)
			return [False, e]

		self.connection.commit()
		return ret


	def disconnect(self):
		self.connection.close()



