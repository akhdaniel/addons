from openerp.osv import osv,fields
from openerp import tools
# from openerp.tools.translate import _

class hr_manpower_report(osv.Model):
	_name = 'hr.manpower.report'
	_auto = False
	_description = 'PPI Manpower Reports'

	_columns = {
		'work_location2': fields.selection([('karawang','Karawang'),('tanggerang','Tangerang'),('proyek','Proyek')],'Alamat Kantor', readonly=True), 
		'usia' : fields.selection([('15','15 - 20 Tahun'),('20','20 - 30 Tahun'),('30','30 - 40 Tahun'),('40','40 - 50 Tahun'),('50','50 - 60 Tahun'),('60','Lebih dari 60 Tahun')],"Usia",readonly=True),      
		'kelamin': fields.selection([('male','Male'),('female','Female')],'Jenis Kelamin', readonly=True),  
		'department_id' : fields.many2one('hr.department', string='Department', readonly=True),
		'nbr' : fields.integer('# of Employee', readonly=True),
	}

	def init(self, cr):

		"""
		ide_report 
		@param cr: the current row, from the database cursor
		"""
		tools.drop_view_if_exists(cr, 'hr_manpower_report')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_manpower_report AS (
				SELECT
					id,
					e.work_location2 as work_location2,
					e.kelamin as kelamin,
					e.department_id as department_id,
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) BETWEEN 15 AND 20 THEN '15' ELSE
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) BETWEEN 20 AND 30 THEN '20' ELSE 
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) BETWEEN 30 AND 40 THEN '30' ELSE
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) BETWEEN 40 AND 50 THEN '40' ELSE
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) BETWEEN 50 AND 60 THEN '50' ELSE
					CASE WHEN floor(extract('day' from (NOW() - birthday))/365) > 60 THEN '60' ELSE '0' END END END END END END as usia,
					1 as nbr
				FROM
					hr_employee e
			)""")

hr_manpower_report()