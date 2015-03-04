from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class academic_year(osv.Model):
	''' Defining an academic year '''
	_name = "academic.year"
	_description = "Academic Year"
	_rec_name = "code"
	_order = "code"

	_columns = {
		#'sequence': fields.integer('Urutan', required=True, help="Urutan yang akan di tampilkan."),
		'name': fields.char('Nama', size=64, select=1),
		'code': fields.char('Kode', size=6, required=True),
		'date_start': fields.date('Tanggal Mulai', required=True),
		'date_stop': fields.date('Tanggal Berakhir', required=True),
		'month_ids': fields.one2many('academic.month', 'year_id', 'Bulan', help="related Academic months"),
		#'grade_id' : fields.many2one('grade.master', "Grade"),
		'description': fields.text('Deskripsi'),
		'mekanisme_nilai' :fields.selection([('terbaru','Nilai Terbaru'),('terbaik','Nilai Terbaik')],'Mekanisme Nilai',required=True,
				help='Mekanisme pengambilan nilai di transkrip jika remedial/her \
					\n* Terbaru = Jika terdapat 2 atau lebih matakuliah yang sama maka di ambil yang terbaru sesuai tanggal KHS. \
					\n* Terbaik = Jika terdapat 2 atau lebih matakuliah yang sama maka di ambil yang terbaik sesuai tanggal KHS.'),
		'max_mk': fields.integer('Maksimal Matakuliah',required=True,help='Jumlah maksimal matakuliah BL untuk bisa mengajukan judul'),
	}

	_sql_constraints = [('code_uniq', 'unique(code)','Kode tahun akademik tidak boleh sama')]

	_defaults = {
		'mekanisme_nilai':'terbaru',

	}

	def create_period(self, cr, uid, ids, context=None, interval=1):
		period_obj = self.pool.get('academic.month')
		for fy in self.browse(cr, uid, ids, context=context):
			ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
			period_obj.create(cr, uid, {
					'name':  "%s %s" % (_('Opening Period'), ds.strftime('%Y')),
					'code': ds.strftime('00/%Y'),
					'date_start': ds,
					'date_stop': ds,
					'year_id': fy.id,
				})
			while ds.strftime('%Y-%m-%d') < fy.date_stop:
				de = ds + relativedelta(months=interval, days=-1)

				if de.strftime('%Y-%m-%d') > fy.date_stop:
					de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

				period_obj.create(cr, uid, {
					'name': ds.strftime('%m/%Y'),
					'code': ds.strftime('%m/%Y'),
					'date_start': ds.strftime('%Y-%m-%d'),
					'date_stop': de.strftime('%Y-%m-%d'),
					'year_id': fy.id,
				})
				ds = ds + relativedelta(months=interval)
		return True

	# def next_year(self, cr, uid, sequence, context=None):
	# 	year_ids = self.search(cr, uid, [('sequence', '>', sequence)])
	# 	if year_ids:
	# 		return year_ids[0]
	# 	return False

	def name_get(self, cr, uid, ids, context=None):
		res = []
		for acd_year_rec in self.read(cr, uid, ids, context=context):
			nam = "[" + acd_year_rec['code'] + "]" + acd_year_rec['name']
			res.append((acd_year_rec['id'], nam))
		return res

	def _check_academic_year(self, cr, uid, ids, context=None):
		obj_academic_ids = self.search(cr, uid, [], context=context)
		for current_academic_yr in self.browse(cr, uid, ids, context=context):
			obj_academic_ids.remove(current_academic_yr.id)
			data_academic_yr = self.browse(cr, uid, obj_academic_ids, context=context)
			for old_ac in data_academic_yr:
				if old_ac.date_start <= current_academic_yr.date_start <= old_ac.date_stop or \
					old_ac.date_start <= current_academic_yr.date_stop <= old_ac.date_stop:
					return False
		return True

	def _check_duration(self, cr, uid, ids, context=None):
		for obj_ac in self.browse(cr, uid, ids, context=context):
			if obj_ac.date_stop < obj_ac.date_start:
				return False
		return True

	_constraints = [
		(_check_duration, _('Error! The duration of the academic year is invalid.'), ['date_stop']),
		(_check_academic_year, _('Error! You cannot define overlapping academic years'), ['date_start', 'date_stop'])
	]

academic_year()

