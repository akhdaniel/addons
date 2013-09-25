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
