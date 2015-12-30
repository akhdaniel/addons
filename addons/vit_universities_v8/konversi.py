from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class konversi(osv.Model):
	_name = 'akademik.konversi'

	_columns = {
		'name' :fields.char('Kode Konversi',size=36,required = True,readonly=True, states={'draft': [('readonly', False)]}),
		'partner_id' : fields.many2one('res.partner','Mahasiswa',required=True,readonly=True, domain="[('status_mahasiswa','=','Mahasiswa')]", states={'draft': [('readonly', False)]}),
		'semester_id':fields.many2one('master.semester','Sampai Semester',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		# 'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,readonly=True, states={'draft': [('readonly', False)]}),

		'asal_prodi_id':fields.many2one('master.prodi','Asal Program Studi',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'asal_jurusan_id':fields.many2one('master.jurusan','Asal Jurusan',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'asal_fakultas_id':fields.many2one('master.fakultas','Asal Fakultas',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'asal_univ_id':fields.many2one('res.partner','Asal Universitas',required=True,readonly=True, states={'draft': [('readonly', False)]}),

		'prodi_id':fields.many2one('master.prodi','Program Studi',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'jurusan_id':fields.many2one('master.jurusan','Jurusan',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'tahun_ajaran_id': fields.many2one('academic.year','Angkatan', required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'state':fields.selection([('draft','Draft'),('waiting','Waiting Approval'),('confirm','Confirmed'),('cancel','Canceled'),('refuse','Refused'),('done','Done')],'Status', states={'draft': [('readonly', False)]}),
  		'notes' : fields.text('Alasan',required=True,readonly=True, states={'draft': [('readonly', False)]}),
		'user_id':fields.many2one('res.users', 'User',readonly=True),
		'date': fields.date('Tanggal Registrasi',readonly=True,states={'draft': [('readonly', False)]}),
		'krs_done':fields.boolean('KRS Done',readonly=True,states={'draft': [('readonly', False)]}),

		'asal_matakuliah_ids' 	: fields.one2many('akademik.konversi.asal_mk','konversi_id','Asal Mata Kuliah', ondelete="cascade"),
		'matakuliah_ids' 		: fields.one2many('akademik.konversi.mk','konversi_id','Mata Kuliah', ondelete="cascade" ),
	}

	_defaults = {  
		'state':'draft',
		'user_id':lambda obj, cr, uid, context: uid,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'akademik.konversi'), 
	}
			
	_sql_constraints = [('name_uniq', 'unique(name)','Kode akademik.konversi tidak boleh sama')]

	def onchange_partner(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, jurusan_id, prodi_id, kelas_id, partner_id, context=None):
		results = {}
		if not partner_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [('id','=',partner_id)], context=context)

		#import pdb;pdb.set_trace()
		par_id = par_obj.browse(cr,uid,par_ids,context=context)[0]
		kelas_id = par_id.kelas_id.id
		tahun_ajaran_id = par_id.tahun_ajaran_id.id
		fakultas_id = par_id.fakultas_id.id
		jurusan_id = par_id.jurusan_id.id
		prodi_id = par_id.prodi_id.id

		results = {
			'value' : {
				'kelas_id': kelas_id,
				'tahun_ajaran_id' : tahun_ajaran_id,
				'fakultas_id' : fakultas_id,
				'jurusan_id' : jurusan_id,
				'prodi_id' : prodi_id,
			}
		}
		return results 

	def confirm(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'waiting'},context=context)
		return True	

	def approve(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			mhs_id = ct.partner_id.id
			self.pool.get('res.partner').write(cr,uid,mhs_id,{'status_mahasiswa':'cuti','active':False},context=context)
			self.write(cr,uid,ct.id,{'state':'confirm'},context=context)
		return True	

	def cancel(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'cancel'},context=context)
		return True	

	def set_draft(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'draft'},context=context)
		return True	

	def refuse(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'refuse'},context=context)
		return True	

	def done(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			mhs_id = ct.partner_id.id
			self.pool.get('res.partner').write(cr,uid,mhs_id,{'status_mahasiswa':'Mahasiswa','active':True},context=context)
			self.write(cr,uid,ct.id,{'state':'done'},context=context)
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(konversi, self).unlink(cr, uid, ids, context=context)
			
konversi()



class konversi_asal_mk(osv.osv):
	_name 		= "akademik.konversi.asal_mk"
	_columns 	= {
		'konversi_id' : fields.many2one('akademik.konversi', 'Konversi'),
		'matakuliah_id' : fields.many2one('akademik.konversi.master_asal_mk', 'Nama Matakuliah'),
		'nilai'			: fields.float('Nilai'),
		'nilai_a'		: fields.char('Nilai 2'),
	}

class konversi_mk(osv.osv):
	_name 		= "akademik.konversi.mk"
	_columns 	= {
		'konversi_id' : fields.many2one('akademik.konversi', 'Konversi'),
		'matakuliah_id' : fields.many2one('master.matakuliah', 'Nama Matakuliah'),
		'nilai'			: fields.float('Nilai'),
		'nilai_a'		: fields.char('Nilai 2'),
	}

