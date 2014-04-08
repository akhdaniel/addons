from openerp.osv import fields, osv
import datetime

class report_recruit(osv.osv_memory):
	_name = "hr_report.recruitment"

	_columns = {
		'report' : fields.selection((('data_seleksi','Data Seleksi Pelamar'),
			('laporan_pemenuhan','Laporan Pemenuhan Recruitment'),
			('list_pemenuhan_harian','List Pemenuhan Harian'),
			('list_pemenuhan_bulanan','List Pemenuhan Bulanan'),
			('sumary_kebutuhan_harian','Sumary Kebutuhan Harian'),
			('sumary_kebutuhan_bulanan','Sumary Kebutuhan Bulanan'),
			('sumary_sasaranmutu','Sumary Monitoring Sasaran Mutu'),
			('detail_sasaranmutu','Detail Monitoring Sasaran Mutu'),
			('permintaan_recruitment','Laporan Permintaan Recruitment'),
			('detail_monitoring_progres','Detail Monitoring Progres Interview'),
			('sumary_monitoring_progres','Sumary Monitoring Progres Interview')), 'Report',required=True),
		'year_id' : fields.many2one('report.tahun','Tahun'),
		'department' : fields.many2one('hr.department','Department'),
		'star_date' : fields.date('Mulai Dari'),
		'end_date' : fields.date('Sampai'),
	}

	def cleanup(self,cr,uid,ids,context={}):
		idea_obj = self.pool.get('idea.idea')
		for wiz in self.browse(cr,uid,ids):
			if wiz.idea_age <= 3:
				raise osv.except_osv('UserError','Please select a larger age')
			limit = datetime.date.today()-datetime.timedelta(days=wiz.idea_age)
			ids_to_del = idea_obj.search(cr,uid, [('create_date', '<' ,
					limit.strftime('%Y-%m-%d 00:00:00'))],context=context)
			idea_obj.unlink(cr,uid,ids_to_del)
		return {}

	def eksport_report(self, cr, uid, ids, context=None):
		data = []
		val = self.browse(cr,uid,ids)[0]
		rpt = val.report
		year = val.year_id.name
		if rpt == 'data_seleksi' :
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
			obj_pemenuhan = self.pool.get('hr_pemenuhan')
			src = obj_pemenuhan.search(cr,uid,[('department','=',dept),('tgl_permintaan','>=',star),('tgl_permintaan','<=',end)])
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
				'report_name': 'pemenuhan.recruitment',
				'nodestroy': True,
				'datas': datas,
				}
			
report_recruit()

class year(osv.osv_memory):
	_name = "report.tahun"

	_columns = {
		'name' : fields.integer('Tahun'),
	}
year()	
