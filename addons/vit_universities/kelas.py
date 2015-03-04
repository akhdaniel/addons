from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class master_kelas (osv.Model):
	_name = 'master.kelas'

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'nama'], context=context)
		res = []
		for record in reads:
			name= record['name']
			if record['nama']:
				name = '['+record['name'] +']'+ ' ' + record['nama']
			res.append((record['id'], name))
		return res

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
		'name' :fields.char('Kode',size=36,required = True),
		'nama' :fields.char('Nama',size=128),
		#'semester_id':fields.many2one('master.semester','Semester'),
		'prodi_id':fields.many2one('master.prodi','Program Studi',required = True),
		'jurusan_id':fields.many2one('master.jurusan','Jurusan',required = True),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required = True),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Ajaran',required = True),
		'kuota':fields.integer('Kuota',required = True),
		'state':fields.selection([('draft','Draft'),('confirm','Confirm')],'Status'),
		'partner_ids':fields.many2many(
			'res.partner',   	# 'other.object.name' dengan siapa dia many2many
			'kelas_mahasiswa_rel',          # 'relation object'
			'kelas_id',               # 'actual.object.id' in relation table
			'partner_id',           # 'other.object.id' in relation table
			'Mahasiswa',              # 'Field Name'
			domain="[('status_mahasiswa','=','Mahasiswa'), \
			('tahun_ajaran_id','=',tahun_ajaran_id),\
			('fakultas_id','=',fakultas_id),\
			('jurusan_id','=',jurusan_id),\
			('prodi_id','=',prodi_id),\
			('kelas_id','=',False)]",
			readonly=False),    			
		'employee_id':fields.many2one('hr.employee', domain="[('is_dosen','=',True)]",required = True,string="Dosen Wali"),
			}

	_defaults = {  
		'kuota':1,
		'state':'draft',
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.kelas'), 
				}
			
	_sql_constraints = [('name_uniq', 'unique(name)','Kode kelas tidak boleh sama')]

	def onchange_kelas(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, jurusan_id, prodi_id,kuota,context=None):

		results = {}
		if not prodi_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			('jurusan_id','=',jurusan_id),
			('prodi_id','=',prodi_id),
			('kelas_id','=',False)], context=context)

		#import pdb;pdb.set_trace()
		res = []
		x=0
		for peserta in par_ids:
			x += 1			
			if x > kuota :
				break
			res.append(peserta)
		#insert many2many records
		wisuda_line_ids = [(6,0,res)]
		results = {
			'value' : {
				'partner_ids' : wisuda_line_ids,
			}
		}
		return results

	def button_reload(self,cr,uid,ids,context=None):

		my_form = self.browse(cr,uid,ids[0])
		tahun_ajaran_id = my_form.tahun_ajaran_id.id
		fakultas_id = my_form.fakultas_id.id
		jurusan_id = my_form.jurusan_id.id
		prodi_id = my_form.prodi_id.id
		kuota = my_form.kuota

		par_obj = self.pool.get('res.partner')

		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			('jurusan_id','=',jurusan_id),
			('prodi_id','=',prodi_id),
			('kelas_id','=',False)], context=context)
		res = []
		x=0
		for peserta in par_ids:
			x += 1			
			if x > kuota :
				break
			res.append(peserta)
		#insert many2many records
		peserta_line_ids = [(6,0,res)]
		
		self.write(cr,uid,ids[0],{'partner_ids':peserta_line_ids,},context=context)
		return True

	def confirm(self,cr,uid,ids,context=None):
		my_form = self.browse(cr,uid,ids[0])
		for mhs in my_form.partner_ids:
			#import pdb;pdb.set_trace()
			self.pool.get('res.partner').write(cr,uid,mhs.id,{'kelas_id':my_form.id},context=context)
		self.write(cr,uid,ids,{'state':'confirm'},context=context)
		return True	

	def cancel(self,cr,uid,ids,context=None):
		my_form = self.browse(cr,uid,ids[0])
		for mhs in my_form.partner_ids:
			self.pool.get('res.partner').write(cr,uid,mhs.id,{'kelas_id':False},context=context)		
		self.write(cr,uid,ids,{'state':'draft'},context=context)
		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(master_kelas, self).unlink(cr, uid, ids, context=context)
			
master_kelas()
