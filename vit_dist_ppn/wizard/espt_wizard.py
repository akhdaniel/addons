from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class espt_wizard(osv.TransientModel): 
	_name = 'vit_dist_ppn.espt_wizard' 

	_columns = {
		'date_start' : fields.date('Invoice Date Start'),
		'date_end'   : fields.date('Invoice Date End'),
        'invoice_ids' : fields.one2many('vit_dist_ppn.espt_invoice_wizard',
                        'wizard_id', 'Attendees'),		

	}

	_defaults = {
		'date_start'  : lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month, 1)).strftime('%Y-%m-%d'),	
		'date_end'    : lambda *a : (datetime.date(datetime.date.today().year, datetime.date.today().month + 1, 1) - datetime.timedelta(days = 1)).strftime('%Y-%m-%d'),	
	}

	def find_invoices(self, cr, uid, date_start, date_end):
		res = {}
		context={}

		############################################################################
		# cari invoice sesuai kriteria tanggal wizard
		# yang udah ada nomor seri faktur pajak nya
		############################################################################
		invoice_obj = self.pool.get('account.invoice')
		invoice_ids = invoice_obj.search(cr, uid, 
			[
				('date_invoice',    '>=', date_start),
				('date_invoice' ,   '<=', date_end ), 
				('state',           '=' , 'open'),
				('tax_number',      '!=' , False )
			], 
			context)

		############################################################################
		# generate invoice_ids o2m records
		############################################################################
		invoice_data = []
		for inv in invoice_obj.browse(cr, uid, invoice_ids, context):
			invoice_data.append((0,0,{
					'invoice_id' : inv.id, 
					'amount'     : inv.amount_total, 
					'date'       : inv.date_invoice,
					'customer'   : inv.partner_id.name,
					'npwp'       : inv.partner_id.npwp,
					'tax_number' : inv.tax_number
					}) 
				)

		############################################################################
		# return value onchange
		############################################################################
		res = {'value' : {'invoice_ids': invoice_data} }
		return res

	def onchange_date_start(self, cr, uid, ids, date_start, date_end):
		results = self.find_invoices(cr, uid, date_start, date_end)
		return results		

	def onchange_date_end(self, cr, uid, ids, date_start, date_end):
		results = self.find_invoices(cr, uid, date_start, date_end)
		return results

	def export_espt(self, cr, uid, ids, context=None):
		invoice_obj = self.pool.get('account.invoice')
		wizard = self.browse(cr, uid, ids[0], context=context) 
		for wz_inv in wizard.invoice_ids:
			data = {'espt_export' : True, 
				'espt_export_date': datetime.date.today().strftime('%Y-%m-%d') }
			invoice_obj.write(cr, uid, [wz_inv.invoice_id.id], data, context=context)

		return {}

class espt_invoice_wizard(osv.TransientModel):
	_name = 'vit_dist_ppn.espt_invoice_wizard' 
	_columns = {
        'invoice_id' : fields.many2one('account.invoice', 'Customer Invoice', required=True),
        'amount'     : fields.float("Amount Total"),
        'date'       : fields.date("Date"),
        'tax_number' : fields.char('Tax Number', length=120),
        'customer'   : fields.char('Customer'),
        'npwp'		 : fields.char('NPWP'),
        'wizard_id'  : fields.many2one('vit_dist_ppn.espt_wizard'),
    }