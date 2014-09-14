from osv import osv,fields

class CreateAttendeeWizard(osv.TransientModel): 
	_name = 'academic.create.attendee.wizard' 
	_columns = {
		'session_ids'   : fields.many2many(
			'academic.session', 	# 'other.object.name' dengan siapa dia many2many
			'session_attendee',     # 'relation object'
			'wizard_id',            # 'actual.object.id' in relation table
			'session_id',           # 'other.object.id' in relation table
			'Session',              # 'Field Name'
			required=True),
        'attendee_ids': fields.one2many('academic.attendee.wizard',
                            'wizard_id', 'Attendees'),
	}

	#set default value utk session_ids
	def _get_active_sessions(self, cr, uid, context):
		if context.get('active_model') == 'academic.session':
			return context.get('active_ids', False) 
		return False
	
	_defaults = {
		'session_ids': _get_active_sessions,
	}

	#create method
	def action_add_attendee(self, cr, uid, ids, context=None): 
		session_model = self.pool.get('academic.session') 
		wizard = self.browse(cr, uid, ids[0], context=context) 
		session_ids = [sess.id for sess in wizard.session_ids]
		att_data = [{'partner_id': att.partner_id.id, 'name': "%05d" % att.partner_id.id} 
				for att in wizard.attendee_ids] 
		session_model.write(cr, uid, session_ids,
			{'attendee_ids': [(0, 0, data) for data in att_data]},
			context) 
		return {}

class AttendeeWizard(osv.TransientModel): 
	_name = 'academic.attendee.wizard' 
	_columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'wizard_id':fields.many2one('academic.create.attendee.wizard'),
    }



