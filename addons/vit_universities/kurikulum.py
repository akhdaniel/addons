from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class master_kurikulum (osv.Model):
	_name = 'master.kurikulum'
	_order = 'name'


	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		if vals['max_sks'] == 0:
			raise osv.except_osv(_('Error!'), _('Maximal total SKS tidak boleh nol !'))		
		if not vals['kurikulum_detail_ids']:
			raise osv.except_osv(_('Error!'), _('Matakuliah tidak boleh kosong !'))
		mk = vals['kurikulum_detail_ids'][0][2]
		tot_mk = 0
		for m in mk:
			sks = self.pool.get('master.matakuliah').browse(cr,uid,m,context=context).sks
			tot_mk += int(sks)

		toleransi_sks = vals['max_sks']	
		if tot_mk > toleransi_sks :
			raise osv.except_osv(_('Error!'), _('Total matakuliah melebihi batas maximal SKS !'))		

		return super(master_kurikulum, self).create(cr, uid, vals, context=context)

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

	def _get_total_sks(self,cr,uid,ids,field,args,context=None):
		result = {}
		sult = 0
		for res in self.browse(cr,uid,ids[0],context=context).kurikulum_detail_ids:
			sks = res.sks
			sult += int(sks)
		# if sult > self.browse(cr,uid,ids[0]).max_sks :
		# 		raise openerp.exceptions.Warning(_('Error!'), _('Jumlah SKS melebihi batas maximal SKS yang ditentukan !'))			

		result[ids[0]] = sult
		return result

	def _get_total_sks2(self,cr,uid,ids,field,args,context=None):
		
		result = {}
		sult = 0
		for res in self.browse(cr,uid,ids[0],context=context).total_mk_ids:
			sks = res.sks
			sult += int(sks)
			
		result[ids[0]] = sult
		return result 

	def _get_total_mk_kurikulum(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		tahun_ajaran_id = self.browse(cr,uid,ids[0]).tahun_ajaran_id.id
		prodi_id = self.browse(cr,uid,ids[0]).prodi_id.id
		cr.execute("""SELECT kmr.matakuliah_id kmr
						FROM kurikulum_mahasiswa_rel kmr
						LEFT JOIN master_matakuliah mm ON mm.id = kmr.matakuliah_id
						LEFT JOIN master_kurikulum mk ON kmr.kurikulum_id = mk.id 
						WHERE mk.tahun_ajaran_id ="""+ str(tahun_ajaran_id) +""" 
						AND mk.prodi_id = """+ str(prodi_id) +"""
						AND mk.state = 'confirm'""")		   
		mk = cr.fetchall()			
		if mk == []:
			return result
		mk_ids= []
		for m in mk:
			if m[0] not in mk_ids:
				mk_ids.append(m[0])		
		result[ids[0]] = mk_ids
		return result

	_columns = {
		'name' :fields.char('Kode Kurikulum', size=28,required = True,ondelete="cascade"),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required = True),         
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',required = True),           
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required = True),
		'semester_id':fields.many2one('master.semester','Semester',required = True),
		'max_sks':fields.integer('Max Total SKS',required = True,help="Maksimal SKS dalam satu KRS"),
		'min_ip':fields.float('Min Indeks Prestasi',required = True,help="Minimal indeks prestasi untuk bisa ambil matakuliah tambahan dalam KRS"),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Ajaran',required = True),
		'state':fields.selection([('draft','Draft'),('confirm','Confirm')],string="Status",required = True),
		'kurikulum_detail_ids':fields.many2many(
			'master.matakuliah',   	# 'other.object.name' dengan siapa dia many2many
			'kurikulum_mahasiswa_rel',       # 'relation object'
			'kurikulum_id',               # 'actual.object.id' in relation table
			'matakuliah_id',           # 'other.object.id' in relation table
			'Daftar Mata Kuliah',		# 'Field Name'  
			domain="['|',('prodi_id','=',prodi_id),\
			('jenis','=','mk_umum')]",),	   
		'total_sks':fields.function(_get_total_sks,type="integer",string="Total SKS"),         			
		'total_mk_ids' : fields.function(_get_total_mk_kurikulum, type='many2many', relation="master.matakuliah", string="Total Mata Kuliah",readonly=True),
		'total_sks2':fields.function(_get_total_sks2,type="integer",string="Total SKS"), 
			}
			
	_sql_constraints = [('name_uniq', 'unique(name)','Kode kurikulum tidak boleh sama')]

	_defaults = {
		'state' : 'draft',
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.kurikulum'), 
	}

	def confirm(self,cr,uid,ids,context=None):		
		return self.write(cr,uid,ids,{'state':'confirm'},context=context)

	def cancel(self,cr,uid,ids,context=None):		
		return self.write(cr,uid,ids,{'state':'draft'},context=context)			

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(master_kurikulum, self).unlink(cr, uid, ids, context=context)					
			
master_kurikulum()