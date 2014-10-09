#
# DIJ SLU
#
{
    'name': 'Faktur(Invoice) and Picking Print',
	'version':'0.1',	
    'depends': ['sale'],
    'author'  :'vitraining.com',
    'category': 'Warehouse',
    'description': """
Print Out Faktur in SO form and Picking List
""",
    'installable':True,
    'data': ['report/so_picking.xml',],
}
