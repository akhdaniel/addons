from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class spmb_mahasiswa(osv.Model):
	_name = 'spmb.mahasiswa'    

	def onchange_prodi(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, prodi_id, kuota, nilai,context=None):
		
		results = {}
		if not prodi_id:
			return results
		
		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','calon'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('fakultas_id','=',fakultas_id),
			# ('jurusan_id','=',jurusan_id),
			('prodi_id','=',prodi_id),
			('jenis_pendaftaran_id','=',1),
			('nilai_ujian','>=',nilai)], context=context)

		if par_ids == []:
			return results
		if len(par_ids) == 1:
			part_ids = par_ids[0]
			cr.execute("""SELECT nilai_ujian,id
							FROM res_partner
							WHERE id = """+ str(part_ids))			
		else:
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
			if x <= kuota :
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
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',domain="[('jurusan_id','=',jurusan_id)]",required=True),		
		'kuota':fields.integer('Kuota',required=True),
		'nilai':fields.integer('Nilai Minimal',required=True),
		'partner_ids':fields.many2many(
			'res.partner',   	# 'other.object.name' dengan siapa dia many2many
			'filter_mahasiswa_rel',          # 'relation object'
			'filter_id',               # 'actual.object.id' in relation table
			'partner_id',           # 'other.object.id' in relation table
			'Calon Mahasiswa',              # 'Field Name'
			domain="[('status_mahasiswa','=','calon'), \
			('tahun_ajaran_id','=',tahun_ajaran_id),\
			('fakultas_id','=',fakultas_id),\
			('prodi_id','=',prodi_id),]",
			readonly=False),	
		'nilai_min':fields.float('Nilai Minimal Calon Mahasiswa Saat Ini',readonly=True),
		'state':fields.selection([('draft','Draft'),('done','Lulus')],'Status'),
	}
	_defaults = {  
		'kuota': 1,
		'state':'draft',
				}

	def button_reload(self,cr,uid,ids,context=None):
		results = {}
		my_form = self.browse(cr,uid,ids[0])
		angkatan = my_form.tahun_ajaran_id.id
		fakultas = my_form.fakultas_id.id
		prodi = my_form.prodi_id.id
		kuota = my_form.kuota
		nilai = my_form.nilai

		par_obj = self.pool.get('res.partner')

		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','calon'),
			('tahun_ajaran_id','=',angkatan),
			('fakultas_id','=',fakultas),
			# ('jurusan_id','=',jurusan),
			('prodi_id','=',prodi),
			('jenis_pendaftaran_id','=',1),
			('nilai_ujian','>=',nilai)], context=context)
		#import pdb;pdb.set_trace()
		if par_ids == []:
			return results
		if len(par_ids) == 1:
			part_ids = par_ids[0]
			cr.execute("""SELECT nilai_ujian,id
							FROM res_partner
							WHERE id = """+ str(part_ids))			
		else:
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
			if x <= kuota :
				na = nli			
			if x > kuota :
				break
			res.append(idd)
		
		#insert many2many records
		calon_line_ids = [(6,0,res)]		
		self.write(cr,uid,ids[0],{'partner_ids':calon_line_ids,'nilai_min':na,},context=context)
		return True

	def confirm(self,cr,uid,ids,context=None):

		bea_obj = self.pool.get('beasiswa.prodi')
		calon_obj = self.pool.get('res.partner.calon.mhs')
		my_form = self.browse(cr,uid,ids[0])

		nilai = my_form.nilai_min
		#import pdb;pdb.set_trace()
		t_id = my_form.tahun_ajaran_id.date_start
		t_tuple =  tuple(t_id)
		t_id_final = t_tuple[2]+t_tuple[3]#ambil 2 digit paling belakang dari tahun saja
		f_id = my_form.fakultas_id.kode
		
		# j_id = my_form.jurusan_id.kode
		# j_id = my_form.prodi_id.kode

		# if j_id.find(".") != -1:
		# 	j = j_id.split(".")
		# 	j_id = j[1]

		p_id = my_form.prodi_id.kode

		if p_id.find(".") != -1:
			j = p_id.split(".")
			p_id = j[1]

		#batas nilai penerima beasiswa
		limit_bea = 1000 # default nilai besar supaya tidak ada yg lolos
		data_bea = bea_obj.search(cr,uid,[('is_active','=',True),
											('tahun_ajaran_id','=',my_form.tahun_ajaran_id.id),
											('fakultas_id','=',my_form.fakultas_id.id),
											('prodi_id','=',my_form.prodi_id.id),],context=context)
		if data_bea:
			bea_browse=bea_obj.browse(cr,uid,data_bea[0])
			if bea_browse.product_id1:
				limit_bea = bea_browse.limit_nilai_sma

		for p in my_form.partner_ids:
			is_bea = False
			if p.nilai_beasiswa >= limit_bea:
				is_bea = True
			st = p.status_mahasiswa
			nilai_sma = p.nilai_beasiswa
			jp_id = p.jenis_pendaftaran_id.code

			se = self.pool.get('ir.sequence').get(cr, uid, 'seq.npm.partner') or '/'

			# sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and jurusan_id=%s and tahun_ajaran_id=%s" % (
			sql = "select count(*) from res_partner where jenis_pendaftaran_id=%s and prodi_id=%s and tahun_ajaran_id=%s and status_mahasiswa='Mahasiswa' " % (
				p.jenis_pendaftaran_id.id, 
				my_form.prodi_id.id, 
				my_form.tahun_ajaran_id.id)
			cr.execute(sql)
			#import pdb; pdb.set_trace()
			hasil = cr.fetchone()
			if hasil and hasil[0] != None:
				se = "%04d" % (hasil[0] + 1)
			else:
				se = "0001"

			self.pool.get('res.partner').write(cr,uid,p.id,{
				'status_mahasiswa':'Mahasiswa',
				'batas_nilai':nilai,
				# 'npm':t_id_final+f_id+j_id+p_id+se,
				'npm':t_id_final + p_id + jp_id + se,#t_id_final +pend+ f_id+p_id +lokasi+ jp_id + se
				'user_id':uid,
				'is_beasiswa':is_bea},
				context=context)
			cr.commit()
			#create data calon yang lulus tersebut ke tabel res.partner.calon.mhs agar ada history terpisah
			calon_obj.create(cr,uid,{'reg'				:p.reg,
									'name'				:p.name,
									'jenis_kelamin'		:p.jenis_kelamin or False,
									'tempat_lahir'		:p.tempat_lahir or False,
									'tanggal_lahir'		:p.tanggal_lahir or False,                  
									'fakultas_id'		:p.fakultas_id.id,
									# 'jurusan_id'		:p.jurusan_id.id,
									'prodi_id'			:p.prodi_id.id,
									'tahun_ajaran_id'	:p.tahun_ajaran_id.id,                
									'tgl_lulus'			:p.tgl_lulus or False,
									'no_formulir'		:p.no_formulir or False,
									'tgl_ujian'			:p.tgl_ujian or False,
									'nilai_ujian'		:p.nilai_ujian or False,
									'batas_nilai'		:nilai,
									'status_pernikahan'	:p.status_pernikahan or False,
									'agama'				:p.agama or False,
									'tgl_daftar'		:p.tgl_daftar or False,
									'nilai_beasiswa'	:nilai_sma or False,
									'is_beasiswa' 		:is_bea,
									'date_move'			:time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
									'user_id'			:uid},									
									context=context)

			#####################################################################################
			# fitur untuk pembuatan draft invoice full sampai semester terakhir di hilangkan dulu
			#####################################################################################
			# if my_form.tahun_ajaran_id.type == 'flat':
			# 	byr_obj = self.pool.get('master.pembayaran')
			# 	byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',my_form.tahun_ajaran_id.id),
			# 		('fakultas_id','=',my_form.fakultas_id.id),
			# 		('jurusan_id','=',my_form.jurusan_id.id),
			# 		('prodi_id','=',my_form.prodi_id.id),
			# 		('state','=','confirm'),
			# 		])
				
			# 	if byr_sch != []:
			# 		byr_bws = byr_obj.browse(cr,uid,byr_sch,context=context)[0]
					
			# 		#biaya_ids = []
			# 		for biaya in byr_obj.browse(cr,uid,byr_sch,context=context)[0].product_ids:
			# 			pel_id = biaya.id
			# 			#import pdb;pdb.set_trace()
			# 			#pel = biaya_ids.append(pel_id)
			# 			self.pool.get('account.invoice').create(cr,uid,{
			# 				'partner_id':p.id,
			# 				'type':'out_invoice',
			# 				'account_id':p.property_account_receivable.id,
			# 				'invoice_line':[(0, 0, {'product_id':pel_id,'name':biaya.name,'price_unit':biaya.list_price})],
			# 				},context=context)
		self.write(cr,uid,ids,{'state':'done'},context=context)
		return True	


	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Invalid Action!'), _('The data can be removed only with the status of the draft'))
		return super(spmb_mahasiswa, self).unlink(cr, uid, ids, context=context)

#class untuk menampung sequence npm di objek res.partner
class seq_npm_partner(osv.Model):
	_name = "seq.npm.partner"

	_columns = {
		'name' : fields.char('Nomor Induk Mahasiswa',size=36),
	}