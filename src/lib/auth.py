import hashlib
import uuid
import json
import zlib
import base64
from Crypto.Cipher import AES

class Auth():

	SALT_LENGTH = 24
	AUTH_COOKIE_NAME = 'fl_a_ck'
	MAGIC = 'ErCWTDub{BpUbH}33xU%#OaMCS=`5Q_G' # must not include a '|'
	IV = 's!XrHd}ro *gLyR('

  	"""
	password hash -- call it with no _compare arg
	to get the original one to store in the db
	for login, call it with the user's entered plaintext
	pass on the first arg, and the db pass value for
	the _compare arg.

	In code this becomes
	if db_pass_value == password_hash(user_entered_raw, db_pass_value):
	     .... success ....

	So when querying DB to login, just pick up the row
	by the username, and don't check the pass in the sql
	"""
	def password_hash(self, _str, _compare = None):
		if _compare is None:
			salt = hashlib.md5(str(uuid.uuid4())).hexdigest()[:self.SALT_LENGTH]
		else:
			salt = _compare[:self.SALT_LENGTH]

		return salt + hashlib.sha1(salt + _str).hexdigest()


	def authorize_user(self, user, password):
		if user['password'] == self.password_hash(password, user['password']):
			return True
		return False


	# base64 encoding, plus translation of url-unsafe chars
	def transport_encode(self, val):
		tmp = base64.b64encode(val)
		tmp = tmp.replace('+', '-')
		tmp = tmp.replace('/', '_')
		return tmp.replace('=', '.')

	# base64 decoding, plus translation back into url-unsafe chars
	def transport_decode(self, val):
		tmp = val.replace('-', '+')
		tmp = tmp.replace('_', '/')
		tmp = tmp.replace('.', '=')
		return base64.b64decode(tmp)


	# @param dict user - dict of user from db
	# @param int expiration - unix timestamp
	def encrypt_auth_cookie(self, user, expiration):
		data = json.dumps(user)
		a    = "%s|%x" % (user['username'], expiration)
		b    = a + '|' + data + '|' + self.MAGIC
		k    = hashlib.sha1(a).hexdigest()[:16]
		blob = AES.new(self.MAGIC, AES.MODE_CFB, k).encrypt(b)
		ck   = a + '|' + str(zlib.crc32(data)) + '|' + self.transport_encode(blob)
		ck = AES.new(self.MAGIC, AES.MODE_CFB, self.MAGIC[:16]).encrypt(ck)
		return self.transport_encode(ck)


	# @param string ck - Flarespringer auth cookie value
	def decrypt_auth_cookie(self, ck):
		tmp = self.transport_decode(ck)
		tmp = AES.new(self.MAGIC, AES.MODE_CFB, self.MAGIC[:16]).decrypt(tmp)
		try:
			username, exp, data_crc32, blob = tmp.split('|')
		except Exception as e:
			print "BAD split"
			return False

		a = "%s|%x" % (username, int(exp, 16))
		k = hashlib.sha1(a).hexdigest()[:16]
		tmp2 = AES.new(self.MAGIC, AES.MODE_CFB, k).decrypt(self.transport_decode(blob))

		try:
			u2, exp2, data, sk = tmp2.split('|')
		except Exception as e:
			print "BAD split 2"
			print tmp2
			return False

		if u2 != username:
			print "%s != %s" % (u2, username)
			return False

		if exp2 != exp:
			print "%s != %s" % (exp2, exp)
			return False

		if str(zlib.crc32(data)) != data_crc32:
			print "%s != %s" % (str(zlib.crc32(data)), data_crc32)
			return False

		if sk.strip() != self.MAGIC:
			print "%s != %s" % (sk.strip(), self.MAGIC)
			return False

		# return user dict
		return json.loads(data)


	def create_auth_cookie():
		pass


	def check_auth_cookie():
		pass

