from openerp.osv import fields, osv
from osv import osv, fields
from datetime import date
from time import strftime

class employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _inherits = {'resource.resource': "resource_id"}

    _columns = {
        'nik': fields.char('NIK',size=20),
        'sim_a': fields.char('Driver License A No',size=25),
        'sim_b': fields.char('Driver License B No',size=25),
        'pos_code':fields.char('Postal Code', size=8),
        'city':fields.char('City',128),
        'alamat':fields.text('Address (Domicile)',size=160),
        'wifename':fields.char('Wife/Husband Name',128),
        'lahir':fields.date('Wife/Husband Birth'),
        'personal_email':fields.char('Personal E-Mail',128),
        'emergency_contact':fields.char('Emergency Contact',size=25),
        'thn_lulus':fields.date('Graduate Year'),
        'ipk':fields.float('GPA'),
        'mother':fields.char('Name of Biological Mother'),
        'type_salesman_id': fields.many2one('type.salesman','Type Salesman', ondelete='cascade'),
        'warehouse_id' : fields.many2one('stock.warehouse','Cabang', ondelete='cascade'),
        'location_id' : fields.many2one('sale.shop','Location', ondelete='cascade'),
        #'shop_id' : fields.many2one('sale.shop','Location', ondelete='cascade'),
        'agama_id':fields.many2one('hr.employee.agama','Religion'),
        'anak_ids':fields.one2many('hr.employee.anak','employee_id','Children'),
        'pendidikan_id':fields.many2one('hr.employee.pendidikan','Current Education'),
        'sekolah_id':fields.many2one('hr.employee.sekolah','School/University name'),
        'jurusan_id':fields.many2one('hr.employee.jurusan','Concentration'),
        'ktp_id':fields.many2one('hr.employee.ktp','Identification No'),
        'npwp_id':fields.many2one('hr.employee.npwp','Tax No (NPWP)'),
        'tax_id': fields.related('npwp_id', 'tax_id', type='many2one', relation='hr.employee.status', string='Tax Status', store=True, readonly=True),
        'insurance_id':fields.many2one('hr.employee.insurance','Insurance'),
        'status_id':fields.many2one('hr.employee.status','Tax Status'),
        'jamsostek_id':fields.many2one('hr.employee.jamsostek','Jamsostek No'),

        }
         
employee()

class anak(osv.osv):
    _name='hr.employee.anak'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'no':fields.selection([('anak1','1 st'),('anak2','2 nd'),('anak3','3 rd'),('anak4','4 th'),('anak5','5 th'),('anak6','6 th')],'Sequance of Children'),
        'name':fields.char('Name',required=True),
        'gender':fields.selection([('male','Male'),('female','Female')],'Gender'),
        'lahir':fields.date('Date of Birth'),
            }
    _sql_constraints = [
        ('no_uniq', 'unique(no)','Sequence of children already exist !')
    ]
            
anak()
  
class status(osv.osv):
    _name='hr.employee.status'
    
    _columns= {
        'name':fields.char('Tax Status',128,required=True),
            }
status() 

class agama(osv.osv):
    _name='hr.employee.agama'
    
    _columns= {
        'name':fields.char('Name',128,required=True),
            }
agama()      

class pendidikan(osv.osv):
    _name='hr.employee.pendidikan'
    
    _columns= {      
        'name':fields.char('Name',128,required=True),

            }
pendidikan()    

class sekolah(osv.osv):
    _name='hr.employee.sekolah'
    
    _columns= {
        'name':fields.char('Name',128,required=True),
            }
sekolah()

class jurusan(osv.osv):
    _name='hr.employee.jurusan'
    
    _columns= {
        'name':fields.char('Name',128,required=True),
            }
jurusan()

class action(osv.osv):
    _name='hr.applicant.action'
    _rec_name='date'
    _columns={
        'date':fields.date('Next Action',required=True),
        'appreciation':fields.selection([('5', 'Not Good'),('4', 'On Average'),('3', 'Good'),('2', 'Very Good'),('1', 'Excellent')],'Appreciation'),
        'applicant_id':fields.many2one('hr.applicant','Name'),
        }
action()

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    _rec_name='partner_name'

    _columns={
        'action_ids':fields.one2many('hr.applicant.action','applicant_id','Next Action'),

    }

class jamsostek(osv.osv):
    _name='hr.employee.jamsostek'
    _rec_name='no'    
    _columns= {
        'no': fields.char('Number',128,required=True),
        'name':fields.char('Name',128),
        'date':fields.char('Month of Registered',128),
            }

class insurance(osv.osv):
    _name='hr.employee.insurance' 
    _rec_name='no'    
    _columns= {
        'no': fields.char('Number',128,required=True),
        'name':fields.char('Name',128),
        'class': fields.char('Inpatient Class',128),
        'date':fields.date('Start Periode'),
        'date2':fields.date('End Periode'),
            }     

class npwp(osv.osv):
    _name='hr.employee.npwp' 
    _rec_name='no'    
    _columns= {
        'no': fields.char('Number',128,required=True),
        'name':fields.char('Name',128),
        'address': fields.char('Address',128),
        'date':fields.date('Date of Registered'),
        'tax_id':fields.many2one('hr.employee.status','Tax Status'),
        'pkp' : fields.boolean('PKP'),
            }  

class ktp(osv.osv):
    _name='hr.employee.ktp' 
    _rec_name='no'    
    _columns= {
        'no': fields.char('Number',128,required=True),
        'name':fields.char('Name',128),
        'expired':fields.date('Expired Date'),
        'address': fields.char('Address',128),
        'pos_code':fields.char('Postal Code', size=8),
        'city':fields.char('City',128),
            } 

class type_salesman(osv.osv):
    _name='type.salesman'  
    _columns= {
        'no': fields.char('Code',128,required=True),
        'name':fields.char('Name',128),
            }             