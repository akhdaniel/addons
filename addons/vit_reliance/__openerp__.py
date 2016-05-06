{
	"name": "Reliance Data Repository Customer Information System", 
	"version": "1.0", 
	"depends": [
		"base",
		"stock",
		"product",
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

		"data/sequence.xml",
		"data/cron.xml",
		"data/parameter.xml",
	],
	"installable": True,
	"auto_install": False,
}