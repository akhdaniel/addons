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

		for import_ajri in self.browse(cr, uid, ids, context=context):
			data = {
				'nomor_participant'	: 
				'nomor_polis'		: 
			}
			data.update({'comment':'AJRI'})
			
			# check exiting partner 
			pid = partner.search(cr, uid, [('nomor_participant','=',import_ajri.nomor_participant)],context=context)
			if not pid:
				pid = partner.create(cr, uid, data, context=context)	
				i = i + 1
			else:
				_logger.warning('Partner exist with nomor_participant %s' % import_ajri.nomor_participant)
				ex = ex + 1

			cr.execute("update reliance_import_ajri set is_imported='t' where id=%s" % import_ajri.id)

			#commit per record
			cr.commit()
		raise osv.except_osv( 'OK!' , 'Done creating %s partner and skipped %s existing' % (i, ex) )


