# -*- coding: utf-8 -*-
from openerp.osv import osv, fields
from openerp.report import report_sxw
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class purchase_order_line(osv.osv):
	_inherit  = 'purchase.order.line'

	def _amount_line(self, cr, uid, ids, prop, arg, context=None):
		res = {}
		cur_obj = self.pool.get('res.currency')
		tax_obj = self.pool.get('account.tax')
		for line in self.browse(cr, uid, ids, context=context):

			taxes = tax_obj.compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id,
										line.order_id.partner_id)
			cur = line.order_id.pricelist_id.currency_id
			res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])

			if line.discount > 0.0 and line.discount <= 100.0:
				res[line.id] = res[line.id] * (100 - line.discount)

		return res



	# add discount before taxes
	def _calc_line_base_price(self, cr, uid, line, context=None):
		"""Return the base price of the line to be used for tax calculation.

		This function can be extended by other modules to modify this base
		price (adding a discount, for example).
		"""
		if line.discount > 100.00:
			raise osv.except_osv(_('Error!'), _('Discount  lebih dari 100%!'))
		price =  line.price_unit
		discount = line.discount/100 or 0.0
		price -= price*discount
		return  price



	def _get_tax_notes(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res={}
		rp = str(self.browse(cr, uid, ids[0], context).order_id.currency_id.symbol) or ''
		for line in self.browse(cr, uid, ids, context):
			taxes=[]
			for tx in line.taxes_id:
				amt = tx.amount or 0.0
				if tx.type == 'percent':
					taxes.append("%s%%" % str(int(amt*100)) )
				elif tx.type == 'fixed':
					taxes.append(" ".join([rp,str(amt)]))
				else : taxes.append(tx.name)
			taxes = ",".join(taxes)
			res[line.id] = taxes
		return res

	_columns = {
		'taxes_str': fields.function(_get_tax_notes, type='char',string='Taxes',store=False),
		'discount': fields.float(string='Discount(%)',digits=(3,1),length=3),
		'price_subtotal': fields.function(_amount_line, string='Subtotal', digits_compute=dp.get_precision('Account')),
	}

	def _cek_discount(self,cr,uid,ids,context=None):
		line = self.browse(cr,uid,ids,context=context)
		if line.discount<0.0 or line.discount > 100.00:
			return False

		return True

	_constraints = [( _cek_discount,_('Discount must be 0-100%!'), ['discount'])]


class purchase_order(osv.osv):
	_inherit  = 'purchase.order'

	def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
		res = {}
		cur_obj = self.pool.get('res.currency')
		for order in self.browse(cr, uid, ids, context=context):
			res[order.id] = {
				'amount_untaxed': 0.0,
				'amount_tax': 0.0,
				'amount_total': 0.0,
			}
			val = val1 = 0.0
			cur = order.pricelist_id.currency_id
			for line in order.order_line:
				val1 += line.price_subtotal
				for c in \
				self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty,
														 line.product_id, order.partner_id)['taxes']:
					val += c.get('amount', 0.0) * (100 - line.discount)/100
			res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
			res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
			res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
		return res

	def wkf_confirm_order(self, cr, uid, ids, context=None):
		self.write_bc(cr,uid,ids,context)
		super(purchase_order, self).wkf_confirm_order(cr, uid, ids, context=context)
		return True

	def write_bc(self,cr,uid,ids,context):
		# siapkan format penulisan L,R or C
		def dikiri(length,kata):
			txtFormat=''
			txtFormat = '{:<%d}' % length
			return txtFormat.format(kata)
		def dikanan(length,kata):
			txtFormat=''
			txtFormat = '{:>%d}' % length
			return txtFormat.format(kata)
		def ditengah(length,kata,separator):
			if not separator: separator=" "
			txtFormat=''
			txtFormat = '{:%s^%d}' % (separator,length)
			return txtFormat.format(kata)
		def diDiv(length,kata):
			kata = kata.split("\n")
			dived=[]
			for kt in kata:
				x0=0
				x=len(kt)
				L=[];st=[];fs=[]
				while x>0:
					st.append(x0*length)
					x0+=1
					fs.append(x0*length)
					x-=length
				for x,y in zip(st,fs):
					L.append(kt[x:y])
				dived += L
			return  dived
		def cekElem(arrDict):
			# input : arrDict = {'a':arrayA,'b':arrayB,'c':arrayC}
			# output : length array will same acording to the bigest length, append by " "
			kosong = arrDict['kosong']
			arrDict.pop('kosong')
			L=0
			if len(arrDict.keys()) > 1 :
				L= max(len(k) for k in arrDict.values())
				for div in  arrDict.keys():
					while len(arrDict[div])<L:
						arrDict[div].append(dikiri(kosong[div]-1," "))
			return arrDict,L

		# PAPER LENGTH 95 chrs

		# grs separator 95chrs length
		separator="-----------------------------------------------------------------------------------------------"

		for data in self.browse(cr,uid,ids,):
			result=""
			comp = data.company_id.name.upper()
			alamatC = ' '.join([str(data.company_id.street or ''),
										str(data.company_id.street2 or ''),
										str(data.company_id.city or ''),
										str(data.company_id.state_id and data.company_id.state_id.name or ''),
										str(data.company_id.zip or ''),
										str(data.company_id.country_id and data.company_id.country_id.name or '')])
			phoneC = ' '.join([data.company_id.phone and str("phone %s" % data.company_id.phone) or '',  data.company_id.fax and str(", fax %s" % data.company_id.fax) or ''])
			if data.company_id.partner_id.npwp:
				phoneC = " ".join([phoneC,data.company_id.partner_id.npwp])

			# Company header
			mainHeader=[dikiri(95,comp),dikiri(95,alamatC),dikiri(95,phoneC),separator]

			partner = data.partner_id.name
			almatkpd = ' '.join([str(data.partner_id.street or ''),
										str(data.partner_id.street2 or ''),
										str(data.partner_id.city or '')])
			phkpd = ' '.join([data.partner_id.phone or '',  data.partner_id.fax and str(" fax %s" % data.partner_id.fax) or ''])

			# main title
			titles = []
			hdL=[12,22,18,40]
			tabs = 54
			titles.append(ditengah(tabs,"PURCHASE ORDER"," "))
			titles.append(" ".join([dikiri(hdL[0],"No.Order :"), dikiri(hdL[1],"Order Date :"), dikiri(hdL[2],"Prepared By :"), dikiri(hdL[3],partner[:hdL[3]])]))
			titles.append(" ".join([dikiri(hdL[0],data.name), dikiri(hdL[1],data.date_order), dikiri(hdL[2],data.validator.name), dikiri(hdL[3],almatkpd[:hdL[3]])]))
			if almatkpd[hdL[3]:] :
				titles.append(" ".join([dikanan(tabs," "),dikiri(hdL[3],almatkpd[hdL[3]:])]))
			titles.append(" ".join([dikanan(tabs," "),dikiri(tabs,phkpd[:hdL[3]])]))
			if phkpd[hdL[3]:] :
				titles.append(" ".join([dikanan(tabs," "),dikiri(tabs,phkpd[37:])]))

			# lines
			lines=[]
			# panjang karakter max tiap kolom, to joined by single space
			lgt = [22,7,8,14,18,21]
			lineH = ["Description","Tax","Disc (%)","Qty","Unit Price","Net Price"]
			# format header
			lines.append(separator)
			lines.append(' '.join([dikiri(lgt[0],lineH[0]),dikiri(lgt[1],lineH[1]),dikiri(lgt[2],lineH[2]),dikanan(lgt[3],lineH[3]),dikanan(lgt[4],lineH[4]),dikanan(lgt[5],lineH[5])]) )
			lines.append(separator)

			rp = str(data.currency_id.symbol)
			rml_parser = report_sxw.rml_parse(cr, uid, '', context=context)
			for line in data.order_line:
				taxes=[]
				for tx in line.taxes_id:
					amt = tx.amount or 0.0
					if tx.type == 'percent':
						taxes.append(" ".join([str(amt*100),"%"]))
					elif tx.type == 'fixed':
						taxes.append(" ".join([rp,str(amt)]))
					else : taxes.append(tx.name)
				taxes = ",".join(taxes)
				names = diDiv(lgt[0],line.name)
				# names = names.split("\n")
				# import pdb;pdb.set_trace()
				amt_price_unit = rml_parser.formatLang(line.price_unit, currency_obj=data.currency_id).replace(u'\xa0', u' ')
				amt_price_stot = rml_parser.formatLang(line.price_subtotal, currency_obj=data.currency_id).replace(u'\xa0', u' ')
				lines.append(' '.join([
						dikiri(lgt[0],names[0]),
						dikiri(lgt[1],taxes[:lgt[1]]),
						dikiri(lgt[2],str(line.taxes_str)),
						dikanan(lgt[3]," ".join([str(line.product_qty),line.product_uom.name])),
						dikanan(lgt[4],amt_price_unit),
						dikanan(lgt[5],amt_price_stot)
						]))
				if len(names)>1:
					names.remove(names[0])
					for nm in names:
						lines.append(dikiri(lgt[0],nm))
			# konstruk div for 3 cols
			footerkiri = []
			Lf={'1':tabs,'2':3,'3':19,'4':17}
			if data.notes2:
				note = '\n'.join(["Terms & Condition :",data.notes2])
				footerkiri += [dikiri(Lf['1'],x) for x in diDiv(tabs,note)]
			footerkanan1 = [dikiri(Lf['3'],x) for x in ["-------------------","Total Without Taxes", "Taxes","-------------------","Total"]]
			amt_amount_untax = rml_parser.formatLang(data.amount_untaxed, currency_obj=data.currency_id).replace(u'\xa0', u' ')
			amt_amount_tax = rml_parser.formatLang(data.amount_tax, currency_obj=data.currency_id).replace(u'\xa0', u' ')
			amt_amount_tot = rml_parser.formatLang(data.amount_total, currency_obj=data.currency_id).replace(u'\xa0', u' ')

			footerkanan2 = [dikanan(Lf['4'],x) for x in  ["-----------------",amt_amount_untax, amt_amount_tax,"-----------------", amt_amount_tot]]

			kosong=[]
			elem = {}
			elem.update({'1':footerkiri,'2':kosong,'3':footerkanan1,'4':footerkanan2,'kosong':Lf})
			elem,L = cekElem(elem)

			L= max(len(k) for k in elem.values())
			i=0
			footer = []
			while i<L:
				all=[]
				for y in zip(x for x in elem.values()):
					all.append(y[0][i])
				S = " ".join(all)
				footer.append(S)
				i+=1
			# print("\n".join(footer))
			ttd = [separator, ditengah(tabs/2,"    Supplier    "," ")+ditengah(tabs/2,"  Hormat Kami,  "," "), "\n\n"+ditengah(tabs/2,"( ________________ )"," ")+ditengah(tabs/2,"( ________________ )"," ")]
			result = '\n'.join(mainHeader+titles+lines+footer+ttd)
			self.write(cr,uid,data.id,{'barcode_data': result})
		return  True

	def _get_order(self, cr, uid, ids, context=None):
		result = {}
		for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
			result[line.order_id.id] = True
		return result.keys()

	_columns = {
		'barcode_data': fields.text('Barcode Data'),
		'amount_untaxed': fields.function(_amount_all, digits_compute=dp.get_precision('Account'),
										  string='Untaxed Amount',
										  store={
											  'purchase.order.line': (_get_order, None, 10),
										  }, multi="sums", help="The amount without tax", track_visibility='always'),
		'amount_tax': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Taxes',
									  store={
										  'purchase.order.line': (_get_order, None, 10),
									  }, multi="sums", help="The tax amount"),
		'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
										store={
											'purchase.order.line': (_get_order, None, 10),
										}, multi="sums", help="The total amount"),
	}

	_sql_constraints = [
		('po_no_uniq', 'unique(name,company_id)', 'The number of PO must be unique per company!'),
	]
