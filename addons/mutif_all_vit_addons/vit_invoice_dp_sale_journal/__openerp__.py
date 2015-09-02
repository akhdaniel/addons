{
	'name':'Invoice DP Accounting Module',
	'description':'Can Add DP Journal on Invoice, reducing the amount of AR',
	'version':'1.0',
	'website':'http://www.vitraining.com',
	'depends':['base','product',"process", "decimal_precision",'account','sale','purchase'],
	'init_xml':[],
	'data':[
		'invoice.xml',
		'security/ir.model.access.csv',
		'company.xml',
	],
	'demo_xml':[],
	'installable':True,
	'active':False,
	'certificate':'',
}
