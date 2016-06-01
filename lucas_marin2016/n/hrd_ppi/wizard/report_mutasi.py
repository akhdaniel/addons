import re
import time
import xlwt
from report import report_sxw
from report_engine_xls import report_xls

class ReportStatus(report_sxw.rml_parse):
	def __init__(self, cr, uid, name, context=None):
		super(ReportStatus, self).__init__(cr, uid, name, context=context)
		self.localcontext.update({
		    'time': time,           
		})


class seleksi_pelamar(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Laporan Seleksi Pelamar'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
	 
		cols_specs = [
		              ('Nama', 1, 70, 'text', lambda x, d, p: x[0]),
		              ('Tgl Selek Hrd', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Tgl Selek Usr', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Pendidikan', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jurusan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Tgl Lahir', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Usia', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Sumber', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Ref', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('Kehadiran', 1, 70, 'text', lambda x, d, p: x[9]),
		              ('Bagian', 1, 70, 'text', lambda x, d, p: x[11]),
		              ('Jabatan', 1, 70, 'text', lambda x, d, p: x[12]),
		              ('ref Jabatan', 1, 70, 'text', lambda x, d, p: x[13]),
		              ('Status Hrd', 1, 70, 'text', lambda x, d, p: x[14]),
		              ('Status User', 1, 70, 'text', lambda x, d, p: x[15]),
		              ('Keputusan', 1, 70, 'text', lambda x, d, p: x[16]),
		              ('Tgl Keputusan', 1, 70, 'text', lambda x, d, p: x[17]),
		              
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['Nama', 'Tgl Selek Hrd', 'Tgl Selek Usr', 'Pendidikan', 'Jurusan', 'Tgl Lahir',
								 'Usia', 'Sumber', 'Ref', 'Kehadiran', 'Department', 'Bagian', 'Jabatan',
								 'ref Jabatan', 'Status Hrd', 'Status User', 'Keputusan', 'Tgl Keputusan'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])
		    ws.write(row_count, 14, x[14])
		    ws.write(row_count, 15, x[15])
		    ws.write(row_count, 16, x[16])
		    ws.write(row_count, 17, x[17])

		    row_count += 1
		     
		pass

seleksi_pelamar('report.seleksi.pelamar', 'hr.seleksi_pelamar', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class pemenuhan_recruitmen(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Laporan Pemenuhan Recruitment'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30 , 'text', lambda x, d, p: x[0]),
		              ('No Permintaan', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Tanggal Permintaan', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jabatan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Jumlah Permintaan', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Aktifitas', 1, 100, 'text', lambda x, d, p: x[6]),
		              ('Tanggal Seleksi', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Jumlah Kandidat',1, 70, 'text', lambda x, d, p: x[8]),
		              ('Jumlah Diterima', 1, 70, 'text', lambda x, d, p: x[9]),
		              ('Permohonan Masuk', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[11]),
		              ('Keterangan',  1, 70, 'text', lambda x, d, p: x[12]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','No Permintaan','Tanggal Permintaan','Department','Jabatan',
        'Jumlah Permintaan','Aktifitas','Tanggal Seleksi','Jumlah Kandidat','Jumlah Diterima','Permohonan Masuk','Status','Keterangan'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])

		    row_count += 1
		     
		pass

pemenuhan_recruitmen('report.pemenuhan.recruitmen', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class pemenuhan_kebutuhan_harian(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Pemenuhan Kebutuhan Harian'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('NO', 1, 30, 'text', lambda x, d, p: x[0]),
		              ('BULANAN/HARIAN', 1, 100, 'text', lambda x, d, p: x[1]),
		              ('DIVISI', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('DEPARTEMEN', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('BAGIAN', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('JABATAN', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('LEVEL', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('TANGGAL PERMOHONAN', 1, 100, 'text', lambda x, d, p: x[7]),
		              ('STATUS WAWANCARA',1, 100, 'text', lambda x, d, p: x[8]),
		              ('STATUS PEMENUHAN', 1, 100, 'text', lambda x, d, p: x[9]),
		              ('JUMLAH KEBUTUHAN', 1, 100, 'text', lambda x, d, p: x[10]),
		              ('JUMLAH TERPENUHI', 1, 100, 'text', lambda x, d, p: x[11]),
		              ('KEKURANGAN KEBUTUHAN',  1, 100, 'text', lambda x, d, p: x[12]),
		              ('KETERANGAN',  1, 70, 'text', lambda x, d, p: x[13]),
		              ('REVIEW',  1, 70, 'text', lambda x, d, p: x[14]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['NO','BULANAN/HARIAN','DIVISI','DEPARTEMEN','BAGIAN','JABATAN','LEVEL',
		'TANGGAL PERMHONAN','STATUS WAWANCARA','STATUS PEMENUHAN','JUMLAH KEBUTUHAN','JUMLAH TERPENUHI',
		'KEKURANGAN KEBUTUHAN','KETERANGAN','REVIEW'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])
		    ws.write(row_count, 14, x[14])

		    row_count += 1
		     
		pass

pemenuhan_kebutuhan_harian('report.pemenuhan.kebutuhan.harian', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class pemenuhan_kebutuhan_bulanan(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Pemenuhan Kebutuhan Bulanan'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('NO', 1, 30, 'text', lambda x, d, p: x[0]),
		              ('BULANAN/HARIAN', 1, 100, 'text', lambda x, d, p: x[1]),
		              ('DIVISI', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('DEPARTEMEN', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('BAGIAN', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('JABATAN', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('LEVEL', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('TANGGAL PERMOHONAN', 1, 100, 'text', lambda x, d, p: x[7]),
		              ('STATUS WAWANCARA',1, 100, 'text', lambda x, d, p: x[8]),
		              ('STATUS PEMENUHAN', 1, 100, 'text', lambda x, d, p: x[9]),
		              ('JUMLAH KEBUTUHAN', 1, 100, 'text', lambda x, d, p: x[10]),
		              ('JUMLAH TERPENUHI', 1, 100, 'text', lambda x, d, p: x[11]),
		              ('KEKURANGAN KEBUTUHAN',  1, 100, 'text', lambda x, d, p: x[12]),
		              ('KETERANGAN',  1, 70, 'text', lambda x, d, p: x[13]),
		              ('REVIEW',  1, 70, 'text', lambda x, d, p: x[14]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['NO','BULANAN/HARIAN','DIVISI','DEPARTEMEN','BAGIAN','JABATAN','LEVEL',
		'TANGGAL PERMHONAN','STATUS WAWANCARA','STATUS PEMENUHAN','JUMLAH KEBUTUHAN','JUMLAH TERPENUHI',
		'KEKURANGAN KEBUTUHAN','KETERANGAN','REVIEW'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])
		    ws.write(row_count, 14, x[14])

		    row_count += 1
		     
		pass

pemenuhan_kebutuhan_bulanan('report.pemenuhan.kebutuhan.bulanan', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class sumary_kebutuhan_harian(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Pemenuhan Kebutuhan Harian'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
		              ('No', 1, 30, 'text', lambda x, d, p: x[0]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Jumlah Kebutuhan', 1, 100, 'text', lambda x, d, p: x[2]),
		              ('Jumlah Terpenuhi', 1, 100, 'text', lambda x, d, p: x[3]),
		              ('Varian', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Percentage', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Keterangan', 1, 70, 'text', lambda x, d, p: x[6]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Department','Jumlah Kebutuhan','Jumlah Terpenuhi','Varian','Percentage','Keterangan'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])

		    row_count += 1
		     
		pass

sumary_kebutuhan_harian('report.sumary.kebutuhan.harian', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class sumary_kebutuhan_bulanan(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Pemenuhan Kebutuhan Bulanan'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
		              ('No', 1, 30, 'text', lambda x, d, p: x[0]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Jumlah Kebutuhan', 1, 100, 'text', lambda x, d, p: x[2]),
		              ('Jumlah Terpenuhi', 1, 100, 'text', lambda x, d, p: x[3]),
		              ('Varian', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Percentage', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Keterangan', 1, 70, 'text', lambda x, d, p: x[6]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Department','Jumlah Kebutuhan','Jumlah Terpenuhi','Varian','Percentage','Keterangan'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])

		    row_count += 1
		     
		pass

sumary_kebutuhan_bulanan('report.sumary.kebutuhan.bulanan', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class laporan_permintaan_recruitment(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Laporan Permintaan Recruitment'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
		              ('No', 1, 30, 'text', lambda x, d, p: x[0]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Posisi', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Jumlah', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('wkt Penempatan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Pengalaman', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Usia', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Jenis Kelamin', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('Domisili', 1, 70, 'text', lambda x, d, p: x[9]),
		              
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Department','Posisi','Jumlah','wkt Penempatan',
						'Pengalaman', 'Usia', 'Jenis Kelamin', 'Status', 'Domisili'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])

		    row_count += 1
		     
		pass

laporan_permintaan_recruitment('report.laporan.permintaan.recruitment', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class detail_monitoring_progres(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Detail Monitoring Progres'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30, 'text', lambda x, d, p: x[0]),	
		              ('Nama', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Test Tertlis HRD', 1, 100, 'text', lambda x, d, p: x[3]),
		              ('Test Wawancara HRD', 1, 100, 'text', lambda x, d, p: x[4]),
		              ('Test Wawancara USR 1', 1, 100, 'text', lambda x, d, p: x[5]),
		              ('Test Wawancara USR 2', 1, 100, 'text', lambda x, d, p: x[6]),
		              ('Management Approval', 1, 100, 'text', lambda x, d, p: x[7]),
		              ('Test Kesehatan', 1, 100, 'text', lambda x, d, p: x[8]),
		              ('Keterangan', 1, 100, 'text', lambda x, d, p: x[9]),
		              ('Status', 1, 100, 'text', lambda x, d, p: x[10]),
		              
		              
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No', 'Nama', 'Department', 'Test Tertlis HRD','Test Wawancara HRD',
				'Test Wawancara USR 1', 'Test Wawancara USR 2',	'Management Approval',	'Test Kesehatan', 'Keterangan','Status',])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])

		    row_count += 1
		     
		pass

detail_monitoring_progres('report.detail.monitoring.progres', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class sumary_monitoring_progres_recruitment(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Detail Monitoring Progres'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30, 'text', lambda x, d, p: x[0]),	
		              ('Department', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Qty Total', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Test Tertlis HRD', 1, 100, 'text', lambda x, d, p: x[3]),
		              ('Wawancara HRD', 1, 100, 'text', lambda x, d, p: x[4]),
		              ('Wawancara USR 1', 1, 100, 'text', lambda x, d, p: x[5]),
		              ('Wawancara USR 2', 1, 100, 'text', lambda x, d, p: x[6]),
		              ('Management Approval', 1, 100, 'text', lambda x, d, p: x[7]),
		              ('Test Kesehatan', 1, 90, 'text', lambda x, d, p: x[8]),
		              ('Pending', 1, 70, 'text', lambda x, d, p: x[9]),
		              
		              
		              
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No', 'Department', 'Qty Total', 'Test Tertlis',
				'Wawancara HRD', 'Wawancara USR 1', 'Wawancara USR 2','Management Approval',	
				'Test Kesehatan', 'Pending'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])

		    row_count += 1
		     
		pass

sumary_monitoring_progres_recruitment('report.sumary.monitoring.progres.recruitment', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class daftar_pelamar(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Detail Monitoring Progres'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30, 'text', lambda x, d, p: x[0]),	
		              ('Nama', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Subjek', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Posisi Diaplikasikan', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jenis Kelamin', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Usia', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Pendidikan', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Jurusan', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('Perguruan Tinggi', 1, 70, 'text', lambda x, d, p: x[9]),
		              ('Pengalaman', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('AI. Domisili (Kota)', 1, 70, 'text', lambda x, d, p: x[11]),
		              ('Phone', 1, 70, 'text', lambda x, d, p: x[12]),
		              ('Email', 1, 70, 'text', lambda x, d, p: x[13]),
		              
		              
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Nama','Subjek','Posisi Diaplikasikan','Jenis Kelamin','Usia',
						'Status','Pendidikan','Jurusan','Perguruan Tinggi', 'Pengalaman','AI. Domisili (Kota)', 'Phone','Email',])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])

		    row_count += 1
		     
		pass

daftar_pelamar('report.daftar.pelamar', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class detail_sarmut(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Detail Sasaran Mutu'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30, 'text', lambda x, d, p: x[0]),	
		              ('Divisi', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Departement', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Bagia', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jabatan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Jumlah Orang Yang dibutuhkan', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Level', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Tanggal Permohonan Dari User', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Persetujuan Diterima Dari Atasan User', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('waktu Proses 1', 1, 70, 'text', lambda x, d, p: x[9]),
		              ('Persetujuan Diterima Dari Direktur', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('Waktu Proses 2', 1, 70, 'text', lambda x, d, p: x[11]),
		              ('Persetujuan Diterima Dari Direktur Fin & Adnm', 1, 70, 'text', lambda x, d, p: x[12]),
		              ('Waktu Proses 3', 1, 70, 'text', lambda x, d, p: x[13]),
		              ('Diterima Bagian Recruitment Setelah Persetujuan', 1, 70, 'text', lambda x, d, p: x[14]),
		              ('Waktu Proses 4', 1, 70, 'text', lambda x, d, p: x[15]),
		              ('Wawancara 1', 1, 70, 'text', lambda x, d, p: x[16]),
		              ('Waktu Proses 5', 1, 70, 'text', lambda x, d, p: x[17]),
		              ('Waktu Proses Persetujuan', 1, 70, 'text', lambda x, d, p: x[18]),
		              ('Waktu Proses Tunggu Wawancara Pertama', 1, 70, 'text', lambda x, d, p: x[19]),
		              ('Jumlah NWD', 1, 70, 'text', lambda x, d, p: x[20]),
		              ('Waktu Total', 1, 70, 'text', lambda x, d, p: x[21]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[22]),
		              ('Keterangan', 1, 70, 'text', lambda x, d, p: x[23]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Divisi','Departement','Bagia','Jabatan','Jumlah Orang Yang dibutuhkan',
				'Level','Tanggal Permohonan Dari User','Persetujuan Diterima Dari Atasan User','waktu Proses 1','Persetujuan Diterima Dari Direktur', 
				'Waktu Proses 2', 'Persetujuan Diterima Dari Direktur Fin & Adnm','Waktu Proses 3','Diterima Bagian Recruitment Setelah Persetujuan', 
				'Waktu Proses 4','Wawancara 1','Waktu Proses 5','Waktu Proses Persetujuan','Waktu Proses Tunggu Wawancara Pertama', 
				'Jumlah NWD','Waktu Total','Status','Keterangan' ])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])
		    ws.write(row_count, 14, x[14])
		    ws.write(row_count, 15, x[15])
		    ws.write(row_count, 16, x[16])
		    ws.write(row_count, 17, x[17])
		    ws.write(row_count, 18, x[18])
		    ws.write(row_count, 19, x[19])
		    ws.write(row_count, 20, x[20])
		    ws.write(row_count, 21, x[21])
		    ws.write(row_count, 22, x[22])
		    ws.write(row_count, 23, x[23])

		    row_count += 1
		     
		pass

detail_sarmut('report.detail.sarmut', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)

class sumary_sarmut(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Detail Sasaran Mutu'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
		cols_specs = [
					  ('No', 1, 30, 'text', lambda x, d, p: x[0]),	
		              ('Jabatan', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Jumlah Permohonan', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Jumlah Orang Yang Dibutuhkan', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jumlah Waktu Proses Yang Dibutuhkan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Rata-Rata Waktu Proses Yang Dibutuhkan', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Jumlah Proses Tunggu Wawancara 1', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Rata-Rata Proses Tunggu Wawancara 1', 1, 70, 'text', lambda x, d, p: x[7]),
		              ('Jumlah NWD', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('Total Waktu Proses, 1, 70', 'text', lambda x, d, p: x[9]),
		              ('Rata-Rata Waktu Pemenuhan Karyawan', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('Target', 1, 70, 'text', lambda x, d, p: x[11]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[12]),
		              ('Keterangan', 1, 70, 'text', lambda x, d, p: x[13]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No','Jabatan','Jumlah Permohonan','Jumlah Orang Yang Dibutuhkan','Jumlah Waktu Proses Yang Dibutuhkan',
				'Rata-Rata Waktu Proses Yang Dibutuhkan','Jumlah Proses Tunggu Wawancara 1','Rata-Rata Proses Tunggu Wawancara 1',
				'Jumlah NWD','Total Waktu Proses','Rata-Rata Waktu Pemenuhan Karyawan', 'Target','Status','Keterangan',])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 1
		for x in data['csv']:
		    ws.write(row_count, 0, x[0])
		    ws.write(row_count, 1, x[1])
		    ws.write(row_count, 2, x[2])
		    ws.write(row_count, 3, x[3])
		    ws.write(row_count, 4, x[4])
		    ws.write(row_count, 5, x[5])
		    ws.write(row_count, 6, x[6])
		    ws.write(row_count, 7, x[7])
		    ws.write(row_count, 8, x[8])
		    ws.write(row_count, 9, x[9])
		    ws.write(row_count, 10, x[10])
		    ws.write(row_count, 11, x[11])
		    ws.write(row_count, 12, x[12])
		    ws.write(row_count, 13, x[13])

		    row_count += 1
		     
		pass

sumary_sarmut('report.sumary.sarmut', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)