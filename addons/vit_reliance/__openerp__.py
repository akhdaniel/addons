{
	"name": "Reliance Data Repository Customer Information System", 
	"version": "1.1", 
	"depends": [
		"base",
		"stock",
		"product",
		"calendar",
		"mail",
	], 
	"author": "vitraining.com", 
	"category": "Tools", 
	"description": """\

Manage
============================

* this is my 
* this is my 
* FTP upload: make sure odoo user can read and write ftp upload folders

""",
	"data": [
		"security/groups.xml",
		"security/ir.model.access.csv",
		"views/partner.xml", 
		"views/campaign.xml", 
		"views/product.xml", 
		
		"menu.xml", 
		"views/import_ls.xml", 
		"views/import_ajri.xml", 
		"views/import_arg.xml", 
		"views/import_refi.xml", 
		"views/import_rmi.xml", 
		"views/import_health.xml", 

		"views/import_zip_ls.xml", 
		"views/import_zip_ajri.xml", 
		"views/import_zip_arg.xml", 
		"views/import_zip_refi.xml", 
		"views/import_zip_rmi.xml", 
		"views/import_zip_health.xml", 

		"views/import_ftp_ls.xml", 
		"views/import_ftp_health.xml", 
		"views/import_ftp_arg.xml", 
		"views/import_ftp_ajri.xml", 
		"views/import_ftp_rmi.xml", 
		"views/import_ftp_refi.xml", 

		"data/sequence.xml",
		"data/cron.xml",
		"data/parameter.xml",
		"data/res.country.state.csv",
		"data/reliance.states_mapping.csv",
		"data/reliance.agama.csv",
		"data/reliance.jenis_kelamin.csv",
		"data/reliance.status_nikah.csv",
		"data/reliance.pekerjaan.csv",
		"data/reliance.pekerjaan_ls.csv",
		"data/reliance.pekerjaan_rmi.csv",
		"data/reliance.pekerjaan_refi.csv",
		"data/reliance.warga_negara.csv",
		"data/reliance.range_penghasilan.csv",
		"data/reliance.range_penghasilan_ls.csv",
		"data/reliance.range_penghasilan_rmi.csv",
		"data/reliance.range_penghasilan_refi.csv",
        # 'views/web_asset.xml',
        'views/master.xml',

	],
    # 'css':['static/src/css/*.css'],
    # 'js':['static/src/js/*.js'],	
	"installable": True,
	"auto_install": False,
}
