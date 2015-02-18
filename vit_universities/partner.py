from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


SESSION_STATES = [('calon','Calon'),('Mahasiswa','Mahasiswa'),('alumni','Alumni'),('orang_tua','Orang Tua')]
class res_partner (osv.osv):
	_name = 'res.partner'
	_inherit= 'res.partner'
	
	#def create(self, cr, uid, vals, context=None):
		#jurusan = self.pool.get('master.jurusan').browse(cr, uid, vals['jurusan_id'], context)[0]
		#nim = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')
		#vals['npm'] = jurusan.fakultas_id.kode + jurusan.kode + nim 
		#return super(partner, self).create(cr, uid, vals, context=None)
	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'npm'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['npm']:
				name = '['+record['npm'] +']'+ ' ' + name
			res.append((record['id'], name))
		return res

	def create(self, cr, uid, vals, context=None):
		#import pdb;pdb.set_trace()
		if vals['status_mahasiswa'] == 'calon':
			if vals.get('reg','/')=='/':
				vals['reg'] = self.pool.get('ir.sequence').get(cr, uid, 'res.partner') or '/'
		if vals['status_mahasiswa'] == 'Mahasiswa':
			if vals.get('npm','/')=='/':
				ta = vals['tahun_ajaran_id']
				t_idd = self.pool.get('academic.year').browse(cr,uid,ta,context=context).date_start				
				ta_tuple =  tuple(t_idd)
				ta_id = ta_tuple[2]+ta_tuple[3]#ambil 2 digit paling belakang dari tahun saja		

				fak = vals['fakultas_id']
				fak_id = self.pool.get('master.fakultas').browse(cr,uid,fak,context=context).kode

				jur = vals['jurusan_id']
				jur_id = self.pool.get('master.jurusan').browse(cr,uid,jur,context=context).kode

				pro = vals['prodi_id']
				pro_id = self.pool.get('master.prodi').browse(cr,uid,pro,context=context).kode

				sequence = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'

				vals['npm'] = ta_id+fak_id+jur_id+pro_id+sequence
		if vals['status_mahasiswa'] == 'alumni':
				raise osv.except_osv(_('Error!'), _('Data alumni harus dibuat dari data mahasiswa'))			
		return super(res_partner, self).create(cr, uid, vals, context=context)

	def _calc_age(self, cr, uid, ids, name, arg, context=None):
		''' Fungsi otomatis utk menghitung usia'''
		res = {}
		for mhs in self.browse(cr, uid, ids, context=context):
			start = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
			if mhs.tanggal_lahir:
				start = datetime.strptime(mhs.tanggal_lahir, DEFAULT_SERVER_DATE_FORMAT)
			end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
			delta = end - start
			years = (delta.days / 365)
			res[mhs.id] = years
		return res		

	_columns = {
		#Mahasiswa
		'npm' :fields.char(string='NPM',readonly=True,size=34),
		'reg': fields.char('No. Pendaftaran',readonly=True,size=34),
		# 'nama_tengah':fields.char('Nama Tengah',size=60),
		# 'nama_belakang':fields.char('Nama Tengah',size=60),
		'jenis_kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
		'tempat_lahir':fields.char('Tempat Lahir'),
		'tanggal_lahir':fields.date('Tanggal Lahir'),
		'status_mahasiswa':fields.selection(SESSION_STATES,'Status Mhs',required=True),                  
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',domain="[('fakultas_id','=',fakultas_id)]",required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('jurusan_id','=',jurusan_id)]",required=True),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas',readonly=True),                
		#'peserta_kelas_id':fields.many2one('master.peserta_kelas',string='Mahasiswa',),
		'ipk':fields.float('IPK',digits=(2,2),readonly=True),
		'judul':fields.text('Judul Tugas Akhir'),
		'wisuda':fields.date('Tanggal Wisuda'),
		'tgl_lulus':fields.date('Tanggal Lulus'),
		'no_formulir':fields.char('No Formulir Ujian'),
		'tgl_ujian':fields.date('Tanggal Ujian'),
		'nilai_ujian':fields.float('Nilai Ujian'),
		'batas_nilai':fields.float('Batas Nilai Kelulusan',readonly=True),
		'is_dosen':fields.boolean(''),
		'biodata_keluarga_ids':fields.one2many('master.biodata_keluarga','partner_id','Biodata Keluarga',),
		'riwayat_pendidikan_ids':fields.one2many('master.riwayat_pendidikan','partner_id','Riwayat Pendidikan',ondelete='cascade',),
		'pelanggaran_ids':fields.one2many('master.pelanggaran','partner_id','Pelanggaran',),
		'jadwal_ids':fields.one2many('master.jadwal','partner_id','Jadwal Mengajar',),
		'nidn':fields.char('NIDN'),
		'status_dosen':fields.selection([('tetap','Tetap'),('tidak_tetap','Tidak Tetap')],'Status Dosen'),
		#'state': fields.selection([('draft','Calon Mahasiswa'),('on_progress','Mahasiswa'),('done','Alumni')],'Status Mahasiswa'),
		'age':fields.function(_calc_age, method=True, required=True, string='Usia (Tahun)', readonly=True, type="integer"),
		'status_pernikahan':fields.selection([('belum','Belum Menikah'),('menikah','Menikah'),('janda','Janda'),('duda','Duda')],'Status Pernikahan'),
		'agama':fields.selection([('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')],'Agama'),
		'lokasi_wisuda':fields.char('Tempat Wisuda',size=128,readonly=True),
		'tgl_daftar':fields.date('Tanggal Daftar',readonly=True),
				}

	_sql_constraints = [('reg_uniq', 'unique(reg)','No. pendaftaran tidak boleh sama')]
	_sql_constraints = [('npm_uniq', 'unique(npm)','NPM tidak boleh sama')]

	def action_draft(self,cr,uid,ids,context=None):
			#set to "draft" state
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[0][0]},context=context)
			
	def action_confirm(self,cr,uid,ids,jurusan_id,context=None):
		#import pdb;pdb.set_trace()
		#jurus = self.pool.get('master.jurusan')
		val = self.browse(cr,uid,ids)[0]
		kod = val.jurusan_id.kode
		val1 = val.jurusan_id.fakultas_id.kode
		val2= val.prodi_id.kode
		nem = self.pool.get('ir.sequence').get(cr, uid, 'res.partner')        
		vals = val1+kod+val2+nem 
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[1][0],'npm':vals},context=context)
			
	def action_done(self,cr,uid,ids,context=None):
			#set to "done" state
		return self.write(cr,uid,ids,{'status_mahasiswa':SESSION_STATES[2][0]},context=context)      

	_defaults = {
		#'is_dosen':False, #(domain = [('status_mahasiswa','=','calon')]),
		#'status_mahasiswa' : SESSION_STATES[3][0],
		#'angkatan': lambda*a : time.strftime('%Y'),
		'tgl_daftar' : fields.date.context_today,
		#'npm':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'res.partner'), 
		'npm' : '/',  
		'reg': '/',
				}

res_partner()