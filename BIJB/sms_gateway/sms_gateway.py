from openerp.osv import fields, osv
from datetime import datetime
from openerp.tools.translate import _

class calendar_event(osv.osv):
    _name = 'calendar.event'
    _inherit = 'calendar.event'

    def do_sendsms(self, cr, uid, ids, context=None):
        import requests
        for event in self.browse(cr, uid, ids, context):
            import pdb;pdb.set_trace()
            # current_user = self.pool['hr.applicant'].browse(cr, uid, uid, context=context)
            for att in event.applicant_ids:
                date = date(event.start_datetime)
                mobile = att.partner_phone
                import pdb;
                pdb.set_trace();
                if mobile is not None:
                    payload = {'username': 'tig', 'password': 'p4ssw0rd','hp':mobile,'message':'Salam, Kami mengundang Sdr/i '+event.applicant_ids.partner_name+' mengikuti Tes tulis u/ posisi '+event.applicant_ids.job_id.name+' pada : '+event.start_datetime+' tempat : '+event.location+'. Mohon konfirmasi kehadiran dengan menghubungi CP : Ridwan 083822761725. Terimakasih'}
                    r = requests.get("http://103.16.199.187/masking/send.php", params=payload)
        return
        
calendar_event()