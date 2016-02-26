{
	"name": "Auto Reset to 1 sequence every month", 
	"version": "1.0", 
	"depends": [
		"base",
		"account"
	], 
	"author": "vitraining.com", 
	"category": "Tools", 
	"description": """\

Manage
=================================================

* created new field : is_autoreset_monthly and is_autoreset_yearly in ir_sequence, 
  for example for invoice, sales order, puchase order: 
* for monthy reset, format sequence should be: DOC/yyyy/mm/00001
* every month or year, cron will look for ir_sequence with is_reset_monthly=True or is_reset_yearly=True 
  and update the next_number = 1
* function cron_reset() executed monthly at 00:00 every 1st date in month , if its 1st January 
   it will search for is_reset_yearly=True also

""",
	"data": [
		"cron.xml",
		"ir_sequence.xml",
	],
	"installable": True,
	"auto_install": False,
}