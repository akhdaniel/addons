{
	"name": "Capture Gross and Nett on Receive", 
	"version": "1.0", 
	"depends": [
		"base",
		"stock",
		"account"
	], 
	"author": "vitraining", 
	"category": "Warehouse", 
	"description": """\

Manage
==============

* can input Gross and Nett received value
* if difference, create adjustment journal : inventory => cost Gross nett difference

""",
	"data": [
		"receive.xml"
	],
	"installable": True,
	"auto_install": False,
}