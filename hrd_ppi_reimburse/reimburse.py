import datetime
import time
from itertools import groupby
from operator import itemgetter

import math
from openerp import netsvc
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import psycopg2

REIMBURSE_STATES =[
	('draft','Draft'),
	('verify','Verify'),
	('reject','Reject'),
	('approve','Approve'),
	('approve2','Second Approve'),
                   ]

class reimburse(osv.osv):
    _name="reimburse"
    _rec_name="jenis"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _track = {
        'state': {
            'reimburse.mt_reimburse_approved': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'approve2',
            'reimburse.mt_reimburse_refused': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'reject',
            'reimburse.mt_reimburse_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'verify',
            }
        }, 
    
    def employe(self, cr, uid,ids,vals,name,context=None):  
        #import pdb;pdb.set_trace()
        result ={}
        for xxx in self.browse(cr,uid,ids):
            tahun = xxx.tahun
            thn = time.strftime('%Y')
            tanggal =xxx.tanggal
            if tahun == thn :
                if tanggal == False :
                    yyy = xxx.employee_id.name
                    contract_obj = self.pool.get('hr.contract')
                    co_id = contract_obj.search(cr, uid,[('employee_id', '=', yyy)],context=context) 
                    ob= contract_obj.browse(cr, uid, co_id, context=context)[0]                             
                    jeje=xxx.jenis      
                    obcd=ob.department_id.id 
                    if jeje == 'obat':  
                        result[xxx.id]=ob.jatah_reimburse_pengobatan                    
                    elif jeje == 'rawat':   
                        result[xxx.id]=ob.jatah_reimburse_perawatan                   
        return result       
    
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _compute_sisa_reimburse(self, cr, uid, ids, name, args, context=None):
        result = {}
        for hol in self.browse(cr, uid, ids, context=context):
            if hol.type=='remove':
                result[hol.id] = hol.nominal
            else:
                result[hol.id] = -hol.nominal
        return result
                   
    def action_draft(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':REIMBURSE_STATES[0][0]},context=context)

    def action_verify(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':REIMBURSE_STATES[1][0]},context=context)
 
    def action_reject(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':REIMBURSE_STATES[2][0]},context=context) 
    	
    def action_approve(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':REIMBURSE_STATES[3][0]},context=context)   
    	 
    def action_approve2(self,cr,uid,ids,context=None): 
    	return self.write(cr,uid,ids,{'state':REIMBURSE_STATES[4][0]},context=context)
    
    _columns={
        'jenis':fields.selection([('obat','Pengobatan Tahunan'),('rawat','Perawatan Rumah Sakit')],'Jenis Reimburse'),
        'employee_id':fields.many2one('hr.employee','Nama Karyawan',select=True,store=True),
        'user_id':fields.related('employee_id', 'user_id', type='many2one', relation='res.users', string='User', store=True),
        'department_id' : fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='Departemen',store=True,readonly=True),
        'nominal':fields.function(employe,string='Alokasi Reimburse',store=True),
        'nomin' : fields.float("Permintaan Reimburse"),
        'sisa_reimburse': fields.function(_compute_sisa_reimburse, string='Sisa Reimburse', store=True),
        'tanggal':fields.date('Tanggal',required=True),
        'keterangan':fields.char('Keterangan',200),
        'bukti':fields.binary('Bukti File',),
        'state': fields.selection(REIMBURSE_STATES, 'Status', readonly=True, help="Gives the status of the reimburse."),  
        'type': fields.selection([('remove','Permohonan Reimburse'),('add','Alokasi Reimburse')], 'Tipe Reimburse', required=True, readonly=True, states={'draft':[('readonly',False)], 'verify':[('readonly',False)]}, select=True),  
        'parent_id': fields.many2one('reimburse', 'Parent'),      
        "tahun" : fields.char("Tahun",readonly=True),
            }
    _defaults = {
        'employee_id': _employee_get,
        'state': REIMBURSE_STATES[0][0],
        'type': 'remove',
        'user_id': lambda obj, cr, uid, context: uid,    
        'tahun' : lambda *a : time.strftime('%Y')    
        }   
        
    #def unlink(self, cr, uid, ids, context=None):
     #   for rec in self.browse(cr, uid, ids, context=context):
      #      if rec.state not in ['draft', 'reject', 'verify']:
       #         raise osv.except_osv(_('Warning!'),_('Anda tidak bisa menghapus reimburse ketika statusnya %s.')%(rec.state))
        #return super(reimburse, self).unlink(cr, uid, ids, context)       
        
    def create(self, cr, uid, values, context=None):
        """ Override to avoid automatic logging of creation """
        if context is None:
            context = {}
        context = dict(context, mail_create_nolog=True)
        return super(reimburse, self).create(cr, uid, values, context=context)

    def reimburse_alloc(self,cr,uid, ids=None,context=None):
        #""" Override to avoid automatic logging of creation """
        #import pdb; pdb.set_trace()
        employee_ids = self.pool.get('hr.employee')
        src = employee_ids.search(cr,uid, [])
        employs = employee_ids.browse(cr, uid, src)
        values={}
        values1={}
        for xxx in employs:
            '''result ={}
            tahun = xxx.tahun
            thn = time.strftime('%Y')
            if tahun == thn :
                yyy = xxx.employee_id.name
                contract_obj = self.pool.get('hr.contract')
                co_id = contract_obj.search(cr, uid,[('employee_id', '=', yyy)],context=context) 
                ob= contract_obj.browse(cr, uid, co_id, context=context)[0]                             
                jeje=xxx.jenis      
                obcd=ob.department_id.id 
                if jeje == 'obat':  
                    result[xxx.id]=ob.jatah_reimburse_pengobatan                    
                elif jeje == 'rawat':   
                    result[xxx.id]=ob.jatah_reimburse_perawatan                          
            '''
            values = {
                'jenis':'obat',
                #'Keterangan': _("Reimburse Allocation for %s") % _(xxx.name), 
                'employee_id':xxx.id,
                'keterangan':"tes"
                }
            self.create(cr,uid,values,context=context)
            values = {
                'jenis':'rawat',
                #'Keterangan': _("Reimburse Allocation for %s") % _(xxx.name),
                #'nominal': result,
                #'tahun':time.strftime('%Y'),  
                'employee_id':xxx.id,
                'keterangan':"tes"
                }
            self.create(cr,uid,values,context=context)
        return True
        
reimburse()

class hr_employee(osv.osv):
    _inherit="hr.employee"

    def create(self, cr, uid, vals, context=None):

        if 'sisa_reimburse_pengobatan' in vals and not vals['sisa_reimburse_pengobatan']:
            del(vals['sisa_reimburse_pengobatan'])
        if 'sisa_reimburse_rs' in vals and not vals['sisa_reimburse_rs']:
            del(vals['sisa_reimburse_rs'])    
        return super(hr_employee, self).create(cr, uid, vals, context=context)

    def _set_remaining_reimburse_obat(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.sisa_reimburse_pengobatan

        reimburse_obj = self.pool.get('reimburse')
        if diff > 0:
            reim_id = reimburse_obj.create(cr, uid, {'name': _('Alokasi untuk %s') % employee.name, 'employee_id': employee.id, 'type': 'add', 'nominal': diff}, context=context)
        elif diff < 0:
            reim_id = reimburse_obj.create(cr, uid, {'employee_id': employee.id, 'type': 'remove','nominal': abs(diff)}, context=context)
        else:
            return False
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'verify', cr)
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'approve', cr)
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'approve2', cr)
        return True

    def _set_remaining_reimburse_rawat(self, cr, uid, empl_id, name, value, arg, context=None):
        employee = self.browse(cr, uid, empl_id, context=context)
        diff = value - employee.sisa_reimburse_rs

        reimburse_obj = self.pool.get('reimburse')
        if diff > 0:
            reim_id = reimburse_obj.create(cr, uid, {'name': _('Alokasi untuk %s') % employee.name, 'employee_id': employee.id, 'type': 'add', 'nominal': diff}, context=context)
        elif diff < 0:
            reim_id = reimburse_obj.create(cr, uid, {'employee_id': employee.id, 'type': 'remove','nominal': abs(diff)}, context=context)
        else:
            return False
        wf_service = netsvc.LocalService("workflow")
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'verify', cr)
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'approve', cr)
        wf_service.trg_validate(uid, 'reimburse', leave_id, 'approve2', cr)
        return True

    def _compute_sisa_reimburse_obat(self, cr, uid, ids, name, args, context=None):
        #import pdb;pdb.set_trace()
       #reimburse = self.pool.get('reimburse').browse(cr, uid, ids, context=context)
        reimburse_obj = self.pool.get("reimburse")
        yyy=0.0
        result={}
        zz=0.0
        for reim in self.browse(cr,uid,ids):
            xxx=reim.name
            search_obj=reimburse_obj.search(cr,uid,[('employee_id','=',xxx)])
            reimb=reimburse_obj.browse(cr,uid,search_obj,context=context)
            for emp in reimb :
                xyz=emp.jenis
                thn = time.strftime('%Y')
                tahun =emp.tahun
                zzz = emp.nominal
                stt = emp.state
                if tahun == thn and stt == 'approve2':
                    if xyz  == "obat":
                        yyy += emp.nomin
                    if zzz != False and xyz == "obat" :
                        zz = emp.nominal
            result[reim.id] =zz - yyy
        return result
        
    def _compute_sisa_reimburse_rawat(self, cr, uid, ids, name, args, context=None):
        #import pdb;pdb.set_trace()
       #reimburse = self.pool.get('reimburse').browse(cr, uid, ids, context=context)
        reimburse_obj = self.pool.get("reimburse")
        yyy=0.0
        result={}
        zz=0.0
        for reim in self.browse(cr,uid,ids):
            xxx=reim.name
            search_obj=reimburse_obj.search(cr,uid,[('employee_id','=',xxx)])
            reimb=reimburse_obj.browse(cr,uid,search_obj,context=context)
            for emp in reimb :
                xyz=emp.jenis
                thn = time.strftime('%Y')
                tahun =emp.tahun
                zzz = emp.nominal
                stt = emp.state
                if tahun == thn and stt == 'approve2':
                    if xyz  == "rawat":
                        yyy += emp.nomin
                    if zzz != False and xyz == "rawat" :
                        zz = emp.nominal
            result[reim.id] =zz - yyy
        return result 

    def _get_reimburse_status(self, cr, uid, ids, name, args, context=None):
        reimburse_obj = self.pool.get('reimburse')
        reimburse_id = reimburse_obj.search(cr, uid,
           [('employee_id', 'in', ids),('type','=','remove'),('state','not in',('cancel','reject'))],
           context=context)
        result = {}
        for id in ids:
            result[id] = {
                'current_reimburse_state': False,
            }
        for reim in self.pool.get('reimburse').browse(cr, uid, reimburse_id, context=context):
            result[reim.employee_id.id]['current_reimburse_state'] = reim.state
        return result

    _columns = {
        'sisa_reimburse_pengobatan': fields.function(_compute_sisa_reimburse_obat, string='Sisa Reimburse Pengobatan', fnct_inv=_set_remaining_reimburse_obat, type="float",),
        'sisa_reimburse_rs': fields.function(_compute_sisa_reimburse_rawat, string='Sisa Reimburse Perawatan RS', fnct_inv=_set_remaining_reimburse_rawat, type="float",),
        'reimburse_ids':fields.one2many('reimburse','employee_id','Daftar Reimburse',readonly=True),
    }

hr_employee()

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    def _hitung_reimburse_obat(self, cr, uid, ids, wage, jatah_reimburse_pengobatan, arg, context=None):
        rec = self.browse(cr, uid, ids, context=context)[0]
        typ=rec.type_id.reimburse_pengobatan
        wag=rec.wage
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
            if wag:
                jatah = typ * wag
            result [r.id]= jatah
        return result    
        
    def _hitung_reimburse_rawat(self, cr, uid, ids, wage, jatah_reimburse_perawatan, arg, context=None):
        rec = self.browse(cr, uid, ids, context=context)[0]
        typ=rec.type_id.reimburse_perawatan
        wag=rec.wage
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
            if wag:
                jatah = typ * wag
            result [r.id]= jatah
        return result          
    
    _columns = {
        "jatah_reimburse_pengobatan":fields.function(_hitung_reimburse_obat, type='float', obj='hr.contract', method=True, store=False,string='Pengobatan Tahunan',readonly=True),
        "jatah_reimburse_perawatan":fields.function(_hitung_reimburse_rawat, type='float', obj='hr.contract', method=True, store=False,string='Perawatan Rumah Sakit',readonly=True),

    }
hr_contract()  

