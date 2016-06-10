{
	"name": "Import Fingerprint Logs", 
	"version": "1.0", 
	"depends": [
		"base",
		"hr","hr_attendance"
	], 
	"author": "akhmad.daniel@gmail.com", 
	"category": "HR", 
	"description": """\

Manage
======================================================================

* this provide import finger print data 
* created menu: Attandace - Import Krisbow
* created object: vit.kribow
* created views: list krisbow
* crob job will process the imported logs unto the hr_attendance data
* 

""",
	"data": [
		"view/krisbow.xml", 
		"data/cron.xml",
	],
	"installable": True,
	"auto_install": False,
}