from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import netsvc

class operasional_krs (osv.Model):
	_name= 'operasional.krs'
	_rec_name='kode'

	def add_discount_sequence(self, cr, uid, ids ,disc,inv_line,bea_line_obj,partner,semester,jml_inv,inv_ids,amount_total, context=None):
		disc_ids = map(lambda x: x[0], disc)
		for bea_line in bea_line_obj.browse(cr,uid,disc_ids):
			disc_code 	= bea_line.code
			disc_id 	= bea_line.product_id.id
			disc_name 	= bea_line.name
			disc_nilai 	= bea_line.limit_nilai
			disc_amount	= amount_total - (amount_total*bea_line.amount/100)
			disc_coa  	= bea_line.product_id.property_account_income.id
			if not disc_coa:
				disc_coa = bea_line.product_id.categ_id.property_account_income_categ.id	
			if disc_code == '0':
				if partner.nilai_beasiswa >= disc_nilai: 
					for inv in inv_ids:	
						inv_line.create(cr,uid,{'invoice_id': inv,
												'product_id': disc_id,
												'name'		: disc_name,
												'quantity'	: 1 ,
												'price_unit': -disc_amount,
												'account_id': disc_coa},context=context)
					break															  						
			elif disc_code == '1':
				if partner.keluarga_alumni_id: 
					for inv in inv_ids:	
						inv_line.create(cr,uid,{'invoice_id': inv,
												'product_id': disc_id,
												'name'		: disc_name,
												'quantity'	: 1 ,
												'price_unit': -disc_amount,
												'account_id': disc_coa},context=context)
					break						
			elif disc_code == '2':
				for inv in inv_ids:	
					inv_line.create(cr,uid,{'invoice_id': inv,
											'product_id': disc_id,
											'name'		: disc_name,
											'quantity'	: 1 ,
											'price_unit': -disc_amount,
											'account_id': disc_coa},context=context)
				break	
			elif disc_code == '3':
				if partner.karyawan_id: 
					for inv in inv_ids:	
						inv_line.create(cr,uid,{'invoice_id': inv,
												'product_id': disc_id,
												'name'		: disc_name,
												'quantity'	: 1 ,
												'price_unit': -disc_amount,
												'account_id': disc_coa},context=context)
					break	
			elif disc_code == '4':
				krs_sebelumnya = self.search(cr,uid,[('partner_id','=',partner.id),('semester_id','=',semester.id-1)])
				if krs_sebelumnya:
					if self.browse(cr,uid,krs_sebelumnya[0]).ips_field_persemester >= disc_nilai :
						for inv in inv_ids:	
							inv_line.create(cr,uid,{'invoice_id': inv,
													'product_id': disc_id,
													'name'		: disc_name,
													'quantity'	: 1 ,
													'price_unit': -disc_amount,
													'account_id': disc_coa},context=context)
						break
		return True


	def add_discount(self, cr, uid, ids ,inv_obj, context=None):
		# search inv atas KRS ini
		inv_ids = inv_obj.search(cr,uid,[('krs_id','=',ids)])
		if inv_ids:
			inv_browse 		= inv_obj.browse(cr,uid,inv_ids[0])
			partner 		= inv_browse.krs_id.partner_id
			tahun_ajaran 	= inv_browse.krs_id.tahun_ajaran_id
			fakultas 		= inv_browse.krs_id.fakultas_id
			prodi 			= inv_browse.krs_id.prodi_id 
			semester 		= inv_browse.krs_id.semester_id
			jml_inv 		= len(inv_ids)
			amount_total 	= inv_browse.amount_total
			bea_obj 		= self.pool.get('beasiswa.prodi')
			data_bea 		= bea_obj.search(cr,uid,[('is_active','=',True),
												('tahun_ajaran_id','=',tahun_ajaran.id),
												('fakultas_id','=',fakultas.id),
												('prodi_id','=',prodi.id),],context=context)
			if data_bea :
				inv_line = self.pool.get('account.invoice.line')
				bea_line_obj = self.pool.get('beasiswa.prodi.detail')	

				#########################################################
				# cari dan hitung disc yg memerlukan sequence
				#########################################################
				cr.execute("""SELECT id
								FROM beasiswa_prodi_detail
								WHERE sequence >= 0
								AND beasiswa_prodi_id = %s
								AND ( %s between from_smt_id AND to_smt_id)
								ORDER BY sequence ASC """%(data_bea[0],semester.id))
				disc_seq = cr.fetchall()
				if disc_seq :				
					self.add_discount_sequence(cr, uid, ids ,disc_seq,inv_line,bea_line_obj,partner,semester,jml_inv,inv_ids,amount_total, context=context)


				#########################################################
				# cari dan hitung disc yg tidak memerlukan sequence
				#########################################################
				cr.execute("""SELECT id
								FROM beasiswa_prodi_detail
								WHERE sequence < 0
								AND beasiswa_prodi_id = %s
								AND ( %s between from_smt_id AND to_smt_id)
								ORDER BY sequence ASC """%(data_bea[0],semester.id))
				disc_non_seq = cr.fetchall()
				if disc_non_seq :
					self.add_discount_sequence(cr, uid, ids ,disc_non_seq,inv_line,bea_line_obj,partner,semester,jml_inv,inv_ids,amount_total, context=context)

		return True

	def create(self, cr, uid, vals, context=None):
		prod_obj 		= self.pool.get('product.product')
		inv_obj 		= self.pool.get('account.invoice')
		inv_line_obj 	= self.pool.get('account.invoice.line')
		smt_obj 		= self.pool.get('master.semester')
		if vals.get('kode','/')=='/':
			npm = vals['npm']
			if not npm :
				npm = '<<nim_kosong>> '
			smt = vals['semester_id']
			smt_browse = smt_obj.browse(cr,uid,smt,context=context)
			smt_name = smt_browse.name
			vals['kode'] = npm +'-'+str(smt_name) or '/'
		if 'kurikulum_id' in vals :
			if vals['kurikulum_id']:
				kurikulum = vals['kurikulum_id']
				klm_brw = self.pool.get('master.kurikulum').browse(cr,uid,kurikulum)
				t_sks = klm_brw.max_sks
				sks_kurikulum = 0
				mk_ids_kurikulum = []
				for klm in klm_brw.kurikulum_detail_ids:
					mk_ids_kurikulum.append(klm.id)
					sks_kurikulum += int(klm.sks)

				mk_ids = []
				#import pdb;pdb.set_trace()
				if 'krs_detail_ids' in vals:
					mk = vals['krs_detail_ids']
					tot_mk = 0
					for m in mk:
						if len([m]) > 1 :
							mk_id = m[2]['mata_kuliah_id']
							mk_ids.append(mk_id)
							sks = m[2]['sks']
							tot_mk += int(sks)

					if tot_mk > t_sks  :
						raise osv.except_osv(_('Error!'), _('Total matakuliah (%s SKS) melebihi batas maximal SKS kurikulum (%s SKS) !')%(tot_mk,t_sks))	
					
					# #cek jika mengambil matakuliah lebih
					# tambahan_mk = 0
					# ids_tambahan_mk = []#ambil id matakuliah yang diinput lebih
					# for tambahan in mk:
					# 	if tambahan[2]['mata_kuliah_id'] not in mk_ids_kurikulum:
					# 		mk_id = tambahan[2]['mata_kuliah_id']
					# 		sks = self.pool.get('master.matakuliah').browse(cr,uid,mk_id,context=context).sks
					# 		tambahan_mk += int(sks)
					# 		ids_tambahan_mk.append(mk_id)
					# selisih_tambahan_mk = t_sks - sks_kurikulum
					
					# #pastikan matakuliah yang di tambah tidak lebih dari jatah yg bisa di inputkan
					# if selisih_tambahan_mk > tambahan_mk :			
					# 	raise osv.except_osv(_('Error!'), _('Total matakuliah (%s SKS) melebihi batas maximal SKS (%s SKS) !')%(selisih_tambahan_mk,tambahan_mk))
				#cek juga apa di setingan kurikulum mengijinkan tambah MK sesuai dengan minimal IP sementara
				if klm_brw.min_ip > 0 : #settingan IP di kurikulum harus di isi angka positif
					if len(mk_ids) > len(mk_ids_kurikulum) :
						#hitung IP sementara partner ini
						cr.execute("""SELECT okd.id, okd.mata_kuliah_id
										FROM operasional_krs_detail okd
										LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
										WHERE ok.partner_id = %s
										AND ok.state <> 'draft'"""%(vals['partner_id']))
						dpt = cr.fetchall()
						
						det_id = map(lambda x: x[0], dpt)
						total_mk_ids = map(lambda x: x[1], dpt)
						# for x in dpt:
						# 	x_id = x[0]
						# 	det_id.append(x_id)
						# 	total_mk_ids.append(x[1])

						#cek mk yang dinput lebih harus yang belum di tempuh pada semester sebelumnya
						mk_baru_ids = []
						if ids_tambahan_mk != []:
							for mk_krs in ids_tambahan_mk:	#mk yang baru di tambah
								if mk_krs not in total_mk_ids:#mk-mk yg telah ditempuh pd semester sebelumnya
									mk_baru_ids.append(mk_krs)

						det_sch = self.pool.get('operasional.krs_detail').browse(cr,uid,det_id,context=context)
						sks = 0
						bobot_total = 0.00
						total_mk_ids = []	
						for det in det_sch:
							sks += det.sks
							bobot_total += (det.nilai_angka*det.sks)			

						### ips = (total nilai angka*total sks) / total sks
						if sks == 0:
							ips = 0
						else :
							ips = round(bobot_total/sks,2)
					
						#jika ada mk bru yg di inputkan dan ip tidak memenuhi syarat
						if ips <= klm_brw.min_ip :
							if mk_baru_ids != []:
								raise osv.except_osv(_('Error!'), _('Indeks Prestasi Sementara (%s) kurang dari standar minimal untuk tambah matakuliah semester depan(%s) !')%(ips,klm_brw.min_ip))	



		#cek partner dan semester yang sama
		krs_uniq = self.search(cr,uid,[('partner_id','=',vals['partner_id']),('semester_id','=',vals['semester_id'])])
		if krs_uniq != []:
			raise osv.except_osv(_('Error!'),
								_('KRS untuk mahasiswa dengan semester ini sudah dibuat!'))	

		#langsung create invoice nya
		#import pdb;pdb.set_trace()
		#kecuali smt 1
		smt1_exist = smt_obj.search(cr,uid,[('name','=',1)])
		smt1_id = smt_obj.browse(cr,uid,smt1_exist[0]).id

		smt2_exist = smt_obj.search(cr,uid,[('name','=',2)])
		smt2_id = smt_obj.browse(cr,uid,smt2_exist[0]).id

		my_krs_id = super(operasional_krs, self).create(cr, uid, vals, context=context)	

		if 'state' not in vals and vals['semester_id'] != smt1_id:			
			byr_obj = self.pool.get('master.pembayaran')
			byr_sch = byr_obj.search(cr,uid,[('tahun_ajaran_id','=',vals['tahun_ajaran_id']),
				('fakultas_id','=',vals['fakultas_id']),
				# ('jurusan_id','=',vals['jurusan_id']),
				('prodi_id','=',vals['prodi_id']),
				('state','=','confirm'),
				])		
			if byr_sch != []:
				byr_brw = byr_obj.browse(cr,uid,byr_sch[0],context=context)
				list_pembayaran = byr_brw.detail_product_ids
				inv_ids = []
				for bayar in list_pembayaran:
					
					#jika menemukan semester yang sama
					if vals['semester_id'] == bayar.semester_id.id:
						partner_obj = self.pool.get('res.partner')
						partner = partner_obj.browse(cr,uid,vals['partner_id'])
						split_invoice = partner.split_invoice
						# if split_invoice < 1:
						# 	split_invoice = 1
						# elif split_invoice > 10: # proteksi jika salah input / input terlalu besar, set maks 10 x split
						# 	split_invoice = 10
						# if split_invoice == 1:
						if split_invoice :														
							cr.execute("""SELECT pp.id,pt.name,pbd.total
											FROM product_pembayaran_detail_rel pb_rel 
											LEFT JOIN product_product pp on pb_rel.product_id = pp.id
											LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id
											LEFT JOIN master_pembayaran_detail pbd on pbd.id = pb_rel.pembayaran_detail_id   
											WHERE pb_rel.pembayaran_detail_id ="""+ str(bayar.id) +""" 
											""")		   
							no_split = cr.fetchall()

							if no_split :
								# product_id 		= map(lambda x: x[0], split_true) # atau  [i for (i,) in res] 							
								# product_name 	 	= map(lambda x: x[1], split_true)
								# product_price 	= map(lambda x: x[2], split_true)
								prod_id = []
								for det in no_split :
									product = prod_obj.browse(cr,uid,det[0])
									coa_line = product.property_account_income.id
									if not coa_line:
										coa_line = product.categ_id.property_account_income_categ.id
									prod_id.append((0,0,{'product_id'	: det[0],
														 'name'			: det[1],
														 'price_unit'	: det[2],
														 'account_id'	: coa_line}))
								inv = inv_obj.create(cr,uid,{
									'partner_id':vals['partner_id'],
									'origin': str(self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).npm) +'-'+ str(self.pool.get('master.semester').browse(cr,uid,vals['semester_id']).name),
									'type':'out_invoice',
									'krs_id': my_krs_id,
									'fakultas_id': vals['fakultas_id'],
									'prod_id': vals['prodi_id'],
									'account_id':self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).property_account_receivable.id,
									'invoice_line': prod_id,
									},context=context)
								inv_ids.append(inv)
								#break

						# elif split_invoice > 1:	
							
						# 	# cari product yang bisa split juga
						# 	cr.execute("""SELECT pp.id,pt.name,pt.list_price
						# 					FROM product_pembayaran_detail_rel pb_rel 
						# 					LEFT JOIN product_product pp on pb_rel.product_id = pp.id
						# 					LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id  
						# 					WHERE pb_rel.pembayaran_detail_id ="""+ str(bayar.id) +""" 
						# 					AND pp.split_invoice = True """)		   
						# 	split_true = cr.fetchall()
						# 	if split_true:
						# 		for rg in range(0,split_invoice) :
						# 			prod_split_id = []
						# 			for det in split_true :
						# 				product = prod_obj.browse(cr,uid,det[0])
						# 				coa_line = product.property_account_income.id
						# 				if not coa_line:
						# 					coa_line = product.categ_id.property_account_income_categ.id
						# 				prod_split_id.append((0,0,{'product_id'	: det[0],
						# 												'name'  		: det[1],
						# 												'price_unit'	: det[2]/split_invoice,
						# 												'account_id'	: coa_line}))											
						# 			inv = inv_obj.create(cr,uid,{
						# 				'partner_id':vals['partner_id'],
						# 				'origin': str(self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).npm) +'-'+ str(self.pool.get('master.semester').browse(cr,uid,vals['semester_id']).name),
						# 				'type':'out_invoice',
						# 				'krs_id': my_krs_id,
						# 				'fakultas_id': vals['fakultas_id'],
						# 				'prod_id': vals['prodi_id'],
						# 				'account_id':self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).property_account_receivable.id,
						# 				'invoice_line': prod_split_id,
						# 				},context=context)
						# 			inv_ids.append(inv)
						# 		cr.commit()	

						# 	# cari product yang tidak bisa split			
						# 	cr.execute("""SELECT pp.id,pt.name,pt.list_price
						# 					FROM product_pembayaran_detail_rel pb_rel 
						# 					LEFT JOIN product_product pp on pb_rel.product_id = pp.id
						# 					LEFT JOIN product_template pt on pt.id=pp.product_tmpl_id  
						# 					WHERE pb_rel.pembayaran_detail_id ="""+ str(bayar.id) +""" 
						# 					AND pp.split_invoice = False """)		   
						# 	split_false = cr.fetchall()	
						# 	if split_false:
						# 		inv_exist = inv_obj.search(cr,uid,[('krs_id','=',my_krs_id)])
						# 		prod_split_false_id = []
						# 		for det in split_false:
						# 			product = prod_obj.browse(cr,uid,det[0])
						# 			coa_line = product.property_account_income.id
						# 			if not coa_line:
						# 				coa_line = product.categ_id.property_account_income_categ.id
						# 			prod_split_false_id.append((0,0,{'product_id'	: det[0],
						# 											'name'  		: det[1],
						# 											'price_unit'	: det[2],
						# 											'account_id'	: coa_line}))

						# 			# jika sudah ada invoice lain dg product yg bisa displit, insertkan di inv tsb
						# 			if inv_exist :
						# 				inv_obj.write(cr,uid,inv_exist[0],{'invoice_line' : prod_split_false_id})

						# 		# jika belum ada invoice lain dg product yg bisa displit, create inv baru	
						# 		if not inv_exist :
						# 			inv = inv_obj.create(cr,uid,{
						# 				'partner_id':vals['partner_id'],
						# 				'origin': str(self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).npm) +'-'+ str(self.pool.get('master.semester').browse(cr,uid,vals['semester_id']).name),
						# 				'type':'out_invoice',
						# 				'krs_id': my_krs_id,
						# 				'fakultas_id': vals['fakultas_id'],
						# 				'prod_id': vals['prodi_id'],
						# 				'account_id':self.pool.get('res.partner').browse(cr,uid,vals['partner_id']).property_account_receivable.id,
						# 				'invoice_line': prod_split_false_id,
						# 				},context=context)
						# 			inv_ids.append(inv)
						# if inv_id :
						# 	inv = {'invoice_id':inv_id}
						# 	vals = dict(vals.items()+inv.items())	
			cr.commit()
			#cek jika ada Discount
			self.add_discount(cr, uid, my_krs_id, inv_obj, context=context)

			# selain smt 2 langsung validate
			if vals['semester_id'] != smt2_id :
				for invoice in inv_ids :			
					wf_service = netsvc.LocalService('workflow')
					wf_service.trg_validate(uid, 'account.invoice', invoice, 'invoice_open', cr)				
		return my_krs_id	    
	
	def _get_ips(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		res = {}
		
		krs_id = self.browse(cr,uid,ids[0],context=context)
		partner = krs_id.partner_id.id

		cr.execute("""SELECT okd.id
						FROM operasional_krs_detail okd
						LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
						WHERE ok.partner_id = %s
						AND ok.state <> 'draft'"""%(partner))
		dpt = cr.fetchall()

		det_id = map(lambda x: x[0], dpt)
		#import pdb;pdb.set_trace()
		det_sch = self.pool.get('operasional.krs_detail').browse(cr,uid,det_id,context=context)
		sks = 0
		sks_smt_ini = 0
		bobot_total = 0.00
		bobot_smt_ini = 0.00
		for det in det_sch:
			sks += det.sks
			if det.krs_id.id == ids[0]:
				sks_smt_ini += det.sks
				bobot_smt_ini += (det.nilai_angka*det.sks)
			bobot_total += (det.nilai_angka*det.sks)

		#import pdb;pdb.set_trace()	
		### ips = (total nilai angka*total sks) / total sks
		if sks == 0:
			ips = 0
		else :
			ips = round(bobot_total/sks,2)

		if sks_smt_ini == 0 :	
			ips_smt = 0
		else :
			ips_smt = round(bobot_smt_ini/sks_smt_ini,2)
		self.write(cr,uid,ids[0],{'sks_tot':sks,'ips_field':ips,'ips_field_persemester':ips_smt},context=context)	

		res[ids[0]] = ips
		return res
	
	_columns = {
		'kode' : fields.char('Kode', 128),
		'state':fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],'Status'),
		'partner_id' : fields.many2one('res.partner','Mahasiswa', domain="[('status_mahasiswa','=','Mahasiswa')]"),
		#'employee_id' : fields.many2one('hr.employee','Dosen Wali'),
		#'npm':fields.related('partner_id', 'npm', type='char', relation='res.partner',size=128, string='NPM',readonly=True),
		'npm' : fields.char('NPM',size=28,),
		'fakultas_id':fields.many2one('master.fakultas','Fakultas',required = True),         
		'konsentrasi_id':fields.many2one('master.konsentrasi',string='Konsentrasi',),           
		'prodi_id':fields.many2one('master.prodi',string='Program Studi',required = True),
		'max_smt': fields.integer("Max Semester",),
		'semester_id':fields.many2one('master.semester','Semester',domain="[('name','<=',max_smt)]",required = True),
		'tahun_ajaran_id': fields.many2one('academic.year','Tahun Akademik',required = True),
		'kelas_id':fields.many2one('master.kelas',string='Kelas'), 
		'krs_detail_ids' : fields.one2many('operasional.krs_detail','krs_id','Matakuliah',ondelete="cascade"),
		#'view_ipk_ids' : fields.one2many('operasional.view_ipk','krs_id','Mata Kuliah'),
		'kurikulum_id':fields.many2one('master.kurikulum','Kurikulum'),
		'ips':fields.function(_get_ips,type='float',string='Indeks Prestasi Kumulatif',),
		'ips_field':fields.float(string='Indeks Prestasi (field)',),
		'ips_field_persemester':fields.float(string='Indeks Prestasi Semester Ini',),
		'user_id':fields.many2one('res.users','User',readonly=True),
		'sks_tot' : fields.integer('Total SKS',readonly=True),
		'invoice_id' : fields.many2one('account.invoice','Invoice',domain=[('type', '=','out_invoice')],readonly=True),
		'is_tambahan' : fields.boolean('Kartu Studi Tambahan'),
		'reason' : fields.char('Alasan'),
	}    
				 
	_defaults={
		'state' : 'draft', 
		'kode': '/',
		'user_id': lambda obj, cr, uid, context: uid,
	}

	def confirm(self, cr, uid, ids, context=None):
		#import pdb;pdb.set_trace()
		form_id = self.browse(cr,uid,ids[0],context=context) 
		if not form_id.krs_detail_ids:
			raise osv.except_osv(_('Error!'), _('Matakuliah tidak boleh kosong !'))
		#cek dahulu pembayaran atas KRS ini, minimal ada 1 yg sudah d bayar lunas
		inv_obj = self.pool.get('account.invoice')
		inv_exist = inv_obj.search(cr,uid,[('krs_id','=',form_id.id)])
		if not inv_exist :		
			raise osv.except_osv(_('Error!'), _('Invoice atas KRS ini belum dibuat !'))	
		inv_krs = len(inv_exist)	
		not_paid = 0
		for paid in inv_exist:
			inv_state = inv_obj.browse(cr,uid,paid).state
			if inv_state != 'paid':
				not_paid += 1
		#cek mimimal harus ada 1 invoice yg harus dibayar
		if inv_krs == not_paid:
			raise osv.except_osv(_('Error!'), _('%s invoice atas KRS ini belum dibayar !')%(inv_krs))		
		for x in form_id.krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'confirm'},context=context)
		
	
		self.write(cr, uid, ids, {'state' : 'confirm'}, context=context)
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_universities_v8', 'krs_tree_view')
		view_id = view_ref and view_ref[1] or False,		
		return {
			'name' : _('Temporary View'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'operasional.krs',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			'domain' : "[('state','=','draft')]",
			#'context': "{'default_state':'open'}",#
			'nodestroy': False,
			}

	def cancel(self,cr,uid,ids,context=None):   

		for x in self.browse(cr,uid,ids[0],context=context).krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'draft'},context=context)
		self.write(cr, uid, ids, {'state' : 'draft'}, context=context)
		return True

	def done(self,cr,uid,ids,context=None): 
		#import pdb;pdb.set_trace()	  
		inv_obj = self.pool.get('account.invoice')
		my_obj = self.browse(cr,uid,ids[0],context=context)
		inv = inv_obj.search(cr,uid,[('krs_id','=',ids[0])])
		if not inv:
			raise osv.except_osv(_('Error!'), _('Data tidak bisa di "done" kan, karena tidak ada invoice untuk KHS ini!'))
		for id_inv in inv :
			state = inv_obj.browse(cr,uid,id_inv).state
			if state != 'paid':
				raise osv.except_osv(_('Error!'), _('Data tidak bisa di "done" kan, karena ada invoice yang belum lunas untuk KHS ini!'))	
		for x in my_obj.krs_detail_ids:
			self.pool.get('operasional.krs_detail').write(cr,uid,x.id,{'state':'done'},context=context)

		self.write(cr, uid, ids, {'state' : 'done'}, context=context)
		return True

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(operasional_krs, self).unlink(cr, uid, ids, context=context)


	# def onchange_partner(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, jurusan_id, prodi_id, kelas_id, partner_id, npm, context=None):
	def onchange_partner(self, cr, uid, ids, tahun_ajaran_id, fakultas_id, prodi_id, kelas_id, partner_id, npm, konsentrasi_id,context=None):

		results = {}
		if not partner_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [('id','=',partner_id)], context=context)

		par_id = par_obj.browse(cr,uid,par_ids,context=context)[0]
		npm =par_id.npm
		kelas_id = par_id.kelas_id.id
		tahun_ajaran_id = par_id.tahun_ajaran_id.id
		fakultas_id = par_id.fakultas_id.id
		konsentrasi_id = par_id.konsentrasi_id.id
		prodi_id = par_id.prodi_id.id
		max_smt = par_id.prodi_id.semester_id.name
		# max_smt = par_id.jurusan_id.semester_id.name

		results = {
			'value' : {
				'npm' : npm,
				'kelas_id': kelas_id,
				'tahun_ajaran_id' : tahun_ajaran_id,
				'fakultas_id' : fakultas_id,
				'konsentrasi_id' : konsentrasi_id,
				'prodi_id' : prodi_id,
				'max_smt': max_smt,
			}
		}
		return results 

	def onchange_semester(self, cr, uid, ids, npm, tahun_ajaran_id, prodi_id, semester_id, partner_id, konsentrasi_id,context=None):
	# def onchange_semester(self, cr, uid, ids, npm, tahun_ajaran_id, prodi_id, semester_id, partner_id, context=None):

		results = {}
		if not semester_id:
			return results
		
		kur_obj = self.pool.get('master.kurikulum')
		kur_det_obj = self.pool.get('master.kurikulum.detail')
		kur_ids = kur_obj.search(cr, uid, [
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('konsentrasi_id','=',konsentrasi_id),
			('prodi_id','=',prodi_id),
			('state','=','confirm'),
			('semester_id','=',semester_id)], context=context)
		if kur_ids == []:
			raise osv.except_osv(_('Error!'),
								_('Tidak ada kurikulum yang cocok untuk data ini!'))

		#cek partner dan semester yang sama
		krs_uniq = self.search(cr,uid,[('partner_id','=',partner_id),
										('semester_id','=',semester_id),
										#('is_tambahan','=',False),
										('state','in',('draft','confirm'))])
		if krs_uniq != []:
			raise osv.except_osv(_('Error!'),
								_('KRS untuk mahasiswa dengan semester ini sudah dibuat!'))			
		
		kur_id = kur_obj.browse(cr,uid,kur_ids,context=context)[0].mk_kurikulum_detail_ids
		kur_kode = kur_obj.browse(cr,uid,kur_ids,context=context)[0].id
		mk_kurikulums = []
		for kur in kur_id:
			mk_kurikulums.append([kur.matakuliah_id.id,kur.sks,kur.name])
	
		#cari matakuliah apa saja yg sdh di tempuh di smt sebelumnya
		cr.execute("""SELECT okd.id, okd.mata_kuliah_id
						FROM operasional_krs_detail okd
						LEFT JOIN operasional_krs ok ON ok.id = okd.krs_id
						WHERE ok.partner_id = %s
						AND ok.state <> 'draft'"""%(partner_id))
		dpt = cr.fetchall()
		
		total_mk_ids = map(lambda x: x[1], dpt)
		mk_kurikulum = map(lambda x: x[0], mk_kurikulums)
		#filter matakuliah yg benar-benar belum di tempuh
		mk_baru_ids =set(mk_kurikulum).difference(total_mk_ids)
		#import pdb;pdb.set_trace()
		res = []
		for kur in mk_kurikulums:
			if kur[0] in mk_baru_ids:
				res.append([0,0,{'mata_kuliah_id': kur[0],'sks':kur[1],'state':'draft'}])	
			results = {
				'value' : {
					'kurikulum_id': kur_kode,
					'krs_detail_ids' : res,
				}
			}
		return results 
			
