
import sys, os, re
import json
import ConfigParser


def configure(obj):

	conf_dir = os.path.dirname(os.path.realpath(__file__)) + '/../../conf/'

	name = obj.__class__.__name__

	# conf file - try ini first, then json
	conf_file = conf_dir + 'config.ini'
	c = get_config(conf_file)

	for section in c:
		for k in c[section]:
			setattr(obj, k, c[section][k])

	a = cli_args()
	for arg in a:
		setattr(obj, arg, a[arg])



def get_config(conf_file):
	try:
		if re.search(r'\.json$', conf_file):
			return __get_json_config(conf_file)
		elif re.search(r'\.(ini|properties)$', conf_file):
			return __get_ini_config(conf_file)
		else:
			m = sys._getframe(1).f_code.co_name + \
				"no conf file found for: [%s]" % conf_file
			print m
	except Exception as e:
		print conf_file + ' ' + repr(e)
		return {}


def __get_json_config(conf_file):
	with open(conf_file) as fd:
		data = fd.read()
		return json.loads(data)


def __get_ini_config(conf_file):
	cp = ConfigParser.ConfigParser()
	cp.read(conf_file)
	return {s: {i[0]: i[1] for i in cp.items(s)} for s in cp.sections()}



def cli_args():
	ret = {}
	for k, v in zip(sys.argv[1::2], sys.argv[2::2]):
		if re.match('--\w+', k):
			ret[k.lstrip('-')] = v
	return ret


if __name__ == '__main__':
	c = get_config(sys.argv[1])
	print repr(c)

