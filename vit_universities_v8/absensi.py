from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class absensi(osv.osv):
	_name = 'absensi'

	def create(self, cr, uid, vals, context=None):
		ajaran = vals['tahun_ajaran_id']
		fakultas = vals['fakultas_id']
		prodi = vals['prodi_id']
		semester = vals['semester_id']		
		jad_obj = self.pool.get('absensi')
		jad_id = jad_obj.search(cr,uid,[('tahun_ajaran_id','=',ajaran),
			('fakultas_id','=',fakultas),
			('prodi_id','=',prodi),
			('semester_id','=',semester),])

		if jad_id != [] :
			raise osv.except_osv(_('Error!'), _('Absensi tersebut sudah ada!'))

		return super(absensi, self).create(cr, uid, vals, context=context)   

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		if context is None:
			context = {}
		ids = []
		if name:
			ids = self.search(cr, user, [('name','=',name)] + args, limit=limit, context=context)
		if not ids:
			ids = self.search(cr, user, [('name',operator,name)] + args, limit=limit, context=context)
		return self.name_get(cr, user, ids, context)

	_columns = {
		'name'  : fields.char('Kode',size=30,required=True,readonly=True, states={'open': [('readonly', False)]}),
		'mata_kuliah_id' :fields.many2one('master.matakuliah',string='Matakuliah',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'state':fields.selection([('open','Opened'),('close','Closed')],'State',readonly=True, states={'open': [('readonly', False)]}),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'semester_id':fields.many2one('master.semester',string='Semester',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True,readonly=True, states={'open': [('readonly', False)]}),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',required=True,readonly=True, states={'open': [('readonly', False)]}), 
		'employee_id' :fields.many2one('hr.employee','Dosen', domain="[('is_dosen','=',True)]",required=True,readonly=True, states={'open': [('readonly', False)]}),
		'sesi':fields.integer('Toral Sesi',required=True,readonly=True, states={'open': [('readonly', False)]}),
		
		'kurikulum_id':fields.many2one('master.kurikulum',"Kurikulum",readonly=True, states={'open': [('readonly', False)]}),
		'absensi_ids' : fields.one2many('absensi.detail','absensi_id','Mahasiswa',readonly=True, states={'open': [('readonly', False)]}),

			}
			
	_defaults= {
		'state':'open',

		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'absensi'), 
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Absensi tidak boleh sama')]

	def open_absensi(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'open'},context=context)
			for det in ct.absensi_ids:
				self.pool.get('absensi.detail').write(cr,uid,det.id,{'state':'open'},context=context)
		return True	

	def close_absensi(self,cr,uid,ids,context=None):
		for ct in self.browse(cr,uid,ids):
			self.write(cr,uid,ct.id,{'state':'close'},context=context)
			for det in ct.absensi_ids:
				self.pool.get('absensi.detail').write(cr,uid,det.id,{'state':'close'},context=context)			
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in un active"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state == 'close':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus open'))
		return super(absensi, self).unlink(cr, uid, ids, context=context)

absensi()


class absensi_detail(osv.osv):
	_name = "absensi.detail"

	_columns = {
		'absensi_id' 	: fields.many2one('absensi','Jadwal'),
		'partner_id' 	: fields.many2one('res.partner','Mahasiswa',domain="[('status_mahasiswa','=','Mahasiswa')]",required=True),
		'absensi_1'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'1'),
		'absensi_2'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'2'),
		'absensi_3'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'3'),
		'absensi_4'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'4'),
		'absensi_5'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'5'),
		'absensi_6'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'6'),
		'absensi_7'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'7'),
		'absensi_8'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'8'),
		'absensi_9'		:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'9'),
		'absensi_10'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'10'),
		'absensi_11'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'11'),
		'absensi_12'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'12'),
		'absensi_13'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'13'),
		'absensi_14'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'14'),
		'absensi_15'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'15'),
		'absensi_16'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'16'),
		'absensi_17'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'17'),
		'absensi_18'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'18'),
		'absensi_19'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'19'),
		'absensi_20'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'20'),
		'absensi_21'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'21'),
		'absensi_22'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'22'),
		'absensi_23'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'23'),
		'absensi_24'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'24'),
		'absensi_25'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'25'),
		'absensi_26'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'26'),
		'absensi_27'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'27'),
		'absensi_28'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'28'),
		'absensi_29'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'29'),
		'absensi_30'	:fields.selection([('H','Hadir'),('S','Sakit'),('A','Alpha')],'30'),		
		'note'			:fields.char('Ket.'),
		'state':fields.selection([('open','Open'),('close','Close')],'State'),
	}
