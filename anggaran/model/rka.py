from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
RKA_STATES =[('draft','Draft'),('open','Disahkan'),
                 ('done','Selesai')]

class rka(osv.osv):
	_name 		= "anggaran.rka"
	_rec_name   = "tahun"
	_columns 	= {
		'unit_id'	        : fields.many2one('anggaran.unit', 'Unit Kerja'),
		'tahun'		        : fields.many2one('account.fiscalyear', 'Tahun'),
		'alokasi'			: fields.float('Alokasi'),
		'rka_kegiatan_ids'  : fields.one2many('anggaran.rka_kegiatan','rka_id','Rincian Kegiatan', ondelete="cascade"),
		'state'             : fields.selection(RKA_STATES,'Status',readonly=True,required=True),
		'note'         		: fields.text('Note'),		
	}
	_defaults = {
		'state'       : RKA_STATES[0][0],
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':RKA_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':RKA_STATES[1][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':RKA_STATES[2][0]},context=context)


class rka_kegiatan(osv.osv):
	
	def _total_anggaran(self, cursor, user, ids, name, arg, context=None):
		res = {}

		for rka_keg in self.browse(cursor, user, ids, context=context):
			res[rka_keg.id] = sum([item.total for item in rka_keg.rka_coa_ids]) or 0.0

		return res

	_name 		= "anggaran.rka_kegiatan"
	_rec_name   = "kegiatan_id"
	_columns 	= {
		'rka_id'	        : fields.many2one('anggaran.rka', 'RKA'),
		'kegiatan_id'       : fields.many2one('anggaran.kegiatan', 'Kegiatan'),

		'program_id'      : fields.related('kegiatan_id', 
			'program_id' , type="many2one", 
			relation="anggaran.program", 
			string="Program", store=True, readonly=True ),

		'kebijakan_id'      : fields.related('kegiatan_id', 
			'program_id', 'kebijakan_id' , type="many2one", 
			relation="anggaran.kebijakan", 
			string="Kebijakan", store=True, readonly=True ),

		'indikator'         : fields.text('Indikator'),
		'target_capaian'    : fields.float('Target Capaian'),
		'target_capaian_uom': fields.many2one('product.uom', 'Satuan Target'),
		'anggaran'          : fields.function(_total_anggaran, string='Anggran',type='float', help="total Anggran kegiatan"),
		'rka_coa_ids'       : fields.one2many('anggaran.rka_coa','rka_kegiatan_id','Rincian ', ondelete="cascade")
	}

	def onchange_rka_coa(self,cr, uid, ids, rka_coa_ids, context=None):
		context = context or {}
		if not rka_coa_ids:
		    rka_coa_ids = []
		
		res = {
			'anggaran': 0.0,
		}
		anggaran_total = 0.0
		rka_coa_ids =rka_coa_ids
		rka_coa_ids = self.resolve_2many_commands(cr, uid, 'rka_coa_ids', rka_coa_ids, ['total'], context)

		for rka_coa in rka_coa_ids:
			jumlah = rka_coa.get('total',0.0)
			anggaran_total += jumlah

		total = anggaran_total		
		res.update({'anggaran': total})
		
		
		return {
			'value': res
		}


	

class rka_coa(osv.osv):
	_rec_name   = "coa_id"
	_name 		= "anggaran.rka_coa"
	_columns 	= {
		'rka_kegiatan_id' 	: fields.many2one('anggaran.rka_kegiatan', 'RKA Kegiatan'),
		'nama' 				: fields.text('Nama Rincian'),
		'coa_id'        	: fields.many2one('account.account', 'Nama Account'),
		'total'         	: fields.float('Jumlah Total'),
		'sumber_dana_id'	: fields.many2one('anggaran.sumber_dana', 'Sumber Dana'),
		'bulan'				: fields.many2one('account.period', 'Bulan'),
		'rka_detail_ids'    : fields.one2many('anggaran.rka_detail','rka_coa_id','Detail', ondelete="cascade")
	}

	def onchange_total(self,cr, uid, ids, total, context=None,):
		context = context or {}
		res = {}
		## ---> Set BreakPoint
		total = total or 0.00
		
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')
		view_obj = self.pool.get('ir.ui.view')
		
		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_kas_keluar_list')

		if(ids):
			ang = self.browse(cr,uid,ids[0],).rka_kegiatan_id
			ang.write({'anggaran':total})

		# import pdb;
		# pdb.set_trace()
		res = {
			
			'anggaran': 0.0,
			
		}
		#return super(class_name, self).onchange_total(cr, uid, vals, context=context)
		return {
			'value': res
		}


class rka_detail(osv.osv):
	_rec_name   = "keterangan"
	_name 		= "anggaran.rka_detail"
	_columns 	= {
		'rka_coa_id' 	: fields.many2one('anggaran.rka_coa', 'RKA Kegiatan'),
		'keterangan'	: fields.text('Keterangan'),
		'tarif'         : fields.float('Tarif'),
		'jumlah'        : fields.float('Jumlah'),
		'volume_total' 	: fields.float('Volume Total'),		
		'rka_volume_ids'    : fields.one2many('anggaran.rka_volume','rka_detail_id','Volumes', ondelete="cascade")
	}

class rka_volume(osv.osv):
	_name 		= "anggaran.rka_volume"
	_columns 	= {
		'rka_detail_id' : fields.many2one('anggaran.rka_detail', 'RKA Detail'),
		'volume' 		: fields.float('Volume'),
		'volume_uom'	: fields.many2one('product.uom', 'Satuan Volume'),
	}


	    	

	
