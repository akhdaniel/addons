from openerp.osv import osv, fields

class course(osv.Model):
	_name = 'academic.course'
	_columns = {
		'name'           : fields.char('Name', size=100, required=True),
		'description'    : fields.text('Description'),
		'responsible_id' : fields.many2one('res.users', string='Responsible'),
		'session_ids'    : fields.one2many('academic.session','course_id', 
			                   'Sessions', ondelete="cascade")
	}


