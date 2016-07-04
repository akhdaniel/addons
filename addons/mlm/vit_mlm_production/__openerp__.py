{
    'version': '0.1',
    'name': 'MLM Bonus Production',
    'depends': ['vit_mlm', 'vit_mlm_sale_point'],
    'author'  :'vitraining.com',
    'category': 'Website',
    'data': [
      'mlm_production.xml',
      'data/bonus.xml',
      'data/bonus_produksi_scheduler.xml' ,
      'menu/menu_bonus_produksi.xml',   
    ],    
    'qweb' : ['static/src/xml/*.xml'],
    'description': """

Tambahan Parameter Bonus Production pada menu MLM Plan

""",
    'installable':True,
    'application':True,

}
