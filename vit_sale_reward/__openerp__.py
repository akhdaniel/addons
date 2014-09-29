{
    'name': 'Sale Reward',
    'version': '0.1',
    'author'  :'vitraining.com',
    'category': 'Sale',
    'description': """

* Manage master data reward eg, buy 1000 per SO get 1 point, saved in res_partner.point
* Manage reward point conversion to currency amount
* Manage payable COA related to reward collected
* Collect point on action confirm sale order


""",    
    'depends': [
        'sale', 'base' , 'account', 'vit_partner_addmutif'
    ],
    'update_xml':[],
    'data': [
        'menu.xml',
        'master_reward.xml',
        'sale.xml',
        'partner.xml',
    ],
    'active': False,
    'installable': True,
    'application': True,
}
