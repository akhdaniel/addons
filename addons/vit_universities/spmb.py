from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class spmb_mahasiswa(osv.Model):
	_name = 'spmb.mahasiswa'

	def onchange_prodi(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, jurusan_id, prodi_id, kuota,context=None):
		#import pdb;pdb.set_trace()
		results = {}
		if not prodi_id:
			return results
		
		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','calon'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			('jurusan_id','=',jurusan_id),
			('prodi_id','=',prodi_id)], context=context)

		if par_ids == []:
			return results
		part_ids = tuple(par_ids)
		cr.execute("""SELECT nilai_ujian,id
						FROM res_partner
						WHERE id in """+ str(part_ids))
				   
		nlai = cr.fetchall()
		nlai_sort = sorted(nlai)
		#urutkan dari yang rerbesar dulu
		nlai_sort.reverse()
		x = 0
		res = []
		na = 0
		
		for nl in nlai_sort:
			nli = nl[0]
			idd = nl[1]
			x += 1
			if x == kuota :
				na = nli			
			if x > kuota :
				break
			res.append(idd)

		#insert many2many records
		calon_line_ids = [(6,0,res)]
		results = {
			'value' : {
				'partner_ids' : calon_line_ids,
				'nilai_min':na,
			}
		}
		return results

	_columns = {
		'name': fields.char('Kode',required=True,size=32),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'fakultas_id':fields.many2one('master.fakultas',string='Fakultas',required=True),
		'jurusan_id':fields.many2one('master.jurusan',string='Jurusan',required=True),
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required=True),		
		'kuota':fields.integer('Kuota',required=True),
		'partner_ids':fields.many2many(
			'res.partner',   	# 'other.object.name' dengan siapa dia many2many
			'filter_mahasiswa_rel',          # 'relation object'
			'filter_id',               # 'actual.object.id' in relation table
			'partner_id',           # 'other.object.id' in relation table
			'Calon Mahasiswa',              # 'Field Name'
			domain="[('status_mahasiswa','=','calon'), \
			('tahun_ajaran_id','=',tahun_ajaran_id),\
			('fakultas_id','=',fakultas_id),\
			('jurusan_id','=',jurusan_id),\
			('prodi_id','=',prodi_id),]",
			readonly=False),	
		'nilai_min':fields.float('Nilai Minimal'),
		'state':fields.selection([('draft','Draft'),('done','Lulus')],'Status'),
	}
	_defaults = {  
		'kuota': 1,
		'state':'draft',
				}

	def button_reload(self,cr,uid,ids,context=None):

		my_form = self.browse(cr,uid,ids[0])
		angkatan = my_form.tahun_ajaran_id.id
		fakultas = my_form.fakultas_id.id
		jurusan = my_form.jurusan_id.id
		prodi = my_form.prodi_id.id
		kuota = my_form.kuota

		par_obj = self.pool.get('res.partner')

		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','calon'),
			('tahun_ajaran_id','=',angkatan),
			('fakultas_id','=',fakultas),
			('jurusan_id','=',jurusan),
			('prodi_id','=',prodi)], context=context)

		if par_ids != []:
			part_ids = tuple(par_ids)
			cr.execute("""SELECT nilai_ujian,id
							FROM res_partner
							WHERE id in """+ str(part_ids))
					   
			nlai = cr.fetchall()
			nlai_sort = sorted(nlai)
			#urutkan dari yang terbesar dulu
			nlai_sort.reverse()

			x = 0
			res = []
			na = 0		
			for nl in nlai_sort:
				nli = nl[0]
				idd = nl[1]
				x += 1
				if x == kuota :
					na = nli			
				if x > kuota :
					break
				res.append(idd)
			#import pdb;pdb.set_trace()
			#insert many2many records
			calon_line_ids = [(6,0,res)]		
			self.write(cr,uid,ids[0],{'partner_ids':calon_line_ids,'nilai_min':na,},context=context)
		return True

	def confirm(self,cr,uid,ids,context=None):
		my_form = self.browse(cr,uid,ids[0])
		nilai = my_form.nilai_min
		#import pdb;pdb.set_trace()
		t_id = my_form.tahun_ajaran_id.date_start
		t_tuple =  tuple(t_id)
		t_id_final = t_tuple[2]+t_tuple[3]#ambil 2 digit paling belakang dari tahun saja
		f_id = my_form.fakultas_id.kode
		j_id = my_form.jurusan_id.kode
		p_id = my_form.prodi_id.kode
		for p in my_form.partner_ids:
			st = p.status_mahasiswa
			se = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'
			self.pool.get('res.partner').write(cr,uid,p.id,{'status_mahasiswa':'Mahasiswa','batas_nilai':nilai,'npm':t_id_final+f_id+j_id+p_id+se},context=context)
		self.write(cr,uid,ids,{'state':'done'},context=context)
		return True	


	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(spmb_mahasiswa, self).unlink(cr, uid, ids, context=context)

#class untuk menampung sequence npm di objek res.partner
class seq_npm_partner(osv.Model):
	_name = "seq.npm.partner"

	_columns = {
		'name' : fields.char('Nomor Pokok Mahasiswa',size=36),
	}