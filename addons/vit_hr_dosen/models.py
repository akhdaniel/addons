# -*- coding: utf-8 -*-
from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big

class hr_employee(osv.osv):
	_name = "hr.employee"
	_inherit = "hr.employee"

	_columns = {
		'nid' : fields.char("NID"),
		'tmt' : fields.char("TMT"),
		'jurusan_id' : fields.many2one("master.jurusan", string="Jurusan/Program Studi"),
		'thn_png' : fields.char("Tahun Pengangkatan"),
		'ijasah' : fields.many2one("master.jenjang", string="Ijazah"),
		'no.sk' : fields.char("No. SK Rektor/BPH"),
		'jenjang' : fields.one2many("jenjang.pendidikan", "employee_id"),
		'ket' : fields.char("Keterangan"),
		'pendidikan':fields.selection([('TK','TK'),('SD','SD'),('SMP','SMP'),('SMA','SMA/SMK/SMF'),('Diploma','Akademi/Diploma'),('S1','S1'),('S2','S2'),('S3','S3')],'Pendidikan'),
		'mulai_kerja' : fields.date("Mulai Kerja"),
		'sampai_kerja': fields.date("Sampai Dengan"),
		'no.sk/surat' : fields.char("Nomor SK/Surat"),
	}
hr_employee()

class jenjang_pendidikan(osv.osv):
	_name = "jenjang.pendidikan"

	_columns = {
		"employee_id" : fields.many2one("hr.employee"),
		"jenjang" : fields.many2one("master.jenjang","Jenjang"),
		"bidang" : fields.char("Bidang Ilmu"),
	}
jenjang_pendidikan()