class academic_month(osv.Model):
	''' Defining a month of an academic year '''
	_name = "academic.month"
	_description = "Academic Month"
	_order = "date_start"
	_columns = {
		'name': fields.char('Nama', size=64, required=True, help='Name of Academic month'),
		'code': fields.char('Kode', size=12, required=True, help='Code of Academic month'),
		'date_start': fields.date('Awal Periode', required=True, help='Starting of Academic month'),
		'date_stop': fields.date('Akhir Periode', required=True, help='Ending of Academic month'),
		'year_id': fields.many2one('academic.year', 'Tahun Akademik', required=True, help="Related Academic year "),
		'description': fields.text('Deskripsi')
	}

	def _check_duration(self, cr, uid, ids, context=None):
		for obj_month in self.browse(cr, uid, ids, context=context):
			if obj_month.date_stop < obj_month.date_start:
				return False
		return True

	def _check_year_limit(self, cr, uid, ids, context=None):
		for obj_month in self.browse(cr, uid, ids, context=context):
			if obj_month.year_id.date_stop < obj_month.date_stop or \
			   obj_month.year_id.date_stop < obj_month.date_start or \
			   obj_month.year_id.date_start > obj_month.date_start or \
			   obj_month.year_id.date_start > obj_month.date_stop:
				return False
		return True

	_constraints = [
		(_check_duration, _('Error ! The duration of the Month(s) is/are invalid.'), ['date_stop']),
		(_check_year_limit, _('Invalid Months ! Some months overlap or the date period is not in the scope of the academic year.'), ['date_stop'])
	]

academic_month()


class master_matakuliah (osv.Model):
	_name = 'master.matakuliah'
	_rec_name= 'kode'

	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['nama', 'kode'], context=context)
		res = []
		for record in reads:
			name = record['nama']
			if record['kode']:
				name = '['+record['kode'] +']'+ ' ' + name
			res.append((record['id'], name))
		return res
	
	_columns = {
		'kode' :fields.char('Kode', 128,required = True),
		'nama' :fields.char('Nama',required = True),
		'sks':fields.char('SKS',required = True),
		'jenis':fields.selection([('mk_umum','Mata Kuliah Umum'),('mk_khusus','Mata Kuliah Khusus')],'Jenis',required = True),
		'prodi_id': fields.many2one('master.prodi','Program Studi')
		#'jadwal_ids':fields.one2many('master.jadwal','mata_kuliah_id', string='Jadwal'),
			}

	_defaults = {
		'jenis':'mk_umum',
		'kode':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.matakuliah'), 
	}
			
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode mata kuliah tidak boleh sama')]
			
master_matakuliah()

#class peserta_kelas (osv.osv):
	#_name = 'master.peserta_kelas'
	#_rec_name='partner_id'

   # _columns = {
		#'kelas_id' :fields.many2one('master.kelas',string='Kelas'),
		#'partner_id': fields.many2one('res.partner',string='Nama Mahasiswa',domain="[('status_mahasiswa','=','mahasiswa')]"),
		#'npm':fields.related('partner_id', 'npm', type='char',relation='res.partner', string='Nomor Pokok Mahasiswa',),
			#}
#peserta_kelas()

class master_ruangan (osv.Model):
	_name = 'master.ruangan'
	
	_columns = {
		'name' :fields.char('Kode Ruangan', size=26,required = True),
		'nama' :fields.char('Nama Ruangan', size=128),
		'kapasitas':fields.integer('Kapasitas Ruangan'),
		'gedung':fields.char('Gedung',size=50),
		'alamat':fields.char('Alamat',size=128),
		'ac':fields.boolean('Pendingin Ruangan'),
		'infocus':fields.boolean('Infocus'),
			}
			
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode ruangan tidak boleh sama')]           

	_defaults = {
		'kapasitas':5,
		'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'master.ruangan'), 
	}
			
master_ruangan()


class master_fakultas (osv.Model):
	_name='master.fakultas'
	   
	_columns = {
		'kode':fields.char('Kode', size=28, required = True),
		'name' : fields.char('Nama Fakultas', size=128, required = True),
			}
			
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode fakultas tidak boleh sama')]
			
master_fakultas()

class master_jurusan (osv.Model):
	_name = 'master.jurusan'
	
	_columns = {
		'kode' :fields.char('Kode', size=28, required = True),
		'name' :fields.char('Nama Jurusan',size=128, required = True),
		'fakultas_id' :fields.many2one('master.fakultas',string='Fakultas',required = True),
			}
			
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode jurusan tidak boleh sama')]
			
master_jurusan()

