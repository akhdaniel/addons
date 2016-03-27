{
    'name' : 'User Purchase Request',
    'version' : '0.1',
    'category': 'Purchase Management',
    'images' : [],
    'depends' : ['stock','purchase', 'purchase_requisition','hr', 'vit_mps_fields',
        'vit_lucas_groups'],
    'author' : 'vitraining.com',
    'description': """
Purchase Request
==========================================
* Allow department users to request product to be purchased 
* Approval by Dept Head 
* Allow Purchase Manager to create CAll For Bid, then RFQ, and PO
* Display total RFQ amount under Call for Bids 

    """,
    'website': 'http://www.vitraining.com',
    'data': [
        'menu.xml',
        'security/ir.model.access.csv',
        'security/groups.xml',        
        'product_request.xml',
        'sequence.xml',
        'pr.xml',
        'reports/product_request.xml',
    ],
    'test': [
    ],
    'demo': [],
    'installable': True,
    'auto_install': False
}