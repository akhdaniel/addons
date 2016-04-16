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
		"up"					:	fields.char("Up "),
		"total_premi"			:	fields.char("Total Premi "),
		"status_klaim"			:	fields.char("Status Klaim"),
		"status_bayar"			:	fields.char("Status Bayar"),
		"tgl_bayar"				:	fields.char("Tgl Bayar"),
		"klaim_disetujui"		:	fields.char("Klaim Disetujui "),
		'is_imported' 			: 	fields.boolean("Imported to Partner?", select=1),
		"notes"					:	fields.char("Notes"),
	}

	def action_import_partner(self, cr, uid, context=None):
		active_ids = context and context.get('active_ids', False)
		if not context:
			context = {}

		self.actual_import(cr, uid, active_ids, context=context)


	def cron_import_partner(self, cr, uid, context=None):
		_logger.warning('running cron import_ajri')
		active_ids = self.search(cr, uid, [('is_imported','=', False)], limit=100, context=context)
		if active_ids:
			self.actual_import(cr, uid, active_ids, context=context)
		else:
			print "no partner to import"
		return True

	################################################################
	# the import process
	# baca record ids, insert ke partner dengan field sesuai 
	# PARTNER_MAPPING
	################################################################
	def actual_import(self, cr, uid, ids, context=None):
		i = 0
		ex = 0

		partner = self.pool.get('res.partner')

		pemegang_old = ''

		for import_ajri in self.browse(cr, uid, ids, context=context):

			# import pdb; pdb.set_trace()

			if pemegang_old != import_ajri.nama_pemegang:

				pemegang_data = {
					'name'				: import_ajri.nama_pemegang,
					'nomor_polis'		: import_ajri.nomor_polis,
					'is_company'		: True,
					'comment' 			: 'AJRI'
				}
				
				########################## check exiting pemegang partner 
				pid = partner.search(cr, uid, [('nomor_polis','=',import_ajri.nomor_polis)],context=context)
				if not pid:
					pid = partner.create(cr, uid, pemegang_data, context=context)	
					i = i + 1
				else:
					pid = pid[0]
					_logger.warning('Partner Pemegang exist with nomor_polis %s' % import_ajri.nomor_polis)
					ex = ex + 1

				pemegang_old = import_ajri.nama_pemegang


			########################## check exiting participant partner 
			participant_data = {
				'name'				: import_ajri.nama_partisipan,
				'nomor_partisipan'	: import_ajri.nomor_partisipan,
				'is_company'		: False,
				'parent_id'			: pid,
				'comment' 			: 'AJRI'
			}

			pid2 = partner.search(cr, uid, [('nomor_partisipan','=',import_ajri.nomor_partisipan)],context=context)
			if not pid2:
				pid2 = partner.create(cr, uid, participant_data, context=context)	
				i = i + 1
			else:
				_logger.warning('Partner Partisipan exist with nomor_partisipan %s' % import_ajri.nomor_partisipan)
				ex = ex + 1


			#commit per record
			cr.execute("update reliance_import_ajri set is_imported='t' where id=%s" % import_ajri.id)
			cr.commit()

		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


