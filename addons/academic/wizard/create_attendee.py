from osv import osv,fields

class CreateAttendeeWizard(osv.TransientModel): 
	_name = 'academic.create.attendee.wizard' 
	_columns = {
        'session_id': fields.many2one('academic.session', 
        				'Session',
                        required=True),
        'attendee_ids': fields.one2many('academic.attendee.wizard',
                        'wizard_id', 'Attendees'),
	}

	#set default value utk session_id
	def _get_active_session(self, cr, uid, context):
		if context.get('active_model') == 'academic.session':
			return context.get('active_id', False) 
		return False
	
	_defaults = {
	        'session_id': _get_active_session,
	}

	#create method
	def action_add_attendee(self, cr, uid, ids, context=None): 
		session_model = self.pool.get('academic.session') 
		wizard = self.browse(cr, uid, ids[0], context=context) 
		session_ids = [wizard.session_id.id]
		att_data = [{'partner_id': att.partner_id.id} for att in wizard.attendee_ids] 
		session_model.write(cr, uid, session_ids,
			{'attendee_ids': [(0, 0, data) for data in att_data]},
			context) 
		return {}


	#create method
	#def action_add_attendee(self, cr, uid, ids, context=None): 
	#	attendee_model = self.pool.get('academic.attendee') 
	#	wizard = self.browse(cr, uid, ids[0], context=context) 
	#	for attendee in wizard.attendee_ids:
	#		attendee_model.create(cr, uid, {
	#            'partner_id': attendee.partner_id.id,
	#            'session_id': wizard.session_id.id,
	#		})
	#	return {}	



class AttendeeWizard(osv.TransientModel): 
	_name = 'academic.attendee.wizard' 
	_columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'wizard_id':fields.many2one('academic.create.attendee.wizard'),
    }



