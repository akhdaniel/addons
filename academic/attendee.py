from openerp.osv import osv, fields

class attendee(osv.Model):
	_name = 'academic.attendee'
	_columns = {
		'session_id'  : fields.many2one('academic.session','Session'),
		'partner_id'  : fields.many2one('res.partner','Partner'),
		'name'        : fields.char('Name', size=100),
		'course_id'	  : fields.related(
							'session_id',
							'course_id',
							type='many2one',
							relation='academic.course',
							string='Course',
							store=True)		
 	}

 	def onchange_partner(self, cr, uid, ids, partner_id):
 		partner_obj = self.pool.get('res.partner')
 		p = partner_obj.browse(cr, uid, partner_id)
 		results = {
			'value' : {
				'name' : "%05d" % p.id
			}
		}
		return results


