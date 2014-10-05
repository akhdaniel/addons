from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class set_tax_numbering_wizard(osv.TransientModel): 
	_name = 'vit_dist_ppn.set_tax_numbering_wizard' 

	_columns = {
		'date_start' : fields.date('Invoice Date Start'),
		'date_end'   : fields.date('Invoice Date End'),
        'invoice_ids' : fields.one2many('vit_dist_ppn.invoice_wizard',
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
		# ambil nomor seri faktur pajak current
		############################################################################
		tax_numbering_obj = self.pool.get('vit_dist_ppn.tax_numbering')
		tids = tax_numbering_obj.search(cr, uid, [('year','=',datetime.date.today().year)] , context)
		if not tids:
			raise osv.except_osv(_('Error'), _('Please set Tax Numbering for the current year'))
		tax_numbering = tax_numbering_obj.browse(cr, uid, tids[0], context)
		tax_number    = int(tax_numbering.current_no)
		prefix        = tax_numbering.prefix

		############################################################################
		# cari invoice sesuai kriteria tanggal wizard,
		# hanya out_invoice / customer 
		# yang belum ada nomor seri fatktur pajaknya
		############################################################################
		invoice_obj = self.pool.get('account.invoice')
		invoice_ids = invoice_obj.search(cr, uid, 
			[
				('date_invoice',    '>=', date_start),
				('date_invoice' ,   '<=', date_end ), 
				('state',           '=' , 'open'),
				('tax_number',      '=' , False ),
				('type',            '=' , 'out_invoice')
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
					'tax_number' : "%s%08d" % (prefix, tax_number)
					}) 
				)
			tax_number = int(tax_number) + 1


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

	def set_tax_numbering(self, cr, uid, ids, context=None):
		invoice_obj = self.pool.get('account.invoice')
		wizard = self.browse(cr, uid, ids[0], context=context) 
		last_tax_number = ''
		for wz_inv in wizard.invoice_ids:
			invoice_obj.write(cr, uid, wz_inv.invoice_id.id, {'tax_number': wz_inv.tax_number}, context)
			last_tax_number =  wz_inv.tax_number # prefix.number

		############################################################################
		# update tax numbering to the current number 
		# ambil nomor terakhir, hilangkan prefix
		# set current_no = nomor terakhir + 1
		############################################################################
		tax_numbering_obj = self.pool.get('vit_dist_ppn.tax_numbering')
		tids = tax_numbering_obj.search(cr, uid, [('year','=',datetime.date.today().year)] , context=context)

		tax_number = tax_numbering_obj.browse(cr, uid, tids[0], context)
		prefix     = tax_number.prefix
		last_no    = int(last_tax_number.replace(prefix, ''))

		tax_numbering_obj.write(cr, uid, tids, {'current_no': "%08d" % (last_no+1)}, context)

		return {}

class invoice_wizard(osv.TransientModel):
	_name = 'vit_dist_ppn.invoice_wizard' 
	_columns = {
        'invoice_id' : fields.many2one('account.invoice', 'Customer Invoice', required=True),
        'amount'     : fields.float("Amount Total"),
        'date'       : fields.date("Date"),
        'tax_number' : fields.char('Tax Number', length=120),
        'customer'   : fields.char('Customer'),
        'npwp'		 : fields.char('NPWP'),
        'wizard_id'  : fields.many2one('vit_dist_ppn.set_tax_numbering_wizard'),
    }