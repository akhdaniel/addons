from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SPP_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]


class spp(osv.osv):
	_name 		= 'anggaran.spp'

	def _spm_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for spp in self.browse(cursor, user, ids, context=context):
			res[spp.id] = False
			if spp.spm_ids:
				res[spp.id] = True
		return res


	_columns 	= {
		'name' 				: fields.char('Nomor', required=True, readonly=True),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'tahun_id'		   	: fields.many2one('account.fiscalyear', 'Tahun', readonly=True),
		'kepada'  			: fields.char('Kepada', required=True),
		'dasar_rkat' 		: fields.char('Dasar RKAT Nomor/Tanggal', required=True),
		'jumlah'  			: fields.float('Jumlah Pembayaran', required=True),
		'keperluan' 		: fields.char('Untuk Keperluan', required=True),
		'cara_bayar'        : fields.selection([('tup','TUP'),('gup','GUP'),('ls','Pembayaran LS')],
								'Cara Bayar',required=True),
		'unit_id'  			: fields.many2one('anggaran.unit', 'Atas Nama', required=True),
		'alamat'   			: fields.text('Alamat'),
		'nomor_rek' 		: fields.char('Nomor Rekening'),
		'nama_bank' 		: fields.char('Nama Bank'),

		'spp_line_ids' 		: fields.one2many('anggaran.spp_line','spp_id','Penjelasan', ondelete="cascade"),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'  	: fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'user_id'	    	: fields.many2one('res.users', 'Created', required=True,readonly=True),
		'state'             : fields.selection(SPP_STATES,'Status',readonly=True,required=True),

		'sptb_id'     		: fields.many2one('anggaran.sptb', 'SPTB'),
		'spm_ids'			: fields.one2many('anggaran.spm','spp_id','SPM'),
		'spm_exists'		: fields.function(_spm_exists, 
			string='SPM Sudah Tercatat',  
		    type='boolean', help="Apakah SPP ni sudah dicatatkan SPM-nya."),		
	}
	_defaults = {
		'state'       	: SPP_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':SPP_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':SPP_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':SPP_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':SPP_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.spp') or '/'
		new_id = super(spp, self).create(cr, uid, vals, context=context)
		return new_id

	def action_create_spm(self,cr,uid,ids,context=None):
		spp = self.browse(cr, uid, ids[0], context)
		#############################################################
		# cari rka utk unit_id
		#############################################################
		rka_obj = self.pool.get("anggaran.rka")
		search = [('unit_id.id','=', spp.unit_id.id)]
		rka_ids = rka_obj.search(cr,uid, search, context=context)
		for rka in rka_obj.browse(cr, uid, rka_ids, context=context):	
			kebijakan_ids = []
			for keg in rka.rka_kegiatan_ids:
				kebijakan_ids += keg.kebijakan_id

			spm_line_ids = [(0,0,{
					'kebijakan_id' : keg.kebijakan_id.id
				}) for bij 
				in set(kebijakan_ids) ]

		spm_obj = self.pool.get("anggaran.spm")
		data = {
			'name' 			: '/',
			'tanggal' 		: time.strftime("%Y-%m-%d") ,
			'cara_bayar'    : 'gup',
			'unit_id'	 	: spp.unit_id.id,
			'tahun_id'		: spp.tahun_id.id,
			'jumlah' 		: spp.jumlah,
			'sisa' 			: 0.0,
			'user_id'	    : uid, 
			'state'         : 'draft',
			'spp_id'		: spp.id,
			'spm_line_ids'	: spm_line_ids
		}
		spm_id = spm_obj.create(cr,uid,data,context)
		return spm_id

	def action_view_spm(self, cr, uid, ids, context=None):
		'''
		This function returns an action that display existing spm 
		of given kas ids. It can either be a in a list or in a form view, 
		if there is only one spm to show.
		'''
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_spm_list')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		#compute the number of spm to display
		spm_ids = []
		for kas in self.browse(cr, uid, ids, context=context):
			spm_ids += [spm.id for spm in kas.spm_ids]
		#choose the view_mode accordingly
		if len(spm_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, spm_ids))+"])]"
		else:
			res = mod_obj.get_object_reference(cr, uid, 'anggaran', 'view_spm_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = spm_ids and spm_ids[0] or False
		return result

class spp_line(osv.osv):
	_name 		= "anggaran.spp_line"
	_columns 	= {
		'spp_id' 		: fields.many2one('anggaran.spp', 'SPP'),
		'rka_kegiatan_id' : fields.many2one('anggaran.rka_kegiatan', 'Kegiatan Bersangkutan'),
		'pagu' : fields.related('rka_kegiatan_id', 
				'anggaran',
				type="float", relation="anggaran.rka_kegiatan", 
				string="PAGU", store=True),
		'spp_lalu' : fields.float("SPP sd yg Lalu"),
		'spp_ini'  : fields.float("SPP ini"),
		'jumlah_spp' : fields.float("Jumlah SPP"),
		'sisa_dana'  : fields.float("Sisa Dana"),
	}
