from openerp.osv import osv,fields
from openerp import tools
from datetime import date

class hr_employee(osv.Model):
	_name = 'hr.employee'
	_inherit = 'hr.employee'

	_columns = {
		'date_inactive' : fields.date('Date Inactive', readonly=True),
	}

	def write(self, cr, uid, ids, vals, context=None):
		if any('active' in ac for ac in vals):
			if vals['active']==False:
				vals['date_inactive'] = date.today()
			elif vals['active']==True:
				vals['date_inactive'] = False
		return super(hr_employee,self).write(cr, uid, ids, vals, context=None)

hr_employee()

class hr_turnover_report(osv.Model):
	_name = 'hr.turnover.report'
	_auto = False

	_columns = {
		'department_id' : fields.many2one('hr.department', 'Department', readonly=True),
		'nbr' : fields.integer('# Employee', readonly=True),
		'total': fields.integer('Total', readonly=True),
		'th': fields.char('Tahun', readonly=True,size=10),
		'bln': fields.char('Bulan', readonly=True,size=10),
		'status' : fields.selection([('masuk','Masuk'),('keluar','Keluar')],'Status'),
		# 'persentase': fields.function(_percentInOut,),
		# 'th_keluar': fields.char('Tahun Keluar', readonly=True,size=10),
		# 'bln_keluar': fields.char('Bulan Keluar', readonly=True,size=10),
		# 'masuk' : fields.integer('Masuk', readonly=True),
		# 'keluar': fields.integer('Keluar', readonly=True),
	}

	def init(self, cr):

		"""
		hrd_turnover Report
		@param cr: the current row, from the database cursor
		"""
		tools.drop_view_if_exists(cr, 'hr_turnover_report')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_turnover_report AS (
				SELECT
					e.id,
					e.department_id,
					to_char(date_trunc('year',coalesce(e.date_inactive,e.create_date)), 'YYYY') as th,
					to_char(date_trunc('month',coalesce(e.date_inactive,e.create_date)), 'MM') as bln,
					CASE WHEN r.active = TRUE  THEN 1 END as masuk,
					CASE WHEN r.active = FALSE THEN 1 END as keluar,
					CASE WHEN r.active = TRUE  THEN 'masuk' ELSE
					CASE WHEN r.active = FALSE THEN 'keluar' END END as status,
					(select count(*) from hr_employee WHERE active = TRUE) as total,
					1 as nbr
				FROM
					hr_employee e
				JOIN 
					resource_resource r on r.id = e.resource_id
			)""")

hr_turnover_report()

