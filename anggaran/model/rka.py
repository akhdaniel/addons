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
		'rka_kegiatan_ids'  : fields.one2many('anggaran.rka_kegiatan','rka_id','Rincian Kegiatan', ondelete="cascade"),
		'state'             : fields.selection(RKA_STATES,'Status',readonly=True,required=True),
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
		'anggaran'          : fields.float('Anggaran'),
		'rka_coa_ids'       : fields.one2many('anggaran.rka_coa','rka_kegiatan_id','Rincian COA', ondelete="cascade")
	}

class rka_coa(osv.osv):
	_rec_name   = "coa_id"
	_name 		= "anggaran.rka_coa"
	_columns 	= {
		'rka_kegiatan_id' 	: fields.many2one('anggaran.rka_kegiatan', 'RKA Kegiatan'),
		'coa_id'        	: fields.many2one('account.account', 'Nama Account'),
		'total'         	: fields.float('Jumlah Total'),
		'sumber_dana_id'	: fields.many2one('anggaran.sumber_dana', 'Sumber Dana'),
		'bulan'				: fields.many2one('account.period', 'Bulan'),
		'rka_detail_ids'    : fields.one2many('anggaran.rka_detail','rka_coa_id','Detail', ondelete="cascade")
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
