{
    'version': '0.2',
    'name': 'Aplikasi MLM',
    'depends': ['base','account','product', 'hr', 'report','website'],
    'author'  :'vitraining.com',
    'category': 'Accounting',
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


      'security/ir.model.access.csv',

      'menu/menu_membership.xml',   
      
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
