from datetime import datetime
from datetime import date
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from time import strptime
from time import strftime
from openerp.tools.translate import _

class calendar_meeting(osv.osv):
    _name = "calendar.event"
    _inherit = "calendar.event"

    def do_sendsms(self, cr, uid, ids, context=None):
        import requests
        for event in self.browse(cr, uid, ids, context):
            # current_user = self.pool['hr.applicant'].browse(cr, uid, uid, context=context)
            for att in event.applicant_ids:
                #date = date(event.start_datetime)
                mobile = att.partner_phone
                date = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S")
                date_y = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S").year
                date_m = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S").month
                date_d = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S").day
                date_h = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S").hour + 7
                date_mm = datetime.strptime(event.start_datetime,"%Y-%m-%d %H:%M:%S").minute
                dates =str(date_y) + "-" + str(date_m) + '-' + str(date_d)
                jam =str(date_h) + ":" + str(date_mm) + ":00"
                if event.location == False :
                    raise osv.except_osv(_('Peringatan!'),_('Lokasi Interview Tidak Boleh Kosong'))
                if mobile != False:
                    payload = {'username': 'bijb', 'password': 'b1jbBerjaya','hp':mobile,'message':'Salam, Kami mengundang Sdr/i '+att.partner_name+' mengikuti Tes tulis u/ posisi '+att.job_id.name+' pada tanggal: '+dates+' Jam '+jam+' tempat : '+event.location+'. Mohon konfirmasi kehadiran dengan menghubungi CP : Ridwan 083822761725. Terimakasih'}
                    r = requests.get("http://103.16.199.187/masking/send.php", params=payload)
        return

    _columns = {
        'applicant_ids' : fields.many2many("hr.applicant","meeting_rel","applicant_id","meeting_id","Nama Pelamar"),
    }
calendar_meeting()

class hr_applicant(osv.osv):
    _name='hr.applicant'
    _inherit='hr.applicant'
    
    _columns = {
    	#'applicant_id':fields.many2one('calendar.event'),
    	"meeting_ids" : fields.many2many("calendar.event","meeting_rel","meeting_id","applicant_id",string="Jadwal Interview",readonly=True, domain="[('status','=',True)]"),
    }