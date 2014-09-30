
{
    'name': 'MRP for Garment Industry',
    'version': '1.0',
    'category': 'Manufacturing',
    'sequence': 19,
    'summary': 'Add grade b, waste on produce',
    'description': """

* Input Grade B , Waste Qty on MRP produce
* Select Grade B product
* Generate Stock move for Grade B 
* Select Waste product 
* Generate stock move for Waste product 
* Generate related accounting journal

""",
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'images' : [],
    'depends': ['base', 'product', 'mrp' , 'mrp_operations'],
    'data': [
        'mrp_product_produce.xml',
        'mrp_production.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
