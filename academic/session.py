from openerp.osv import osv, fields
import time

SESSION_STATES =[('draft','Draft'),('confirmed','Confirmed'),
                 ('done','Done')]

class session(osv.Model):
	_name = "academic.session"

	def hitung(self, attendee_ids, seats):
		pct = 100.0 * len(attendee_ids)/seats
		return pct 

	# self = current object = session
	# cr   = database cursor
	# uid  = user id
	# ids  = array() record-record id 
	# field= nama field
	# arg  = argument tambahan
	def _calc_taken_seats(self, cr, uid, ids, field, arg, context=None):
		results = {}

		# browse   = ambil data dari tabel session yang punya id in ids
		# sessions = array of session objects
		sessions = self.browse(cr, uid, ids, context=context) 

		# ambil satu-per-satu sesion object 
		for session in sessions:
			if session.seats:
				results[session.id] = self.hitung(session.attendee_ids, session.seats)
			else:
				results[session.id] = 0.0

		# return harus berupa dictionary dengan key id session
		# contoh kalau 3 records:
		# {
		#      1 : 50.8,
		#      2 : 25.5,
		#      3 : 10.0
		# }
		return results

	def onchange_seats(self, cr, uid, ids, seats, attendee_ids):

		# attendee_ids yang datang dari onchange masih berupa o2m command
		# harus diconvert manjadi record dict (seolah2 udah masuk ke db)
		# ['id'] = field2 yang akan dijadikan output 
		array_of_attendees = self.resolve_o2m_commands_to_record_dicts(
			cr, uid, 'attendee_ids', attendee_ids, ['id']
		)

		# return harus berupa dict yang berisi key = 'value'
		# setiap value berupa dict yang berisi nilai dari field lain
		#   yang mau diupdate 

		results = {
			'value' : {
				'taken_seats' : self.hitung(array_of_attendees, seats)
			}
		}

		# kalau seats yang diinput < 0: warning message
		if seats < 0:
			results['warning'] = {
				'title'   : 'Warning: bad seats value',
				'message' : 'Please enter positive number'
			}
		# kalau seats yang diinput < jumlah attendee: warning message
		elif seats < len(array_of_attendees):
			results['warning'] = {
				'title'   : 'Warning: bad seats value',
				'message' : 'Please enter more seats number'
			}

		return results

	_columns = {
		'course_id'     : fields.many2one('academic.course', 'Course'),
		'instructor_id' : fields.many2one('res.partner','Instructor'),
		'name'          : fields.char('Name', size=100, required=True),
		'start_date'    : fields.date('Start Date', required=True),
		'duration'      : fields.integer('Duration'),
		'seats'         : fields.integer('Number of Seats'),
		'active'        : fields.boolean('Is Active?'),
		'attendee_ids'  : fields.one2many('academic.attendee','session_id',
			                	'Attendees', ondelete="cascade"),
		'taken_seats'   : fields.function(_calc_taken_seats, type='float', 
								string="Taken Seats"),
		'state'         : fields.selection(SESSION_STATES,'Status',readonly=True,
                                required=True),
		'image_small'   : fields.binary('Image Small')
	}


	# mau cek apakah instructor_id ada di dalam attendee_ids.partner_id
	def _cek_instruktur(self, cr, uid, ids, context=None):

		sessions = self.browse(cr, uid, ids, context=context)

		for session in sessions:
			#x = array of partner_id.id yang ada di session.attendee_ids 
			# misal x = [1,2,4,5,6,9]
			# for att in session.attendee_ids:
			# 		x.append(att.partner_id.id)
			x = [att.partner_id.id for att in session.attendee_ids]
			if session.instructor_id.id in x:
				return False 

		return True

	# constraints : [ (nama_function , message, fields) ]
	_constraints = [ (_cek_instruktur , 'Instructor cannot be Attendee' , ['instructor_id', 'attendee_ids']) ]

	_defaults = {
		'active'      : True,
		'start_date'  : lambda *a : time.strftime("%Y-%m-%d") ,
		'state'       : SESSION_STATES[0][0],
	}

	def copy(self, cr, uid, id, defaults, context=None):
		prev_session     = self.browse(cr, uid, id, context=context)
		prev_name        = prev_session.name 
		defaults['name'] = 'Copy of %s' % prev_name
		new_session = super(session, self).copy(cr, uid, id, defaults, context=context)
		return new_session

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':SESSION_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':SESSION_STATES[1][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':SESSION_STATES[2][0]},context=context)



