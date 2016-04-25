
{
    'name': 'Add OPOS extension',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 19,
    'summary': 'Add related field to product, journal POS',
    'description': """
Add related field to product
    property_stock_valuation_account_id

Add Journal POS 

""",
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'images' : [],
    'depends': ['sale', 'product'],
    'data': ['journal.xml'],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
