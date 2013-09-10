from openerp.osv import fields, osv

class title(osv.osv):
    _name='hr.title' 
    
    _columns ={
        'name' : fields.char('Description'),
        'digit':fields.integer('Digit'),
        'code':fields.char('Code'),
        'Jenis_tunjangan':fields.selection([('overtime','Overtime'),('incentive','Incentive')],"Jenis Tunjangan"),
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
