from openerp.osv import osv,fields
from openerp import tools

from openerp.osv import osv,fields
from openerp import tools
# from openerp.tools.translate import _

class hr_payslip_transfer_bank_list_report(osv.Model):
	_name = 'hr.payslip.transfer.bank.list.report'
	_auto = False
	_description = 'PPI Transfer Bank List'

	_columns = {
		'nik' : fields.char('NIK'),
		'employee' : fields.char('Employee Name'),
		'bank_name' : fields.char('Bank'),
		'name' : fields.char('Account Name'),		
		'acc_number' : fields.char('Account Number'), 
		'city' : fields.char('City'), 
		'net' : fields.float('Net'), 
		'date_from' : fields.date('Date from'),
		'date_to' : fields.date('Date to'),
		'bulan':fields.integer('Bulan', readonly=True),
		'tahun':fields.integer('Tahun', readonly=True),
	}

	def init(self, cr):

		"""
		ide_report 
		@param cr: the current row, from the database cursor
		"""
		tools.drop_view_if_exists(cr, 'hr_payslip_transfer_bank_list_report')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_payslip_transfer_bank_list_report AS (
				SELECT
					p.id,
					nik,
					name_related as employee, 
					bank_name,
					rp.name, 
					acc_number, 
					b.city, 
					net, 
					date_from,
					date_to,
					date_part('month',date_from) as bulan,
					date_part('year',date_from) as tahun
				FROM
					hr_payslip p
				INNER JOIN
					hr_employee e on e.id=p.employee_id 
				INNER JOIN 
					resource_resource r on r.id = e.resource_id
				LEFT JOIN
					res_partner_bank b on e.bank_account_id = b.id
				LEFT JOIN
					res_partner rp on b.partner_id = rp.id
				WHERE p.state = 'done'
					AND r.active = TRUE
			)""")

hr_payslip_transfer_bank_list_report()


class hr_payslip_monthly_list_report(osv.Model):
	_name = 'hr.payslip.monthly.list.report'
	_auto = False
	_description = 'PPI Monthly Payslip List'

	_columns = {
		'name_related' : fields.char('Employee Name'),
		'name' : fields.char('Payslip Line'),
		'amount' : fields.float('Amount'),
		'nik' : fields.char('NIK'),		
		'pajak' : fields.char('Status Pajak'),
		'bulan':fields.integer('Bulan', readonly=True),
		'tahun':fields.integer('Tahun', readonly=True),
		'ref_num':fields.char('Reference'),
	}

	def init(self, cr):

		"""
		ide_report 
		@param cr: the current row, from the database cursor
		"""
		tools.drop_view_if_exists(cr, 'hr_payslip_monthly_list_report')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_payslip_monthly_list_report AS (
				SELECT
					l.id,
					l.name,
					l.amount,
					p.number as ref_num,
					(select name_related from hr_employee e where e.id=p.employee_id) as name_related,
					(select nik from hr_employee e where e.id=p.employee_id) as nik,
					(select kode from hr_ptkp sp JOIN hr_employee e1 on e1.ptkp_id=sp.id where e1.id=p.employee_id) as pajak,
					date_part('month',date_from) as bulan,
					date_part('year',date_from) as tahun
				FROM hr_payslip_line l
				JOIN hr_salary_rule_category c ON l.category_id=c.id
				JOIN hr_payslip p ON p.id=l.slip_id
				WHERE amount != 0 AND c.code in ('BASIC','ALW','DED') AND state = 'done'
			)""")

hr_payslip_monthly_list_report()