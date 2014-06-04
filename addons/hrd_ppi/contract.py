from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _
#import pprint

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def create(self, cr, uid, values, context=None):
        employee_pool = self.pool.get('hr.employee')                 
        employee_id = values['employee_id']
        dates = values['date_end']
        name = values['name']
        date_start = values['date_start']
        values['stat'] = 'open'
        src_emp = employee_pool.search(cr,uid,[('id','=',employee_id)])
        brw_emp = employee_pool.browse(cr,uid,src_emp)[0]
        hari = brw_emp.warning_hari
        tanggal = brw_emp.tanggal
        warning_pool = self.pool.get('warning.schedule')
        src_warning = warning_pool.search(cr,uid,[('name','=','kontrak')])
        brw_warning = warning_pool.browse(cr,uid,src_warning)[0]
        durasi = brw_warning.date_warning
        if dates != False :
    		day_now = datetime.now()
        	day_end = datetime.strptime(dates,"%Y-%m-%d")
        	nb_of_days = (day_end - day_now).days + 1   
        if hari > durasi :
        	raise osv.except_osv(_('Peringatan!'),_('Kontrak Karyawan Tidak Boleh Duplikat'))
        else :
        #write a new value to employee
	        if dates == False :
	        	employee_pool.write(cr, uid, [employee_id],
	                        {'status_contract': True,'no_contract': name,'tanggal': dates,'warning_hari': 1000000, 'link_warning' : False}
	                        )
	        else :
	        	employee_pool.write(cr, uid, [employee_id],
	                        {'status_contract': True,'no_contract': name,'tanggal': dates,'warning_hari': nb_of_days,'link_warning' : False}
	                        )     
        if tanggal != False :
            date_employee = datetime.strptime(tanggal,"%Y-%m-%d")
            date_con = datetime.strptime(date_start,"%Y-%m-%d") 
            tot_date = (date_con - date_employee).days                   
            if tot_date <= 0 :
                raise osv.except_osv(_('Peringatan!'),_('Tanggal Kontrak Tidak Boleh Kurang Dari Tanggal Kontrak Sebelumnya'))
            else :
                return super(hr_contract, self).create(cr, uid, values, context)
        date_star = values['date_start']
        dates =datetime.strftime(datetime.now(), "%Y-%m-%d")
        if date_star < dates :
            raise osv.except_osv(_('Peringatan!'),_('Tanggal Mulai Kontrak Tidak Boleh Kurang Dari Tanggal Sekarang'))
        return super(hr_contract, self).create(cr, uid, values, context)

    def onchange_tahun(self,cr,uid,ids, date_end, context=None):
    	dates = date_end
    	if dates == False :
    		tahun = 1000000
    	else:
    		th = str(datetime.strptime(dates,"%Y-%m-%d").year)
    		bl = str(datetime.strptime(dates,"%Y-%m-%d").month)
    		hr = str(datetime.strptime(dates,"%Y-%m-%d").day)
    		tah = th + bl + hr
    		tahun = int(tah)
    	return {'value':{'tahun':tahun}}

    _columns = {
    	'name': fields.char('Contract Reference', size=64, required=True),
    	'status' : fields.boolean('Aktif'),
    	'employee_id': fields.many2one('hr.employee', "Employee",required=True),
    	'tahun' : fields.integer('tahun'),
    	'stat' : fields.char('status Kontak', readonly=True),
        'kelompok_sift' : fields.many2one('hr.contract.schedule','Kelompok Sift'),
    	}

    _defaults = {
    	'status' : True,
    }

    def onchange_employee(self, cr, uid, ids, employee_id):
        employ  = self.pool.get('hr.employee').browse(cr,uid,[employee_id],)[0]
        res={};res['wage']=False; res['job_id']=False       
        res['wage']=employ.wage
        res['job_id']=employ.job_id.id
        ##res['idemp']=employ.id
        return {'value':res}

    def onchange_sift(self, cr, uid, ids, kelompok_sift):
        #import pdb;pdb.set_trace()
        sift = self.pool.get('hr.contract.schedule').browse(cr,uid,[kelompok_sift])[0]
        res={}
        res['working_hours']=sift.sift_roling.schedule.id
        return {'value':res}

   	#Fungsi untuk mewrite status contract di employee
    def status_employee(self, cr, uid, ids=None, context=None):
    	""" Override to avoid automatic logging of creation """
    	if context is None :
    		context = {}
    	context = dict(context, mail_create_nolog=True)
    	dates =datetime.strftime(datetime.now(), "%Y-%m-%d")
    	th = str(datetime.strptime(dates,"%Y-%m-%d").year)
    	bl = str(datetime.strptime(dates,"%Y-%m-%d").month)
    	hr = str(datetime.strptime(dates,"%Y-%m-%d").day)
    	dat = th + bl + hr
    	datas = int(dat)
    	obj_contract = self.pool.get('hr.contract')
    	con_src = obj_contract.search(cr,uid,[('tahun','<',datas)])
    	con_brw = obj_contract.browse(cr,uid,con_src)
    	for contract in con_brw :
    		self.write(cr,uid,ids,{'status':False, 'stat' : 'Close'},context=context)
    	return True

    def duration_employee(self, cr, uid, ids=None, context=None):
		if context is None :
    			context = {}
    		context = dict(context, mail_create_nolog=True)
		#mencari shedule warning
		obj_warning = self.pool.get('warning.schedule')
		src_warning = obj_warning.search(cr,uid,[('name','=','kontrak')])
		brw_warning = obj_warning.browse(cr,uid,src_warning)
		lama = brw_warning[0]
		durasi = lama.date_warning
		dates =datetime.strftime(datetime.now(), "%Y-%m-%d")
		th = datetime.strptime(dates,"%Y-%m-%d").year
    		bl = datetime.strptime(dates,"%Y-%m-%d").month
    		hr = datetime.strptime(dates,"%Y-%m-%d").day
    		#mencari karyawan yang kontrak nya hampir habis
	    	obj_emp = self.pool.get('hr.employee')
	    	src_emp = obj_emp.search(cr,uid,[('tanggal','!=',False)])
	    	brw_emp = obj_emp.browse(cr,uid,src_emp)
	    	for employee in brw_emp :
	    		tgl = employee.tanggal
    			day_now = datetime.now()
        		day_end = datetime.strptime(tgl,"%Y-%m-%d")
        		nb_of_days = (day_end - day_now).days + 1    
    			if nb_of_days <= durasi :
    				obj_emp.write(cr, uid, [employee.id], {'warning_hari': nb_of_days, 'link_warning': lama.id}) 
    			else :
    				obj_emp.write(cr, uid, [employee.id], {'warning_hari': nb_of_days, 'link_warning' : False})
	    	return {'type': 'ir.actions.act_window_close'}

    def unlink(self, cr, uid, ids, context=None):
    	#import pdb;pdb.set_trace()
        obj_cont = self.browse(cr,uid,ids)[0]
        employee_id = obj_cont.employee_id.id
        nama = obj_cont.name
        obj_warning = self.pool.get('warning.schedule')
	src_warning = obj_warning.search(cr,uid,[('name','=','kontrak')])
	brw_warning = obj_warning.browse(cr,uid,src_warning)
	lama = brw_warning[0]
        obj_emp = self.pool.get('hr.employee')
        src_emp = obj_emp.search(cr,uid,[('id','=',employee_id)])
        src_brw = obj_emp.browse(cr,uid,src_emp)
        for employee in src_brw :
        	namas = employee.no_contract
        	if nama == namas :
        		obj_emp.write(cr,uid,[employee.id],{'link_warning':lama.id,'status_contract':False,'no_contract':False,'tanggal':False,
        			'warning_hari' : False})
        contract = []
        for employes in self.browse(cr, uid, ids, context=context):
            contract.append(employes.name)
        return super(hr_contract, self).unlink(cr, uid, ids, context)

    def _check_dates(self, cr, uid, ids, context=None):
    	dates =datetime.strftime(datetime.now(), "%Y-%m-%d")
    	th = str(datetime.strptime(dates,"%Y-%m-%d").year)
    	bl = str(datetime.strptime(dates,"%Y-%m-%d").month)
    	hr = str(datetime.strptime(dates,"%Y-%m-%d").day)
        for contract in self.read(cr, uid, ids, ['date_start', 'date_end'], context=context):
             if contract['date_start'] and contract['date_end'] and contract['date_start'] > contract['date_end']:
                 return False
        return True

    _constraints = [
        (_check_dates, 'Kesalahan! Mulai Kontrak Harus Lebih Kecil Dari Habis Kontrak / Kontrak Mulai Tidak Boleh Lebih Kecil Dari Tanggal Sekarang.', ['date_start', 'date_end'])
    ]
