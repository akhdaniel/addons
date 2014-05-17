from openerp.osv import fields, osv

class warning_schedule(osv.osv):
	_name = 'warning.schedule'
	_description = 'form worning schedule'

	_sql_constraints = [
		('unique_schedule','unique(name)','Warning Tidak Boleh Sama !')
		]

	_columns = {
		'name' : fields.selection([('kontrak','Kontrak'),('alat_berat','Alat Berat'),('iso','ISO')], string='Warning'),
		'date_warning' : fields.integer('Warning/Hari'),
		'warning_kontrak' : fields.one2many('hr.employee','link_warning','Kontrak Yang Akan Berakhir', readonly=True),
	}