{
    'name': 'Pharmacy Manufacture Reschedule & Approval',
    'version': '1.0',
    'category': 'Manufacture',
    'description': """
        ** Menambahkan Approval Di stock.picking bila schedule date < Order date, maka akan muncul atau
        bisa melakukan Reschedule tapi harus melalui Approval
        ** Button approve_reschedule akan muncul di user dengan group warehouse/manager
        ** Setelah Manager melakukan approved akan merubah readonly field schedule date menjadi bisa di edit.

       """,
    'author': 'Wawan|Fb/email:rahasia2alpha@gmail.com',
    'depends': ['stock'],
    'data': ['stock.xml'],
    'test': [],    
    'installable': True,
    'active': False,
    'certificate':''   
}