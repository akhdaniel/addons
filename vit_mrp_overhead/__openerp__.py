{
    'version': '0.1',
    'name': 'Mrp Overheads',
    'depends': ['base','product','resource','mrp','account_cancel'],
    'author'  :['vitraining.com','rahasia2alpha@gmail.com'],
    'category': 'Manufacturing',
    'description': """
        Mrp HPP ,
        - Penambahan Fields Overheads dan jurnal-jurnalnya 
        - HPP Terupdate dengan Penambahan dari WIP Overheadsny 

""",
    'installable':True,
    'data': [
          'master_overheads.xml',
          'mrp_view.xml',
          'menu.xml',
          'account_view.xml',
    ],
}


