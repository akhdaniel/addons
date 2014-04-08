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
		 
		#import pdb;pdb.set_trace() 
		row_count = 4
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


class pemenuhan_recruitment(report_xls):

	def generate_xls_report(self,parser,data,obj,wb):
		ws = wb.add_sheet(('Laporan Pemenuhan Recruitment'))
		ws.panes_frozen = True
		ws.remove_splits = True
		ws.portrait = 0 # Landscape
		ws.fit_width_to_pages = 1
	 	row_count = 4
		cols_specs = [
		              ('No Permintaan', 1, 70, 'text', lambda x, d, p: x[0]),
		              ('Tanggal Permintaan', 1, 70, 'text', lambda x, d, p: x[1]),
		              ('Department', 1, 70, 'text', lambda x, d, p: x[2]),
		              ('Jabatan', 1, 70, 'text', lambda x, d, p: x[3]),
		              ('Jumlah Permintaan', 1, 70, 'text', lambda x, d, p: x[4]),
		              ('Aktifitas', 1, 70, 'text', lambda x, d, p: x[5]),
		              ('Tanggal Seleksi', 1, 70, 'text', lambda x, d, p: x[6]),
		              ('Jumlah Kandidat',1, 70, 'Text', lambda x, d, p: x[7] )
		              ('Jumlah Diterima', 1, 70, 'text', lambda x, d, p: x[8]),
		              ('Permohonan Masuk', 1, 70, 'text', lambda x, d, p: x[9]),
		              ('Status', 1, 70, 'text', lambda x, d, p: x[10]),
		              ('Keterangan',  1, 70, 'text', lambda x, d, p: x[11]),
		]
		
		style = xlwt.easyxf('pattern: pattern solid, fore_colour yellow;')
		title = self.xls_row_template(cols_specs, ['No Permintaan','Tanggal Permintaan','Department','Jabatan',
        'Jumlah Permintaan','Aktifitas','Tanggal Seleksi','jumlah Kandidat','Jumlah Ditrima','Permohonan Masuk','Status','Keterangan'])
		self.xls_write_row_header(ws, 0, title, style, set_column_size=True)
		 
		row_count = 4
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

		    row_count += 1
		     
		pass

pemenuhan_recruitment('report.pemenuhan.recruitment', 'hr_pemenuhan', 'addons/hrd_ppi/wizard/report_excel.mako', parser=ReportStatus, header=False)
