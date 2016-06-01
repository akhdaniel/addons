from openerp.osv import fields, osv

class title(osv.osv):
    _name='hr.title' 
    
    _columns ={
        'name' : fields.char('Description'),
        'digit':fields.integer('Digit'),
        'code':fields.char('Code'),
        'urutan':fields.char("Urutan"),
    }
title

class extitle(osv.osv):
    _name='hr.extitle' 
    
    _columns = {
        'name' : fields.char('Description'),
        'digit':fields.integer('Digit'),
        'code':fields.char('Code')
        }
extitle()
