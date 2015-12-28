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
					date_part('MONTH', a.name) as bulan,
					date_part('YEAR', a.name) as tahun,
					case when date_part('day',a.name) = 1 then 1 else case when 1 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t1,
					case when date_part('day',a.name) = 2 then 1 else case when 2 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t2,
					case when date_part('day',a.name) = 3 then 1 else case when 3 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t3,
					case when date_part('day',a.name) = 4 then 1 else case when 4 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t4,
					case when date_part('day',a.name) = 5 then 1 else case when 5 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t5,
					case when date_part('day',a.name) = 6 then 1 else case when 6 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t6,
					case when date_part('day',a.name) = 7 then 1 else case when 7 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t7,
					case when date_part('day',a.name) = 8 then 1 else case when 8 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t8,
					case when date_part('day',a.name) = 9 then 1 else case when 9 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t9,
					case when date_part('day',a.name) = 10 then 1 else case when 10 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t10,
					case when date_part('day',a.name) = 11 then 1 else case when 11 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t11,
					case when date_part('day',a.name) = 12 then 1 else case when 12 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t12,
					case when date_part('day',a.name) = 13 then 1 else case when 13 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t13,
					case when date_part('day',a.name) = 14 then 1 else case when 14 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t14,
					case when date_part('day',a.name) = 15 then 1 else case when 15 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t15,
					case when date_part('day',a.name) = 16 then 1 else case when 16 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t16,
					case when date_part('day',a.name) = 17 then 1 else case when 17 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t17,
					case when date_part('day',a.name) = 18 then 1 else case when 18 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t18,
					case when date_part('day',a.name) = 19 then 1 else case when 19 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t19,
					case when date_part('day',a.name) = 20 then 1 else case when 20 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t20,
					case when date_part('day',a.name) = 21 then 1 else case when 21 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t21,
					case when date_part('day',a.name) = 22 then 1 else case when 22 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t22,
					case when date_part('day',a.name) = 23 then 1 else case when 23 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t23,
					case when date_part('day',a.name) = 24 then 1 else case when 24 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t24,
					case when date_part('day',a.name) = 25 then 1 else case when 25 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t25,
					case when date_part('day',a.name) = 26 then 1 else case when 26 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t26,
					case when date_part('day',a.name) = 27 then 1 else case when 27 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t27,
					case when date_part('day',a.name) = 28 then 1 else case when 28 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t28,
					case when date_part('day',a.name) = 29 then 1 else case when 29 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t29,
					case when date_part('day',a.name) = 30 then 1 else case when 30 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t30,
					case when date_part('day',a.name) = 31 then 1 else case when 31 between date_part('day',date_from) and date_part('day',date_to) then 2 end end as t31
				FROM
					hr_attendance a
				LEFT JOIN
					(SELECT
						employee_id,
						date_to,
						date_from
					FROM
						hr_holidays
					WHERE type='remove' AND state = 'validate') h
				ON a.employee_id = h.employee_id  AND a.name ::DATE BETWEEN h.date_from ::DATE AND h.date_to ::DATE
				WHERE (action='sign_in' OR action is NULL)
		)""")


#date_part('MONTH', date_from) = date_part('MONTH',CURRENT_DATE)