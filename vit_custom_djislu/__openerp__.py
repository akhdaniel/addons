{
    'name': 'Custom General Module for DJISLU',
    'version': '0.1',
    'author'  :'vitraining.com',
    'category': 'werehouse',
    'description': """



""",    
    'depends': ['product',
     'account',
     'account_accountant',
     'account_asset',
     'account_budget',
     'account_cancel',
     'sale',
     'purchase',
     'stock',
     'fleet',
     'vit_hr_standard'],
     'update_xml':[
	'product.xml',
	'partner.xml',
    'sales.xml',
    'fleet.xml',
    'invoice.xml',
    'groups/groups.xml',
    'workflow/picking_list_workflow.xml',],
    'data': ['security/ir.model.access.csv'],
    'active': False,
    'installable': True,
    'application': True,
}
