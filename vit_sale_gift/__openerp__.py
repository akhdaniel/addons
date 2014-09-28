{
    'name': 'Sale Gift',
    'version': '0.1',
    'author'  :'vitraining.com',
    'category': 'Sale',
    'description': """

* Manage gift master data eg, buy one product get one other product
* Buy 20 product of category A and B get one product 
* Will add new sale order line if condition match 

""",    
    'depends': [
        'product', 'stock', 'sale', 'base'
    ],
    'update_xml':[],
    'data': [
        'menu.xml',
        'master_gift.xml',
    ],
    'active': False,
    'installable': True,
    'application': True,
}
