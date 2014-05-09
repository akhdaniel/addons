from openerp.osv import fields, osv
import datetime

class report_recruit(osv.osv):
	_name = "hr_report.recruitment"

	_columns = {
		'report' : fields.selection((('data_seleksi','Data Seleksi Pelamar'),
			('laporan_pemenuhan','Laporan Pemenuhan Recruitment'),
			('list_pemenuhan_harian','List Pemenuhan Harian'),
			('list_pemenuhan_bulanan','List Pemenuhan Bulanan'),
			('sumary_kebutuhan_harian','Sumary Kebutuhan Harian'),
			('sumary_kebutuhan_bulanan','Sumary Kebutuhan Bulanan'),
			('permintaan_recruitment','Laporan Permintaan Recruitment'),
			('detail_monitoring_progres','Detail Monitoring Progres Interview'),
			('sumary_monitoring_progres','Sumary Monitoring Progres Interview'),
			('daftar_pelamar','Daftar Pelamar')), 'Report',required=True),
		'year_id' : fields.many2one('report.tahun','Tahun'),
		'department' : fields.many2one('hr.department','Department'),
		'divisi' : fields.many2one('hr.divisi','Divisi'),
		'star_date' : fields.date('Mulai Dari'),
		'end_date' : fields.date('Sampai'),
		'status' : fields.selection((('not_yet','Not Yet'),
			('in_progres','In Progres'),
			('done','done'),
			('pending','Pending'),
			('all','ALL')), 'Status'),
	}
	_defaults = {
		'report' :'data_seleksi',
		'year_id' :20,
		'department' : 1, 
		'divisi' : 1,
		'star_date' : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
		'end_date' : lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
		'status' : 'done'
	}


	def eksport_report(self, cr, uid, ids, context=None):
		data = []
		val = self.browse(cr,uid,ids)[0]
		rpt = val.report		
		if rpt == 'data_seleksi' :
			year = val.year_id.name
			#ambil semua data yang berkaitan dengan data seleksi pelamar
			obj_seleksi = self.pool.get('hr.seleksi_pelamar')
			src = obj_seleksi.search(cr,uid,[('tahun','=',year)])
			brw_data = obj_seleksi.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.nama, rpts.tgl_seleksi, rpts.tgl_seleksi1, rpts.pendidikan, rpts.jurusan, rpts.tgl_lahir,
							 rpts.usia, rpts.sumber, rpts.ref, rpts.kehadiran, rpts.department, rpts.bagian, rpts.jabatan,
							 rpts.ref_jab, rpts.status, rpts.status1, rpts.keputusan, rpts.tgl_keputusan])

			if context is None:
				context = {}
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
                'report_name': 'seleksi.pelamar',
                'nodestroy': True,
                'datas': datas,
                }

		if rpt == 'laporan_pemenuhan' :
			dept = val.department.name
			star = val.star_date
			end = val.end_date
			status = val.status
			obj_pemenuhan = self.pool.get('hr_pemenuhan')
			if dept == "All" :
				if status == 'all' :
					src = obj_pemenuhan.search(cr,uid,[('tgl_permintaan','>=',star),('tgl_permintaan','<=',end)])
				else :
					src = obj_pemenuhan.search(cr,uid,[('tgl_permintaan','>=',star),('tgl_permintaan','<=',end),('status','=',status)])
			else :
				if status == 'all' :
					src = obj_pemenuhan.search(cr,uid,[('department','=',dept),('tgl_permintaan','>=',star),('tgl_permintaan','<=',end)])
				else :
					src = obj_pemenuhan.search(cr,uid,[('department','=',dept),('tgl_permintaan','>=',star),('tgl_permintaan','<=',end),('status','=',status)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.no_pmintaan, rpts.tgl_permintaan, rpts.department, rpts.jabatan, rpts.jml_prmintaan,rpts.aktifitas,
					rpts.tgl_seleksi, rpts.jml_kandidat, rpts.jml_diterima, rpts.per_masuk, rpts.status, rpts.ket])
	
			if context is None:
				context = {}
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.recruitmen',
				'nodestroy': True,
				'datas': datas,
				}
			
		if rpt == 'list_pemenuhan_harian' :
			div = val.divisi.name
			star = val.star_date
			end = val.end_date
			obj_pemenuhan = self.pool.get('hr.pemenuhan_kebutuhan')
			if div == "All" :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Harian'),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Harian'),('div','=',div),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.bul_har, rpts.div, rpts.dept, rpts.bagian, rpts.jabatan,rpts.level,
					rpts.tgl_permohonan, rpts.status_wawancara, rpts.status_pemenuhan, rpts.jumlah_kebutuhan, rpts.jumlah_terpenuhi,
					rpts.kekurangan_pmenuhan, rpts.status_penempatan, rpts.ket, rpts.review])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'list_pemenuhan_bulanan' :
			div = val.divisi.name
			star = val.star_date
			end = val.end_date
			obj_pemenuhan = self.pool.get('hr.pemenuhan_kebutuhan')
			if div == "All" :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Bulanan'),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Bulanan'),('div','=',div),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.bul_har, rpts.div, rpts.dept, rpts.bagian, rpts.jabatan,rpts.level,
					rpts.tgl_permohonan, rpts.status_wawancara, rpts.status_pemenuhan, rpts.jumlah_kebutuhan, rpts.jumlah_terpenuhi,
					rpts.kekurangan_pmenuhan, rpts.status_penempatan, rpts.ket, rpts.review])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_kebutuhan_harian' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_kebutuhan_harian')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.tahun, rpts.dep, rpts.jum_kebutuhan, rpts.jum_terpenuhi, rpts.ket])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_kebutuhan_bulanan' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_kebutuhan')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.tahun, rpts.dep, rpts.jum_kebutuhan, rpts.jum_terpenuhi, rpts.ket])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'permintaan_recruitment' :
			dep = val.department.name
			year = int(val.year_id.name)
			obj_pemenuhan = self.pool.get('hr.lap_permintaan_karyawan')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			no = 0
			for rpts in brw_data :
				no = no + 1
				data.append([ no, rpts.dep, rpts.posisi, rpts.jumlah, rpts.wkt_penempatan, rpts.pengalaman, rpts.usia, rpts.jenis_kelamin,
					rpts.status, rpts.domisili,])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'laporan.permintaan.recruitment',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'detail_monitoring_progres' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.monitoring_recruitment')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([ rpts.tahun, rpts.name, rpts.dep, rpts.test1_hrd, rpts.test2_hrd, rpts.test1_usr, rpts.test2_usr,
				 rpts.approval, rpts.tes_kesehatan, rpts.ket, rpts.status])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'detail.monitoring.progres',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_monitoring_progres' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_monitoring')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([ rpts.tahun, rpts.dep, rpts.qty, rpts.test1, rpts.wawancara_hrd, rpts.wawancara1_usr, rpts.wawancara2_usr,
				 rpts.approval, rpts.tes_kesehatan, rpts.pending])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.monitoring.progres.recruitment',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'daftar_pelamar' :
			obj_pelamar = self.pool.get('hr.applicant')
			src = obj_pelamar.search(cr,uid,[('stage_id.sequence','<',100)])
			brw_data = obj_pelamar.browse(cr,uid,src)
			no = 0
			for rpts in brw_data :
				no = no + 1
				data.append([no, rpts.partner_name, rpts.name, rpts.job_id.name, rpts.kelamin, rpts.age, rpts.status,
				rpts.type_id.name, rpts.jurusan_id.name, rpts.pt_id.name, rpts.pengalaman, rpts.kab_id.name, rpts.partner_phone, rpts.email_from])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'daftar.pelamar',
				'nodestroy': True,
				'datas': datas,
				}

	# fungsi for print for pdf
	def eksport_report_pdf(self, cr, uid, ids, context=None):
		data = []
		val = self.browse(cr,uid,ids)[0]
		rpt = val.report		
		if rpt == 'data_seleksi' :
			year = val.year_id.name
			#ambil semua data yang berkaitan dengan data seleksi pelamar
			obj_seleksi = self.pool.get('hr.seleksi_pelamar')
			src = obj_seleksi.search(cr,uid,[('tahun','=',year)])
			brw_data = obj_seleksi.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.nama, rpts.tgl_seleksi, rpts.tgl_seleksi1, rpts.pendidikan, rpts.jurusan, rpts.tgl_lahir,
							 rpts.usia, rpts.sumber, rpts.ref, rpts.kehadiran, rpts.department, rpts.bagian, rpts.jabatan,
							 rpts.ref_jab, rpts.status, rpts.status1, rpts.keputusan, rpts.tgl_keputusan])

			if context is None:
				context = {}
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
                'report_name': 'seleksi.pelamar',
                'nodestroy': True,
                'datas': datas,
                }

		if rpt == 'laporan_pemenuhan' :
			dept = val.department.name
			star = val.star_date
			end = val.end_date
			status = val.status
			obj_pemenuhan = self.pool.get('hr_pemenuhan')
			if dept == "All" :
				if status == 'all' :
					src = obj_pemenuhan.search(cr,uid,[('tgl_permintaan','>=',star),('tgl_permintaan','<=',end)])
				else :
					src = obj_pemenuhan.search(cr,uid,[('tgl_permintaan','>=',star),('tgl_permintaan','<=',end),('status','=',status)])
			else :
				if status == 'all' :
					src = obj_pemenuhan.search(cr,uid,[('department','=',dept),('tgl_permintaan','>=',star),('tgl_permintaan','<=',end)])
				else :
					src = obj_pemenuhan.search(cr,uid,[('department','=',dept),('tgl_permintaan','>=',star),('tgl_permintaan','<=',end),('status','=',status)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.no_pmintaan, rpts.tgl_permintaan, rpts.department, rpts.jabatan, rpts.jml_prmintaan,rpts.aktifitas,
					rpts.tgl_seleksi, rpts.jml_kandidat, rpts.jml_diterima, rpts.per_masuk, rpts.status, rpts.ket])
	
			if context is None:
				context = {}
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.recruitmen',
				'nodestroy': True,
				'datas': datas,
				}
			
		if rpt == 'list_pemenuhan_harian' :
			div = val.divisi.name
			star = val.star_date
			end = val.end_date
			obj_pemenuhan = self.pool.get('hr.pemenuhan_kebutuhan')
			if div == "All" :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Harian'),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Harian'),('div','=',div),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.bul_har, rpts.div, rpts.dept, rpts.bagian, rpts.jabatan,rpts.level,
					rpts.tgl_permohonan, rpts.status_wawancara, rpts.status_pemenuhan, rpts.jumlah_kebutuhan, rpts.jumlah_terpenuhi,
					rpts.kekurangan_pmenuhan, rpts.status_penempatan, rpts.ket, rpts.review])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'list_pemenuhan_bulanan' :
			div = val.divisi.name
			star = val.star_date
			end = val.end_date
			obj_pemenuhan = self.pool.get('hr.pemenuhan_kebutuhan')
			if div == "All" :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Bulanan'),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('bul_har','=','Bulanan'),('div','=',div),('tgl_permohonan','>=',star),('tgl_permohonan','<=',end)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.bul_har, rpts.div, rpts.dept, rpts.bagian, rpts.jabatan,rpts.level,
					rpts.tgl_permohonan, rpts.status_wawancara, rpts.status_pemenuhan, rpts.jumlah_kebutuhan, rpts.jumlah_terpenuhi,
					rpts.kekurangan_pmenuhan, rpts.status_penempatan, rpts.ket, rpts.review])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'pemenuhan.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_kebutuhan_harian' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_kebutuhan_harian')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.tahun, rpts.dep, rpts.jum_kebutuhan, rpts.jum_terpenuhi, rpts.ket])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_kebutuhan_bulanan' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_kebutuhan')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([rpts.tahun, rpts.dep, rpts.jum_kebutuhan, rpts.jum_terpenuhi, rpts.ket])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.kebutuhan.harian',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'permintaan_recruitment' :
			dep = val.department.name
			year = int(val.year_id.name)
			obj_pemenuhan = self.pool.get('hr.lap_permintaan_karyawan')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			no = 0
			for rpts in brw_data :
				no = no + 1
				data.append([ no, rpts.dep, rpts.posisi, rpts.jumlah, rpts.wkt_penempatan, rpts.pengalaman, rpts.usia, rpts.jenis_kelamin,
					rpts.status, rpts.domisili,])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'laporan.permintaan.recruitment',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'detail_monitoring_progres' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.monitoring_recruitment')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([ rpts.tahun, rpts.name, rpts.dep, rpts.test1_hrd, rpts.test2_hrd, rpts.test1_usr, rpts.test2_usr,
				 rpts.approval, rpts.tes_kesehatan, rpts.ket, rpts.status])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'detail.monitoring.progres',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'sumary_monitoring_progres' :
			dep = val.department.name
			year = val.year_id.name
			obj_pemenuhan = self.pool.get('hr.sumary_monitoring')
			if dep == "All" :
				src = obj_pemenuhan.search(cr,uid,[('tahun','=',year)])
			else :
				src = obj_pemenuhan.search(cr,uid,[('dep','=',dep),('tahun','=',year)])
			brw_data = obj_pemenuhan.browse(cr,uid,src)
			for rpts in brw_data :
				data.append([ rpts.tahun, rpts.dep, rpts.qty, rpts.test1, rpts.wawancara_hrd, rpts.wawancara1_usr, rpts.wawancara2_usr,
				 rpts.approval, rpts.tes_kesehatan, rpts.pending])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'sumary.monitoring.progres.recruitment',
				'nodestroy': True,
				'datas': datas,
				}

		if rpt == 'daftar_pelamar' :
			obj_pelamar = self.pool.get('hr.applicant')
			src = obj_pelamar.search(cr,uid,[('stage_id.sequence','<',100)])
			brw_data = obj_pelamar.browse(cr,uid,src)
			no = 0
			for rpts in brw_data :
				no = no + 1
				data.append([no, rpts.partner_name, rpts.name, rpts.job_id.name, rpts.kelamin, rpts.age, rpts.status,
				rpts.type_id.name, rpts.jurusan_id.name, rpts.pt_id.name, rpts.pengalaman, rpts.kab_id.name, rpts.partner_phone, rpts.email_from])
	
			if context is None:
				context = {}
		
			#persiapan parameter untuk excel report
			nilai = self.read(cr,uid,ids)[0]
			datas = {'ids':[nilai['id']]}
			datas['model'] = 'hr_report.recruitment'
			datas['form'] = nilai
			datas['csv'] = data
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'daftar.pelamar',
				'nodestroy': True,
				'datas': datas,
				}
report_recruit()

class year(osv.osv_memory):
	_name = "report.tahun"

	_columns = {
		'name' : fields.char('Tahun'),
		'id' : fields.integer('id', readonly=True),
	}
year()	
