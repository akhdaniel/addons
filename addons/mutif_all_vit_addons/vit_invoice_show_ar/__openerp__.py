{
	"name": "Show Outstanding AR on Customer Invoices", 
	"version": "1.0", 
	"depends": [
		"base",
		"sale",
		"account"
	], 
	"author": "vitraining.com", 
	"category": "Accounting", 
	"description": """\

Manage
==============

* add new field in invoice: 
	outstanding_ar_ids: one2many account.move.line
		domain = partner.id and type=receivable
* add new tab on Customer Invoice : AR Balance
* show outstanding AR for the current customer 
* show total outstanding AR 
* show total invoice amount after outstanding AR 

""",
	"data": ["invoice.xml", 
		],
	"installable": True,
	"auto_install": False,
}