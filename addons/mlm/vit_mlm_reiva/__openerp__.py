{
	"name": "MLM for Reiva",
	"version": "1.0", 
	"depends": [
		'auth_signup',
		"website",
		"vit_mlm",
		"vit_mlm_website",
	],
	"author": "akhmad.daniel@gmail.com", 
	"category": "Website",
	"description": """\

Manage
======================================================================

* additional features requested by Reiva
* update email template : Reset Password, but we must delete the existing one before install or upgrade
*

""",
	"data": [
		'data/paket.xml',
		'security/groups.xml',
		'view/pages.xml',
		'view/member.xml',
		'view/menu.xml',
		'data/email_template.xml',
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}