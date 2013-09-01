import sys, os
import re
import json
import time
from flask import Flask, g, request, Response, render_template, flash, redirect, make_response

_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(_dir + '/..')
sys.path.append(_dir + '/../..')

from flarespringer_www import FlarespringerWWW as fswww
from model.roles import Roles
from model.rules import Rules
from model.users import Users
from model.checks import Checks
from model.role_check_map import RoleCheckMap
from lib.auth import Auth
from lib.sanitizer import Sanitizer
from conf.data_defaults import *

app = Flask(__name__)
app.debug = True
app.secret_key = '6hOh6B#4r]wxEduN'

# breakout by METHOD
# http://flask.pocoo.org/docs/views/#method-views-for-apis

# see also http://flask.pocoo.org/docs/patterns/viewdecorators/
@app.before_request
def check_authorization():
	if request.path[0:7] == '/static':
		return

	# FIXME -- api basic auth?

	if request.endpoint == 'do_login':
		return

	ck = request.cookies.get(Auth().AUTH_COOKIE_NAME)
	if ck is None:
		return redirect('/login')

	g.current_user = Auth().decrypt_auth_cookie(ck)
	if not g.current_user:
		return redirect('/login')


@app.before_request
def filter_input():
 	s = Sanitizer()
 	if request.args:
 		#g.args = s.strip_html(request.args.copy())
 		g.args = request.args.copy()

 	if request.form:
 		#g.form = s.strip_html(request.form.copy())
 		g.form = request.form.copy()


@app.after_request
def do_me_last(response):
	# x= do_something_with(response.data)
	# respnose.data = x (string)
	return response


@app.route('/')
def index_action():
	return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def do_login():
	if request.method == 'GET':
		return render_template('login.html')
	if request.method == 'POST':
		user = fswww().login(g.form)
		if not user:
			flash('Invalid Login')
			return render_template('login.html')
		exp = int(time.time()) + 3600
		ck = Auth().encrypt_auth_cookie(user, exp)
		response = make_response(redirect('/'))
		response.set_cookie(Auth().AUTH_COOKIE_NAME, ck, 3600, exp, '/', None)
		return response


@app.route('/logout')
def do_logout():
	response = make_response(redirect('/'))
	response.set_cookie(Auth().AUTH_COOKIE_NAME, '', -1, -1, '/', None)
	return response


@app.route('/admin')
def do_admin():
        return render_template('admin.html')


@app.route('/users')
def list_users():
	users = Users().get_all_users()
	data = { 'users': users }
        return render_template('users.html', data=data)


