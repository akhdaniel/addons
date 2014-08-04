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
					nik || ' - ' || name_related as employee, 
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