from openerp.osv import fields, osv

class hr_holiday(osv.osv):
	_inherit = "hr.holidays"

	_columns = { 
		'holiday_type': fields.selection([('employee','By Employee'),('category','By Employee Tag')], 'Allocation Mode', help='By Employee: Allocation/Request for individual Employee, By Employee Tag: Allocation/Request for group of employees in category', required=True),
		}
hr_holiday()