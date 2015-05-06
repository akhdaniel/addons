{
    'version': '0.2',
    'name': 'Aplikasi MLM',
    'depends': ['website', 'sale', 'base','account','product', 'hr', 'report','account_accountant','stock'],
    'author'  :'vitraining.com',
    'category': 'Website',
    'data': [
      'menu/menu_configuration.xml',   

      'data/mlm_plan.xml',   
      'data/ir_sequence.xml',   
      'data/bonus.xml',   
      'data/paket.xml',   
    	'data/res_partner_category.xml',   

      'view/member.xml',
      'view/company.xml',
      'view/member_bonus.xml',
      'view/mlm_plan.xml',
      'view/paket.xml',
      'view/broadcast.xml',
      'view/ads.xml',
      'view/paket_produk.xml',

      'security/group.xml',
      'security/ir.model.access.csv',

      'menu/menu_membership.xml',   
      'menu/menu_bonus.xml',   
      'menu/menu_broadcast.xml',   
      'menu/menu_ads.xml',

      'menu/menu_context_bonus.xml',
      'view/d3tree.xml',   
    ],    
    'qweb' : ['static/src/xml/*.xml'],
    'description': """
Description
==================
Aplikasi untuk system MLM lengkap

Model
====================
mlm_plan



""",
    'installable':True,
    'application':True,

}