class master_prodi (osv.Model):
	_name = 'master.prodi'

	_columns = {
		'kode' :fields.char('Kode', size=28,required = True),
		'name' :fields.char('Nama Program Studi',size=128, required = True),
		'jurusan_id' :fields.many2one('master.jurusan',string='Jurusan',required = True),
		'gelar_id' : fields.many2one('res.partner.title',string='Gelar',required=True),
		'semester_id' : fields.many2one('master.semester','Max Semester',required = True),
		'jenjang': fields.selection([('diploma','Diploma'),('sarjana','Sarjana'),('magister','Magister'),('doctor','Doctoral')],'Jenjang',required = True),
			}
			
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode program Studi tidak boleh sama')]         
		   
master_prodi()

class jenis_pelanggaran (osv.Model):
	_name = 'master.jenis_pelanggaran'
	
	_columns = {
		'name' :fields.char('Kode', 128, required=True),
		'desc' :fields.text('Deskripsi'),
				}
  
	_sql_constraints = [('kode_uniq', 'unique(kode)','Kode jenis pelanggaran tidak boleh sama')]  
	
jenis_pelanggaran()

class master_pelanggaran (osv.Model):
	_name = 'master.pelanggaran'
	
	_columns = {
		'partner_id' :fields.many2one('res.partner','Nama Mahasiswa', required = True, ),
		'jenis_pelanggaran_id':fields.many2one('master.jenis_pelanggaran', string = 'Kode Pelanggaran'),
		'tanggal':fields.date('Tanggal Pelanggaran'),
		'nama':fields.related('jenis_pelanggaran_id','nama',type='text',relation='master.jenis_pelanggaran',string='Deskripsi',readonly=True),
			}
master_pelanggaran()

class riwayat_pendidikan (osv.Model):
	_name = 'master.riwayat_pendidikan'
	
	_columns = {
		'partner_id' :fields.many2one('res.partner','Nama Mahasiswa', required = True, ondelete='cascade',),
		'nama_sekolah':fields.char('Nama Sekolah'),
		'tingkat':fields.selection([('TK','TK'),('SD','SD'),('SMP','SMP'),('SMA','SMA/SMK/SMF'),('Diploma','Akademi/Diploma'),('S1','S1'),('S2','S2'),('S3','S3')],'Tingkat'),
		'tahun_masuk':fields.char('Tahun Masuk',size=4,),
		'tahun_lulus':fields.char('Tahun Lulus',size=4,),
		'no_ijazah':fields.char('Nomor Ijazah'),
		'nilai_akhir':fields.float('Nilai Akhir / UN',digits=(2,2)),
			}
			
riwayat_pendidikan()

class biodata_keluarga (osv.Model):
	_name = 'master.biodata_keluarga'
	
	_columns = {
		'partner_id' :fields.many2one('res.partner','Nama Mahasiswa', required = True,),
		'nama':fields.char('Nama'),
		'tempat_lahir':fields.char('Tempat Lahir'),
		'tanggal_lahir':fields.date('Tanggal Lahir'),
		'hubungan_keluarga':fields.char('Hubungan Keluarga'),
		'pekerjaan':fields.char('Pekerjaan'),
		'alamat':fields.text('Alamat'),
		'jenis_kelamin':fields.selection([('laki_laki','Laki-Laki'),('perempuan','Perempuan')],'Jenis Kelamin'),
			}
biodata_keluarga()

class master_semester(osv.Model):
	_name = 'master.semester'
	_order ="name"

	_columns={
		'name': fields.integer('Semester',required=True),
	}

	_sql_constraints = [('name_uniq', 'unique(name)','Semester tidak boleh sama')]

	_defaults ={
		'name':1,
	}

class master_nilai(osv.Model):
	_name = "master.nilai"
	_description = "Master Bobot Nilai"
	_columns = {
		'name': fields.char('Nilai Huruf', size=3, required=True),
		'bobot': fields.float('Nilai Angka',required=True,help="nilai angka harus antara 0 s/d 4"),
		'min': fields.float("Nilai Minimal",required=True,help="nilai angka harus antara 0 s/d 100"),
		'max': fields.float("Nilai Maximal",required=True,help="nilai angka harus antara 0 s/d 100"),
	}	

class master_yudisium(osv.Model):
	_name = "master.yudisium"
	_description = "Master Yudisium"
	_columns = {
		'name': fields.char('Yudisium', size=128, required=True),
		'min': fields.float("IPK Min",required=True,help="nilai angka minimal Indeks Prestasi Komulatif"),
		'max': fields.float("IPK Max",required=True,help="nilai angka maximal Indeks Prestasi Komulatif"),
	}