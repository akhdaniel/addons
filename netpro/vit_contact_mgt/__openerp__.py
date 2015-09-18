{
        "name" : "Contact Management",
        "version" : "0.1",
        "author" : "vitraining.com",
        "website" : "http://vitraining.com",
        "category" : "netpro",
        "description": """  """,
        "depends" : ['base', 'vit_actuary', 'vit_member'],
        "init_xml" : [ ],
        "demo_xml" : [ ],
        "data" : [
                'security/ir.model.access.csv',
                'view/vit_contact_mgt_view.xml',
                'menu.xml',
        ],
        "installable": True
}