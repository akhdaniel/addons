{
	'name':'Sage Truck Module',
	'description':'Add Date ETA on Invoice',
	'version':'1.0',
	'website':'http://www.vitraining.com',
	'depends':['base','product',"process", "decimal_precision",'account','sale','purchase'],
	'init_xml':[],
	'update_xml':[
		'orders_sage.xml'
	],
	'demo_xml':[],
	'installable':True,
	'active':False,
	'certificate':'',
}
