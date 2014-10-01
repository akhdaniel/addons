
{
    'name': 'BOM Product Filter',
    'version': '1.0',
    'category': 'Manufacturing',
    'sequence': 19,
    'summary': 'Add product filter on BOM only can be sold',
    'description': """

* only can be sold product appears on BOM


""",
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'images' : [],
    'depends': ['base', 'product', 'mrp' ],
    'data': [
        'bom.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