hr_contract()

class hr_employee_contract(osv.osv):
	_inherit = "hr.employee"

	_columns = {
		'link_warning1':fields.related('link_warning',type='many2one',
			relation='warning.schedule', string='link'),
		'link_warning' : fields.many2one('warning.schedule','link'),
		'status_contract' : fields.boolean('Status Kontrak',readonly=True),
		'no_contract' : fields.char('No Kontrak', readonly=True),
		'tanggal' : fields.date('Tanggal Kaladuarsa',readonly=True),
		'warning_schedule' :fields.many2one('warning.schedule',''),
		'warning_hari' : fields.integer('Habis Kontrak(Hari)'),
	}	
hr_employee_contract()


class hr_contract_sift(osv.osv):
    _name = "hr.contract.schedule"
    _description = "form untuk mengelompokan karyawan berdasarkan sift"

    _columns = {
        'name': fields.char('Kelompok Sift'),
        'sift_roling':fields.many2one('hr.sift.roling','Urutan Sift'),
        #'tetap': fields.boolean('Status Sift',help='Jika Di centang Maka Sift Akan Tetap')
    }

    def pindah_sift(self, cr, uid, ids, context=None):
        sift_obj = self.pool.get('hr.contract.schedule')
        sift_src = sift_obj.search(cr,uid,[])
        sift_brw = sift_obj.browse(cr,uid,sift_src)
        obj_rol = self.pool.get('hr.sift.roling')
        src_rol = obj_rol.search(cr,uid,[])
        brw_rol = obj_rol.browse(cr,uid,src_rol)
        for sf in sift_brw :
            sifts = sf.sift_roling.name + 1
            for sift in brw_rol :
                name = sift.name
                if sifts == name :
                    stfs = sift.id
                elif name == 1 :
                    stfs = sift.id
            sift_obj.write(cr, uid,[sf.id],{'sift_roling': stfs},context=context)
        return True

    def working_schedule(self,cr,uid,ids,context=None):
        con_obj = self.pool.get('hr.contract')
        con_src = con_obj.search(cr,uid,[('status','=',True)])
        con_brw = con_obj.browse(cr,uid,con_src)
        for contract in con_brw :
            sift = contract.kelompok_sift.sift_roling.schedule.id
            con_obj.write(cr,uid,[contract.id],{'working_hours': sift},context=context)
        return True


hr_contract_sift()

class sift_roling(osv.osv):
    _name = "hr.sift.roling"
    _description = "Perputaran Sift"
    _order_by = 'name'
    
    _columns = {
        'name': fields.integer('urutan Sift'),
        'schedule' : fields.many2one('resource.calendar','Schedule Sift')
    }
sift_roling()