from openerp.osv import osv,fields
from openerp import tools
# from time import time

class hr_absensi_report(osv.Model):
	_name = 'hr.absensi.report'
	_auto = False
	_description = 'PPI Absensi'

	_columns = {
		'employee_id': fields.many2one('hr.employee', "Employee", readonly=True),
		'bulan':fields.integer('Bulan', readonly=True),
		'tahun':fields.integer('Tahun', readonly=True),
		't1': fields.integer("1", size=1,  readonly=True),
		't2': fields.integer("2", size=1,  readonly=True),
		't3': fields.integer("3", size=1,  readonly=True),
		't4': fields.integer("4", size=1,  readonly=True),
		't5': fields.integer("5", size=1,  readonly=True),
		't6': fields.integer("6", size=1,  readonly=True),
		't7': fields.integer("7", size=1,  readonly=True),
		't8': fields.integer("8", size=1,  readonly=True),
		't9': fields.integer("9", size=1,  readonly=True),
		't10': fields.integer("10", size=1,  readonly=True),
		't11': fields.integer("11", size=1,  readonly=True),
		't12': fields.integer("12", size=1,  readonly=True),
		't13': fields.integer("13", size=1,  readonly=True),
		't14': fields.integer("14", size=1,  readonly=True),
		't15': fields.integer("15", size=1,  readonly=True),
		't16': fields.integer("16", size=1,  readonly=True),
		't17': fields.integer("17", size=1,  readonly=True),
		't18': fields.integer("18", size=1,  readonly=True),
		't19': fields.integer("19", size=1,  readonly=True),
		't20': fields.integer("20", size=1,  readonly=True),
		't21': fields.integer("21", size=1,  readonly=True),
		't22': fields.integer("22", size=1,  readonly=True),
		't23': fields.integer("23", size=1,  readonly=True),
		't24': fields.integer("24", size=1,  readonly=True),
		't25': fields.integer("25", size=1,  readonly=True),
		't26': fields.integer("26", size=1,  readonly=True),
		't27': fields.integer("27", size=1,  readonly=True),
		't28': fields.integer("28", size=1,  readonly=True),
		't29': fields.integer("29", size=1,  readonly=True),
		't30': fields.integer("30", size=1,  readonly=True),
		't31': fields.integer("31", size=1,  readonly=True),
	}

	def init(self, cr):
		tools.drop_view_if_exists(cr, 'hr_absensi_report')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_absensi_report AS (
				SELECT 
					a.id,
					a.employee_id,
					date_part('MONTH', name) as bulan,
					date_part('YEAR', name) as tahun,
					case when date_part('day',name) = 1 then 1 end as t1,
					case when date_part('day',name) = 2 then 1 end as t2,
					case when date_part('day',name) = 3 then 1 end as t3,
					case when date_part('day',name) = 4 then 1 end as t4,
					case when date_part('day',name) = 5 then 1 end as t5,
					case when date_part('day',name) = 6 then 1 end as t6,
					case when date_part('day',name) = 7 then 1 end as t7,
					case when date_part('day',name) = 8 then 1 end as t8,
					case when date_part('day',name) = 9 then 1 end as t9,
					case when date_part('day',name) = 10 then 1 end as t10,
					case when date_part('day',name) = 11 then 1 end as t11,
					case when date_part('day',name) = 12 then 1 end as t12,
					case when date_part('day',name) = 13 then 1 end as t13,
					case when date_part('day',name) = 14 then 1 end as t14,
					case when date_part('day',name) = 15 then 1 end as t15,
					case when date_part('day',name) = 16 then 1 end as t16,
					case when date_part('day',name) = 17 then 1 end as t17,
					case when date_part('day',name) = 18 then 1 end as t18,
					case when date_part('day',name) = 19 then 1 end as t19,
					case when date_part('day',name) = 20 then 1 end as t20,
					case when date_part('day',name) = 21 then 1 end as t21,
					case when date_part('day',name) = 22 then 1 end as t22,
					case when date_part('day',name) = 23 then 1 end as t23,
					case when date_part('day',name) = 24 then 1 end as t24,
					case when date_part('day',name) = 25 then 1 end as t25,
					case when date_part('day',name) = 26 then 1 end as t26,
					case when date_part('day',name) = 27 then 1 end as t27,
					case when date_part('day',name) = 28 then 1 end as t28,
					case when date_part('day',name) = 29 then 1 end as t29,
					case when date_part('day',name) = 30 then 1 end as t30,
					case when date_part('day',name) = 31 then 1 end as t31
				FROM
					hr_attendance a
				WHERE (action='sign_in' OR action is NULL)
		)""")


#date_part('MONTH', date_from) = date_part('MONTH',CURRENT_DATE)