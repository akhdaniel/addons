{
    'name': 'Master Partner Discount',
    'version': '0.1',
    'author'  :'vitraining.com',
    'category': 'Sale',
    'description': """

Master Partner Discount

""",    
    'depends': [
        'sale', 'base','vit_partner_addmutif'
    ],
    'update_xml':[],
    'data': [
        'partner.xml',
        'menu.xml',
        'master_disc.xml',
    ],
    'installable': True,
    'application': True,
}
