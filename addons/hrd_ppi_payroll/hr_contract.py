from openerp.osv import fields, osv

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    _columns = {
        'master_gaji_id':fields.many2one('hr.master_gaji', "incentive"),
        'makan':fields.related('master_gaji_id','makan',type='integer',relation='hr.master_gaji',string='Uang Makan',readonly=True),
        'transport':fields.related('master_gaji_id','transport',type='integer',relation='hr.master_gaji',string='Uang Transport',readonly=True),
    }
hr_contract()    
    
class master_gaji(osv.osv):
    _name="hr.master_gaji"
    
    _columns = {
        "name" : fields.selection([('gol1-2','Gol 1-2'),('gol3-4','Gol 3-4'),('gol5','Gol 5 keatas')],'Pilih Golongan'),
        "makan" :fields.integer("Uang Makan"),
        "transport" : fields.integer("Uang Transportasi"),
    }
    _sql_constraints = [('status_uniq', 'unique(status)','Kode status tidak boleh sama')]
    
    
master_gaji()    