@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
	data = data_defaults['user']['edit']
	data['action']['url'] = data['action']['url'] % id
	if request.method == 'GET':
		data['user'] = Users().get_user(id)
		return render_template('user_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['id'] = id
		_input['modified_by'] = g.current_user['id']
		u = Users().get_user(id)
		if 'password' in _input and _input['password']:
			_input['password'] = Auth().password_hash(_input['confirm_password'])
		else:
			_input['password'] = u['password']
		ok, messages = fswww().validate_user_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('user_form.html', data={'user': _input})
		id = Users().update_user(_input)
		if id is not False:
			url = '/users/edit/%d' % id
			flash('user updated')
			return redirect(url)

		flash('unable to update user')
		return render_template('user_form.html', data={'role': _input})



@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
	data = data_defaults['user']['create']
	if request.method == 'GET':
		return render_template('user_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['modified_by'] = g.current_user['id']
		ok, messages = fswww().validate_user_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('user_form.html', data={'user': _input})
		id = Users().create_user(_input)
		if id is not False:
			url = '/user/edit/%d' % id
			flash('user created')
			return redirect(url)

		flash('unable to create user')
		return render_template('user_form.html', data={'user': _input})


@app.route('/roles')
def list_roles():
        roles = Roles().get_all_roles()
	data = { 'roles': roles }
        return render_template('roles.html', data=data)


@app.route('/roles/create', methods=['GET', 'POST'])
def create_role():
	data = data_defaults['role']['create']
	# FIXME -- get list of checks, both associated and not
	# Checks.get_all_checks() - subtract those found by RoleCheckMap
	if request.method == 'GET':
		return render_template('role_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['modified_by'] = g.current_user['id']
		ok, messages = fswww().validate_role_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('role_form.html', data={'role': _input})

		id = Roles().create_role(_input)
		if id is False:
			flash('unable to create role')
			return render_template('role_form.html', data={'role': _input})

		id = RoleCheckMap.update_by_role(id, _input['role_checks'])
		if id is False and _input['role_checks']:
			flash('unable to set role / check mappings')
			return render_template('role_form.html', data={'role': _input})

		url = '/roles/edit/%d' % id
		flash('role created')
		return redirect(url)



@app.route('/roles/edit/<int:id>', methods=['GET', 'POST'])
def edit_role(id):
	data = data_defaults['role']['edit']
	data['action']['url'] = data['action']['url'] % id
	if request.method == 'GET':
		r = Roles().get_role(id)
		data['role'] = r[id]
		return render_template('role_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['id'] = id

		ok, messages = fswww().validate_role_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('role_form.html', data={'role': _input})

		id = Roles().update_role(_input)
		if id is not False:
			url = '/roles/edit/%d' % id
			flash('role updated')
			return redirect(url)

		flash('unable to update role')
		return render_template('role_form.html', data={'role': _input})



@app.route('/roles/delete/<int:id>')
def delete_role(id):
	if request.method == 'POST':
		data = Roles().delete_role(id)


@app.route('/rules')
def list_rules():
        rules = Rules().get_all_rules()
	data = { 'rules': rules }
        return render_template('rules.html', data=data)


@app.route('/rules/create', methods=['GET', 'POST'])
def create_rule():
	data = data_defaults['rule']['create']
	if request.method == 'GET':
		return render_template('rule_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['modified_by'] = g.current_user['id']
		ok, messages = fswww().validate_rule_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('rule_form.html', data={'rule': _input})

		id = Rules().create_rule(_input)
		if id is not False:
			url = '/rules/edit/%d' % id
			flash('rule created')
			return redirect(url)

		flash('unable to create rule')
		return render_template('rule_form.html', data={'rule': _input})


@app.route('/rules/edit/<int:id>', methods=['GET', 'POST'])
def edit_rule(id):
	data = data_defaults['rule']['edit']
	if request.method == 'GET':
		r = Rules().get_rule(id)
		data['rule'] = r[id]
		return render_template('rule_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['id'] = id

		ok, messages = fswww().validate_rule_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('rule_form.html', data={'rule': _input})

		id = Rules().update_rule(_input)
		if id is not False:
			url = '/rules/edit/%d' % id
			flash('rule updated')
			return redirect(url)

		flash('unable to update rule')
		return render_template('rule_form.html', data={'rule': _input})


@app.route('/rules/delete/<int:id>')
def delete_rule(id):
	if request.method == 'POST':
		data = Rules().delete_rule(id)


@app.route('/checks')
def list_checks():
        checks = Checks().get_all_checks()
	data = { 'checks': checks }
        return render_template('checks.html', data=data)


@app.route('/checks/create', methods=['GET', 'POST'])
def create_check():
	data = data_defaults['check']['create']
	if request.method == 'GET':
		return render_template('check_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['modified_by'] = g.current_user['id']
		ok, messages = fswww().validate_check_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('check_form.html', data={'check': _input})

		id = Checks().create_check(_input)
		if id is not False:
			url = '/checks/edit/%d' % id
			flash('check created')
			return redirect(url)

		flash('unable to create check')
		return render_template('check_form.html', data={'check': _input})


@app.route('/checks/edit/<int:id>', methods=['GET', 'POST'])
def edit_check(id):
	data = data_defaults['check']['edit']
	data['action']['url'] = data['action']['url'] % id
	if request.method == 'GET':
		r = Checks().get_check(id)
		data['check'] = r[id]
		return render_template('check_form.html', data=data)
	if request.method == 'POST':
		_input = g.form.copy()
		_input['id'] = id

		ok, messages = fswww().validate_check_properties(_input)
		if not ok:
			for m in messages:
				flash(m)
			return render_template('check_form.html', data={'check': _input})

		id = Checks().update_check(_input)
		if id is not False:
			url = '/checks/edit/%d' % id
			flash('check updated')
			return redirect(url)

		flash('unable to update check')
		return render_template('check_form.html', data={'check': _input})


@app.route('/checks/delete/<int:id>')
def delete_check(id):
	if request.method == 'POST':
		data = Checks().delete_check(id)



