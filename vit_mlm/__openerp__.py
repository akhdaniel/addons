{
    'version': '0.2',
    'name': 'Aplikasi MLM',
    'depends': ['website', 'sale', 'base','account','product', 'hr', 'report'],
    'author'  :'vitraining.com',
    'category': 'Website',
    'data': [
      'menu/menu_configuration.xml',   

      'data/mlm_plan.xml',   
      'data/ir_sequence.xml',   
      'data/bonus.xml',   
    	'data/paket.xml',   

      'view/member.xml',
      'view/company.xml',
      'view/member_bonus.xml',
      'view/mlm_plan.xml',
      'view/pages.xml',
      'view/paket.xml',

      'security/group.xml',
      'security/ir.model.access.csv',

      'menu/menu_membership.xml',   

      'static/src/d3.min.js',
      
    ],    
    'description': """
Description
==================
Aplikasi untuk system MLM lengkap

Model
====================
mlm_plan



""",
    'installable':True,

}