operasional_krs()

class krs_detail (osv.Model):
	_name='operasional.krs_detail'
	_rec_name='krs_id'

	def name_get(self, cr, uid, ids, context=None):
		
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, [ 'mata_kuliah_id','sks','nilai_huruf_field'], context=context)
		res = []
		for record in reads:
			mata_kuliah_id 		= record['mata_kuliah_id']
			sks 				= record['sks']
			nilai_huruf_field 	= record['nilai_huruf_field']
			name 		= mata_kuliah_id[1]+' || '+str(sks)+' SKS || Nilai '+nilai_huruf_field
			res.append((record['id'], name))
		return res
	# def _get_nilai_akhir(self, cr, uid, ids, field_name, arg, context=None):
	# 	if context is None:
	# 		context = {}
	# 	#import pdb;pdb.set_trace()
	# 	nil_obj = self.pool.get('master.nilai')
	# 	absen_obj = self.pool.get('absensi')
	# 	presentase_absen 	= 0.1
	# 	presentase_tugas 	= 0.2
	# 	presentase_uts 		= 0.3
	# 	presentase_uas 		= 0.4
	# 	presentase_ulangan		= 0
	# 	presentase_presentasi 	= 0
	# 	presentase_quiz 		= 0
	# 	presentase_lainnya		= 0		
	# 	result = {}
	# 	for nil in self.browse(cr,uid,ids,context=context):
	# 		tahun_ajaran 	= nil.krs_id.tahun_ajaran_id.id
	# 		fakultas 		= nil.krs_id.fakultas_id.id
	# 		prodi 	 		= nil.krs_id.prodi_id.id
	# 		semester 		= nil.krs_id.semester_id.id
	# 		matakuliah 		= nil.mata_kuliah_id.id
	# 		kelas 			= nil.krs_id.kelas_id.id 
	# 		setting_dosen 	= absen_obj.search(cr,uid,[('tahun_ajaran_id','=',tahun_ajaran),
	# 													('fakultas_id','=',fakultas),
	# 													('prodi_id','=',prodi),
	# 													('semester_id','=',semester),
	# 													('mata_kuliah_id','=',matakuliah),
	# 													('kelas_id','=',kelas)])
	# 		if setting_dosen:
	# 			sett 	= absen_obj.browse(cr,uid,setting_dosen[0]) 
	# 			total_set = (sett.absensi + sett.tugas + sett.uts + sett.uas + sett.ulangan + sett.presentasi + sett.quiz + sett.lainnya)
	# 			if total_set == 100 :
	# 				presentase_absen 		= sett.absensi/100
	# 				presentase_tugas 		= sett.tugas/100
	# 				presentase_uts 			= sett.uts/100
	# 				presentase_uas 			= sett.uas/100			
	# 				presentase_ulangan		= sett.ulangan/100
	# 				presentase_presentasi 	= sett.presentasi/100
	# 				presentase_quiz 		= sett.quiz/100
	# 				presentase_lainnya		= sett.lainnya/100

	# 		absen 			= nil.absensi
	# 		tugas 			= nil.tugas
	# 		ulangan 		= nil.ulangan
	# 		uts 			= nil.uts
	# 		uas 			= nil.uas
	# 		presentasi 		= nil.presentasi
	# 		quiz 			= nil.quiz
	# 		lainnya 		= nil.lainnya			
	# 		tot 			= (absen*presentase_absen)+(tugas*presentase_tugas)+(uts*presentase_uts)+(uas*presentase_uas)+(presentasi*presentase_presentasi)+(ulangan*presentase_ulangan)+(quiz*presentase_quiz)+(lainnya*presentase_lainnya)
	# 		#tot = (tugas+ulangan+uts+uas)/4
	# 		#import pdb;pdb.set_trace()
	# 		nil_src = nil_obj.search(cr,uid,[('min','<=',tot),('max','>=',tot)],context=context)
	# 		if nil_src == []:
	# 			return result

	# 		nil_par = nil_obj.browse(cr,uid,nil_src,context=context)[0]
	# 		huruf = nil_par.name
	# 		angka = nil_par.bobot
			
	# 		result[nil.id] = huruf
	# 		if not nil.is_import :
	# 			wr = self.write(cr,uid,nil.id,{'nilai_angka':angka,'nilai_huruf_field':huruf})
	# 	return result


	def _get_nilai_akhir(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		#import pdb;pdb.set_trace()
		nil_obj = self.pool.get('master.nilai')
		penil_obj = self.pool.get('master.penilaian')
		absen_obj = self.pool.get('absensi')
		presentase_absen 	= 0.1
		presentase_tugas 	= 0.2
		presentase_uts 		= 0.3
		presentase_uas 		= 0.4
		presentase_ulangan		= 0
		presentase_presentasi 	= 0
		presentase_quiz 		= 0
		presentase_lainnya		= 0		
		result = {}
		for nil in self.browse(cr,uid,ids,context=context):	
			tahun_ajaran 	= nil.krs_id.tahun_ajaran_id.id
			setting_nilai 	= penil_obj.search(cr,uid,[('tahun_ajaran_id','=',tahun_ajaran)])
			if setting_nilai:
				sett 	= absen_obj.browse(cr,uid,setting_nilai[0]) 
				total_set = (sett.absensi + sett.tugas + sett.uts + sett.uas)
				if total_set == 100 :
					presentase_absen 		= sett.absensi/100
					presentase_tugas 		= sett.tugas/100
					presentase_uts 			= sett.uts/100
					presentase_uas 			= sett.uas/100			

			absen 			= nil.absensi
			tugas 			= nil.tugas
			uts 			= nil.uts
			uas 			= nil.uas
			tot 			= nil.uas
			if not nil.mata_kuliah_id.penilaian100persen :		
				tot 			= (absen*presentase_absen)+(tugas*presentase_tugas)+(uts*presentase_uts)+(uas*presentase_uas)
			#tot = (tugas+ulangan+uts+uas)/4
			#import pdb;pdb.set_trace()
			nil_src = nil_obj.search(cr,uid,[('min','<=',tot),('max','>=',tot)],context=context)
			if nil_src == []:
				return result

			nil_par = nil_obj.browse(cr,uid,nil_src,context=context)[0]
			huruf = nil_par.name
			angka = nil_par.bobot
			
			result[nil.id] = huruf
			if not nil.is_import :
				wr = self.write(cr,uid,nil.id,{'nilai_angka':angka,'nilai_huruf_field':huruf})
		return result
		
	_columns = {
		'krs_id'		:fields.many2one('operasional.krs','Kode KRS',),
		'mata_kuliah_id':fields.many2one('master.matakuliah','Matakuliah'),
		#'sks'			:fields.related('mata_kuliah_id', 'sks',type='integer',relation='master.matakuliah', string='SKS',store=True),
		'sks'			:fields.float('SKS'),
		'quiz' 		    :fields.float('Quiz'),
		'presentasi' 	:fields.float('Presentasi'),
		'absensi' 		:fields.float('absensi'),
		'lainnya'		:fields.float('Lainnya'),		
		'tugas' 		:fields.float('Tugas'),
		'ulangan' 		:fields.float('Ulangan'),
		'uts'			:fields.float('UTS Angka'),
		'uas'			:fields.float('UAS Angka'),
		'uts_huruf'		:fields.char('UTS'),
		'uas_huruf'		:fields.char('UAS'),
		'nilai_huruf'	:fields.function(_get_nilai_akhir,type='char',string='Nilai Akhir'),
		'nilai_angka'	:fields.float('Nilai Angka'),
		'nilai_huruf_field'	:fields.char('Nilai Huruf Field'),
		'transkrip_id'	:fields.many2one('operasional.transkrip','Transkrip'),
		'state'			:fields.selection([('draft','Draft'),('confirm','Confirm'),('done','Done')],'Status'),
		'is_konversi'	:fields.boolean('Konversi?'),
		'is_import' 	:fields.boolean('Import?'),
		'jadwal_id'		:fields.many2one('master.jadwal','Jadwal'),
			}

	_defaults={
		'state' : 'draft', 
		'is_import' : False,
	}
	 
krs_detail()

 
class operasional_transkrip(osv.Model):
	_name='operasional.transkrip'

	def create(self, cr, uid, vals, context=None):
		
		if 'partner_id' in vals:
			mhs = vals['partner_id']
			partner_brw = self.pool.get('res.partner').browse(cr,uid,mhs)
			# jurusan = partner_brw.jurusan_id.id
			# cek_mhs = self.search(cr,uid,[('partner_id','=',mhs),('jurusan_id','=',jurusan)])
			prodi = partner_brw.prodi_id.id
			cek_mhs = self.search(cr,uid,[('partner_id','=',mhs),('prodi_id','=',prodi)])
			if cek_mhs != []:
				raise osv.except_osv(_('Error!'),
				('Mahasiswa ini sudah mempunyai transkrip dengan program studi dan jenjang yang sama!'))				

		return super(operasional_transkrip, self).create(cr, uid, vals, context=context)	 

		#jika penggambilan MK di KRS berdasarkan yang terbaru
	def get_mk_by_newest(self, cr, uid, ids, context=None):

		mhs_id = self.browse(cr,uid,ids[0],context=context).partner_id.id
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk,s.name AS smt,s2.name AS smt_kurikulum
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_kurikulum mkk ON ok.kurikulum_id = mkk.id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						LEFT JOIN master_semester s2 ON s2.id = mkk.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(mhs_id) +"""
						GROUP BY okd.id,s.name,s2.name
						ORDER BY s2.name,s.name DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			return mk
		id_mk = map(lambda x: x[0], mk)	#id khs detail
		mk_ids = map(lambda x: x[1], mk) #Matakuliah khs detail

		return id_mk

		#jika penggambilan MK di KRS berdasarkan yang terbaik
	def get_mk_by_better(self, cr, uid, ids, context=None):

		mhs_id = self.browse(cr,uid,ids[0],context=context).partner_id.id
		
		ops_obj = self.pool.get('operasional.krs')
		det_obj = self.pool.get('operasional.krs_detail')
	
		cr.execute("""SELECT okd.id AS id, okd.mata_kuliah_id AS mk,okd.nilai_angka AS nilai,s2.name AS smt_kurikulum
						FROM operasional_krs ok
						LEFT JOIN operasional_krs_detail okd ON ok.id = okd.krs_id
						LEFT JOIN master_kurikulum mkk ON ok.kurikulum_id = mkk.id
						LEFT JOIN master_semester s ON s.id = ok.semester_id
						LEFT JOIN master_semester s2 ON s2.id = mkk.semester_id
						WHERE ok.state = 'done' AND ok.partner_id ="""+ str(mhs_id) +"""
						GROUP BY okd.id,s.name,s2.name
						ORDER BY s2.name, okd.nilai_angka DESC""")		   
		mk = cr.fetchall()			

		if mk == []:
			return mk
		id_mk = map(lambda x: x[0], mk)	#id khsdetail
		mk_ids = map(lambda x: x[1], mk) #Matakuliah khsdetail

		return id_mk

	def get_total_khs(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}
		
		for my in self.browse(cr,uid,ids):
			if my.partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaru' :
				mk = self.get_mk_by_newest(cr, uid, ids, context=None)
			elif my.partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaik' :
				mk = self.get_mk_by_better(cr, uid, ids, context=None)

			if mk == []:
				return result
			result[ids[0]] = mk

			tran_resume_obj 	= self.pool.get('operasional.transkrip.resume')		
			nilai_obj		 	= self.pool.get('master.nilai')
			sql 				= "select id,name from master_nilai order by id asc"
			cr.execute(sql)
			hasil = cr.fetchall()
			if hasil:
				#jika sdh ada resume hapus dulu
				resume_exist = tran_resume_obj.search(cr,uid,[('transkrip_id','=',my.id)])	
				if resume_exist :
					tran_resume_obj.unlink(cr,uid,resume_exist,context=context)	
					cr.commit()			
				resume_ids = []
				for rsm in hasil:
					#import pdb;pdb.set_trace()
					nil = nilai_obj.browse(cr,uid,rsm[0])
					cr.execute("""SELECT count(okd.id),sum(okd.sks)
									FROM operasional_krs_detail okd
									LEFT JOIN master_nilai mn ON mn.name=okd.nilai_huruf_field
									WHERE okd.id in %s
									AND mn.id = %s """%(tuple(mk),str(rsm[0])))
					dpt = cr.fetchall()
					if dpt :
						if dpt[0][0] != 0:

							resume_ids.append((0,0,{'nilai_id'	:nil.id,
													'nilai'		:nil.name,
													'jumlah'	:dpt[0][0],
													'jumlah_sks':dpt[0][1]}))
				
				self.write(cr,uid,ids[0],{'transkrip_resume_ids':resume_ids})
				cr.commit()
		return result

	def _get_ipk(self, cr, uid, ids, field_name, arg, context=None):
		if context is None:
			context = {}
		result = {}

		if self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaru' :
			mk = self.get_mk_by_newest(cr, uid, ids, context=None)
		elif self.browse(cr,uid,ids[0]).partner_id.tahun_ajaran_id.mekanisme_nilai == 'terbaik' :
			mk = self.get_mk_by_better(cr, uid, ids, context=None)

		if mk == []:
			raise osv.except_osv(_('Error!'),
				('Untuk menggunakan fitur ini minimal harus selesai 1 semester!'))				
			return result

		det_obj = self.pool.get('operasional.krs_detail')			
		tot_nil = 0.0
		tot_sks = 0.0
		ipk_import = 0.0
		for m in mk:
			det_id = det_obj.browse(cr,uid,m,context=context)
			sks = det_id.sks
			nil = det_id.nilai_angka
			nil_jml = nil*sks

			tot_sks += sks
			tot_nil += nil_jml

			if det_id.is_import and det_id.krs_id.ips_field > 0:
				tot_nil = det_id.krs_id.ips_field
				tot_sks = 1
				break

		ipk = tot_nil/tot_sks
		result[ids[0]] = ipk

		#update nilai IPK di di objek mahasiswa bersangkutan
		nama_mahasiswa = self.browse(cr,uid,ids[0]).partner_id.id
		partner_obj = self.pool.get('res.partner')
		partner_obj.write(cr,uid,nama_mahasiswa,{'ipk':ipk},context=context)

		#get yudisium
		yud_obj = self.pool.get('master.yudisium')
		yud_src = yud_obj.search(cr,uid,[('min','<=',ipk),('max','>=',ipk)],context=context)
		if yud_src != [] :
			yud = yud_src[0]
			yudisium = yud_obj.browse(cr,uid,yud,context=context).id
			self.write(cr,uid,ids[0],{'yudisium_id':yudisium},context=context)
		self.write(cr,uid,ids[0],{'t_sks':tot_sks,'t_nilai':tot_nil},context=context)

		return result

	def _get_resume_nilai(self, cr, uid, context=None):
		resume_ids = []
		nilai_obj = self.pool.get('master.nilai')
		sql = "select id,name from master_nilai order by id asc"
		cr.execute(sql)
		hasil = cr.fetchall()
		if hasil:
			for x in hasil:
				nil = nilai_obj.browse(cr,uid,x[0])
				resume_ids.append((0,0,{'nilai_id':nil.id,'nilai':nil.name}))
		return resume_ids

	_columns={
		'name' : fields.char('Kode',size=28,required=True),
		'partner_id' : fields.many2one('res.partner','Nama Mahasiswa', required=True, domain="[('status_mahasiswa','in',('Mahasiswa','alumni'))]"),
		'npm':fields.related('partner_id','npm',type='char',relation='res.partner',string='NIM'),
		'tempat_lahir':fields.related('partner_id','tempat_lahir',type='char',relation='res.partner',string='Tempat Lahir',readonly=True),
		'tanggal_lahir':fields.related('partner_id','tanggal_lahir',type='date',relation='res.partner',string='Tanggal Lahir',readonly=True),
		'tahun_ajaran_id':fields.related('partner_id', 'tahun_ajaran_id', type='many2one', relation='academic.year',string='Angkatan',readonly=True),
		'fakultas_id':fields.related('partner_id', 'fakultas_id', type='many2one',relation='master.fakultas', string='Fakultas',readonly=True),
		'jurusan_id':fields.related('partner_id', 'jurusan_id', type='many2one',relation='master.jurusan', string='Jurusan',readonly=True),
		'prodi_id':fields.related('partner_id', 'prodi_id', type='many2one',relation='master.prodi', string='Program Studi',readonly=True),
		'konsentrasi_id':fields.related('partner_id', 'konsentrasi_id', type='many2one',relation='master.konsentrasi', string='Konsentrasi',readonly=True),
		'transkrip_detail_ids' : fields.function(get_total_khs, type='many2many', relation="operasional.krs_detail", string="Total Mata Kuliah"), 
		'ipk' : fields.function(_get_ipk,type='float',string='IPK',help="SKS = Total ( SKS * bobot nilai ) / Total SKS"),
		'yudisium_id' : fields.many2one('master.yudisium','Yudisium',readonly=True),
		't_sks' : fields.integer('Total SKS'),
		't_nilai' : fields.char('Total Nilai'),
		'transkrip_resume_ids' : fields.one2many('operasional.transkrip.resume','transkrip_id','Resume',readonly=True, ondelete='cascade',store=True),
			}    

	_sql_constraints = [('name_uniq', 'unique(name)','Kode Transkrip tidak boleh sama')]

	_defaults = {
		#'transkrip_resume_ids' : _get_resume_nilai,
	}

operasional_transkrip()


class operasional_transkrip_resume(osv.osv):
	_name = "operasional.transkrip.resume"
	_rec_name = "nilai"
	_columns = {
		'transkrip_id' 	: fields.many2one('operasional.transkrip','transkrip_id'),
		'nilai_id'		: fields.many2one('master.nilai','Nilai ID'),
		'nilai'			: fields.char('Nilai'),
		'jumlah'		: fields.integer('Jumlah Nilai'),
		'jumlah_sks'	: fields.integer('Jumlah SKS'),
	}