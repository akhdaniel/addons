from openerp.osv import osv,fields
from openerp import tools
# from openerp.tools.translate import _

class hr_pajak_refpegawaia1(osv.Model):
	_name 			= 'hr.pajak.refpegawaia1'
	_auto 			= False
	_description 	= 'PPI Pajak Reports'

	_columns 		= 	{
		'npwp'			: fields.char('NPWP'),
		'nik' 			: fields.char('NIK'),      
		'nama'			: fields.char('Nama'),  
		'alamat' 		: fields.text('Alamat'),
		'jenis_kelamin' : fields.selection([('male','L'),('female','P')],'Jenis Kelamin',readonly=True),
		'status_ptkp'	: fields.char("Status PTKP"),
		'jum_tanggungan': fields.integer('Jumlah Tanggungan'),
		'nama_jabatan'	: fields.char('Nama Jabatan'),
		'wp_luar_negri' : fields.selection([('y','Y'),('n','N')],'WP Luar Negri',readonly=True),
		'kode'			: fields.integer('Kode Negara'),
						}

	def init(self, cr):

		"""
		ide_report 
		@param cr: the current row, from the database cursor
		"""
		tools.drop_view_if_exists(cr, 'hr_pajak_refpegawaia1')
		cr.execute("""
			CREATE OR REPLACE VIEW hr_pajak_refpegawaia1 AS (
				SELECT
					e.id 					,
					e.npwp 			as npwp,
					e.nik 			as nik,
					e.name_related	as nama,
					e.alamat1 		as alamat,
					e.kelamin 		as jenis_kelamin,
					pt.kode 		as status_ptkp,
					e.jml_anak 		as jum_tanggungan,
					e.job_id		as nama_jabatan,	
					CASE WHEN co.name = 'Indonesia' THEN 'n' ELSE 'y' END as wp_luar_negri
				FROM
					hr_employee e
				LEFT JOIN hr_ptkp pt on ptkp_id = pt.id
				LEFT JOIN res_country co on country_id = co.id
			)""")

hr_pajak_refpegawaia1()

class res_country(osv.osv):
	_name 		= 'res.country'
	_inherit	= 'res.country'

	_columns = {
		'country_code' :fields.integer('Country Code')
	}

res_country()