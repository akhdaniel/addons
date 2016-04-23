from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

####################################################################
# partner data
# from ajri-customer csv file
####################################################################
class import_ajri(osv.osv): 
	_name 		= "reliance.import_ajri"
	_columns 	= {
		"nomor_polis"			:	fields.char("Nomor Polis"),
		"nama_pemegang"			:	fields.char("Nama Pemegang"),
		"nomor_partisipan"		:	fields.char("Nomor Partisipan"),
		"nama_partisipan"		:	fields.char("Nama Partisipan"),
		"produk"				:	fields.char("Produk"),
		"tgl_lahir"				:	fields.char("Tgl Lahir"),
		"tgl_mulai"				:	fields.char("Tgl Mulai"),
		"tgl_selesai"			:	fields.char("Tgl Selesai"),
		"status"				:	fields.char("Status"),
		"up"					:	fields.char("Up"),
		"total_premi"			:	fields.char("Total Premi"),
		"status_klaim"			:	fields.char("Status Klaim"),
		"status_bayar"			:	fields.char("Status Bayar"),
		"tgl_bayar"				:	fields.char("Tgl Bayar"),
		"klaim_disetujui"		:	fields.char("Klaim Disetujui"),
		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		ajri_import_partner_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ajri_import_partner_limit')
		_logger.warning('running cron import_ajri')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=int(ajri_import_partner_limit), context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')

		pemegang_old = ''

		for import_ajri in self.browse(cr, uid, ids, context=context):


			if pemegang_old != import_ajri.nama_pemegang:

				pemegang_data = {
					'name'				: import_ajri.nama_pemegang,
					'ajri_nomor_polis'	: import_ajri.nomor_polis,
					'is_company'		: True,
					'comment' 			: 'AJRI'
				}
				
				########################## check exiting pemegang partner 
				pid = partner.search(cr, uid, [
					('ajri_nomor_polis','=',import_ajri.nomor_polis),
					('is_company','=',True)
					],context=context)
				if not pid:
					pid = partner.create(cr, uid, pemegang_data, context=context)	
					i = i + 1
				else:
					pid = pid[0]
					_logger.warning('Partner Pemegang exist with nomor_polis %s' % import_ajri.nomor_polis)
					ex = ex + 1

				pemegang_old = import_ajri.nama_pemegang



			########################## check exiting participant partner 
			if import_ajri.tgl_lahir:
				date = datetime.strptime(import_ajri.tgl_lahir, "%d-%b-%Y")
			else:
				date = False 
			participant_data = {
				'name'					: import_ajri.nama_partisipan,
				'ajri_nomor_partisipan'	: import_ajri.nomor_partisipan,
				'ajri_nomor_polis'		: import_ajri.nomor_polis,
				'is_company'			: False,
				'ajri_parent_id'		: pid,
				'perorangan_tanggal_lahir'	: date,
				'comment' 				: 'AJRI'
			}

			pid2 = partner.search(cr, uid, [('ajri_nomor_partisipan','=',import_ajri.nomor_partisipan)],context=context)
			if not pid2:
				pid2 = partner.create(cr, uid, participant_data, context=context)	
				i = i + 1
			else:
				pid2=pid2[0]
				_logger.warning('Partner Partisipan exist with nomor_partisipan %s' % import_ajri.nomor_partisipan)
				ex = ex + 1

			########################## check exiting product,category, and company
			categ = self.pool.get('product.category')
			categ_id = categ.search(cr, uid, [('name','=','Asuransi Jiwa')], context=context)
			if not categ_id:
				raise osv.except_osv(_('Error'),_("Please Create Product Category: Asuransi Jiwa") ) 

			company = self.pool.get('res.company')
			company_id = company.search(cr, uid, [('name','=','AJRI')], context=context)
			if not company_id:
				raise osv.except_osv(_('Error'),_("Please Create Company: AJRI") ) 

			product = self.pool.get('product.product')
			prod_id = product.search(cr, uid, [('name','=',import_ajri.produk)], context=context)
			if not prod_id:
				product_data = {
					'name'		: import_ajri.produk,
					'categ_id' 	: categ_id[0],
					'owner_id' 	: company_id[0],
				}
				prod_id = product.create(cr, uid, product_data, context=context)
			else:
				prod_id = prod_id[0]


			########################## import to partner_ajri_product
			partner_ajri_product = self.pool.get('reliance.partner_ajri_product')


			pap_data = {
				'partner_id'		: pid2,
				'product_id'		: prod_id,
				'start_date'		: datetime.strptime(import_ajri.tgl_mulai, "%d-%b-%Y") if import_ajri.tgl_mulai else False,
				'end_date'			: datetime.strptime(import_ajri.tgl_selesai, "%d-%b-%Y") if import_ajri.tgl_selesai else False,
				'status'			: import_ajri.status,
				'up'				: import_ajri.up.strip().replace(',','').replace('-','0'),
				"total_premi"		: import_ajri.total_premi.strip().replace(',','').replace('-','0'),
				"status_klaim"		: import_ajri.status_klaim,
				"status_bayar"		: import_ajri.status_bayar,
				"tgl_bayar"			: datetime.strptime(import_ajri.tgl_bayar, "%d-%b-%Y") if import_ajri.tgl_bayar else False,
				"klaim_disetujui" 	: import_ajri.klaim_disetujui,

			}
			partner_ajri_product.create(cr, uid, pap_data, context=context)


			#commit per record
			cr.execute("update reliance_import_ajri set is_imported='t' where id=%s" % import_ajri.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


