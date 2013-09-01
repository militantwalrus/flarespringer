
data_defaults = {
	'user': {
		'edit': {
			'action': {
				'formname': 'edit_user',
				'displayname': 'Edit User',
				'url': '/user/edit/%d'
			}
		},
		'create': {
			'action': {
				'formname': 'create_user',
				'displayname': 'Create User',
				'url': '/user/create'
			},
			'user': {
				'username': '',
				'first_name': '',
				'last_name': '',
			}
		}
	},
	'role': {
		'edit': {
			'action': {
				'formname': 'edit_role',
				'displayname': 'Edit Role',
				'url': '/roles/edit/%d'
			}
		},
		'create': {
			'action': {
				'formname': 'create_role',
				'displayname': 'Create Role',
				'url': '/roles/create'
			},
			'role': { 'name': '' }
		}
	},
	'check': {
		'edit': {
			'action': {
				'formname': 'edit_check',
				'displayname': 'Edit Check',
				'url': '/checks/edit/%d'
			}
		},
		'create': {
			'action': {
				'formname': 'create_check',
				'displayname': 'Create Check',
				'url': '/checks/create'
			},
			'check': { 'name': '' }
		}
	},
	'rule': {
		'edit': {
			'action': {
				'formname': 'edit_rule',
				'displayname': 'Edit Rule',
				'url': '/rules/edit/%d'
			}
		},
		'create': {
			'action': {
				'formname': 'create_rule',
				'displayname': 'Create Rule',
				'url': '/rules/create'
			},
			'rule': { 'name': '' }
		}
	},

}

