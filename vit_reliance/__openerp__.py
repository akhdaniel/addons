{
	"name": "Reliance Data Repository Customer Information System", 
	"version": "1.0", 
	"depends": [
		"base",
		"board",
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
* this is my

""",
	"data": [
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

		"data/sequence.xml",
		"data/cron.xml",
	],
	"installable": True,
	"auto_install": False,
}