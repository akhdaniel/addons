
{
    'name': 'Work Orders for Garment Industry',
    'version': '1.0',
    'category': 'Manufacturing',
    'sequence': 19,
    'summary': 'Add partner, in, out qty in Work Order mrp.production.workcenter.line',
    'description': """
Add:
partner
in qty
out qty 

Work Order mrp.production.workcenter.line
""",
    'author': 'vitraining.com',
    'website': 'http://www.vitraining.com',
    'images' : [],
    'depends': ['base', 'product', 'mrp' , 'mrp_operations'],
    'data': [
        "workcenter_line.xml",
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
