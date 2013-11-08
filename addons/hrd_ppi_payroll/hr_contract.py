from openerp.osv import fields, osv

class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'
    
    _columns = {
        'master_gaji_id':fields.many2one('hr.master_gaji', "incentive"),
        'makan':fields.related('master_gaji_id','makan',type='integer',relation='hr.master_gaji',string='Uang Makan',readonly=True),
        'transport':fields.related('master_gaji_id','transport',type='integer',relation='hr.master_gaji',string='Uang Transport',readonly=True),
        'jenis_lembur' : fields.selection([('incentive','Incentive'),('overtime','Overtime')], 'Jenis Lembur'),
    }
hr_contract()    
    
class master_gaji(osv.osv):
    _name="hr.master_gaji"
    
    _columns = {
        "name" : fields.selection([('1','1'),('2','2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9')],'Pilih Golongan'),
        "makan" :fields.integer("Uang Makan"),
        "transport" : fields.integer("Uang Transportasi"),
    }
    _sql_constraints = [('name_uniq', 'unique(name)','Kode status tidak boleh sama')]
    
    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None: custom_values = {}
        desc = html2plaintext(msg.get('body')) if msg.get('body') else ''
        defaults = {
            'name':  msg.get('subject') or _("No Subject"),
            'description': desc,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'user_id': False,
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(hr_applicant,self).message_new(cr, uid, msg, custom_values=defaults, context=context)
        
    def message_update(self, cr, uid, ids, msg, update_vals=None, context=None):
        """ Override mail_thread message_update that is called by the mailgateway
            through message_process.
            This method updates the document according to the email.
        """
        if isinstance(ids, (str, int, long)):
            ids = [ids]
        if update_vals is None:
            update_vals = {}

        update_vals.update({
            'description': msg.get('body'),
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
        })
        if msg.get('priority'):
            update_vals['priority'] = msg.get('priority')

        maps = {
            'cost': 'planned_cost',
            'revenue': 'planned_revenue',
            'probability': 'probability',
        }
        for line in msg.get('body', '').split('\n'):
            line = line.strip()
            res = tools.command_re.match(line)
            if res and maps.get(res.group(1).lower(), False):
                key = maps.get(res.group(1).lower())
                update_vals[key] = res.group(2).lower()

        return super(hr_applicant, self).message_update(cr, uid, ids, msg, update_vals=update_vals, context=context)
master_gaji()    

class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _inherit= 'hr.contract.type'
    
    _columns = {
        "jams1":fields.float('Kontribusi Karyawan (%)'),
        "jams2":fields.float('Kontribusi Perusahaan (%)'),
        "pajak":fields.float('Pajak (%)'),
        "reimburse_pengobatan":fields.integer('Pengobatan Tahunan',size=1,help='Digit dikalikan dengan gaji pokok karyawan'),
        "reimburse_perawatan":fields.integer('Perawatan Rumah Sakit',size=1,help='Digit dikalikan dengan gaji pokok karyawan'),
        "biaya_jabatan":fields.integer('Biaya Jabatan (%)',size=1),
        "max_biaya_jabatan":fields.float('Nominal Max (Rp)'),
        "tht":fields.float('Kontribusi Perusahaan (%)'),
        'ttht':fields.float('Kontribusi Karyawan (%)'),		
     } 
hr_contract_type()

class pkp(osv.osv):
    _name="hr.pkp"
    _rec_name="kode"
    
    _columns = {
        "kode":fields.char('Kode',size=5,required=True),
        "nominal_min" : fields.float("Nominal Min",required=True),
        "nominal_max" : fields.float("Nominal Max",required=True),
        "pajak":fields.integer('Pajak (%)',size=2,required=True),
    }
    '''
    def _check_nominal(self, cr, uid, ids):
        for nominal in self.browse(cr, uid, ids):
            nominal_id = self.search(cr, uid, [('nominal_min', '>', nominal.nominal_max), ('nominal_max', '<', nominal.nominal_min)])
            if nominal_id:
                return False
        return True      
            
    _constraints = [
        (_check_nominal, 'range max tidak boleh lebih kecil dari range min!', ['nominal_min','nominal_max']),
                    ]    
    '''   
    _sql_constraints = [('kode_uniq', 'unique(kode)','Kode tidak boleh sama!')]
    _sql_constraints = [('pajak_uniq', 'unique(pajak)','Besaran % pajak tidak boleh sama!')]
           
pkp() 

class ptkp(osv.osv):
    _name="hr.ptkp"
    _rec_name="kode"
    
    _columns = {
        "kode":fields.char('Kode',size=5,required=True),
        "nominal_bulan" : fields.float("Nominal Perbulan",required=True),
        "nominal_tahun" : fields.float("Nominal Pertahun"),
    }
    def onchange_kali(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_tahun_': (nominal_bulan ) * 12}
        return {'value': v}

    def onchange_bagi(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_bulan': (nominal_tahun ) /12}
        return {'value': v}
        
    _sql_constraints = [('kode_uniq', 'unique(kode)','Kode tidak boleh sama!')]
           
ptkp()
