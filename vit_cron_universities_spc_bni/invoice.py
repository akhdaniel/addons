import pymysql.cursors
from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import logging
from openerp.tools.translate import _
from openerp import netsvc
_logger = logging.getLogger(__name__)


class spc2(object):
    
    connection = False

    def connect(self, host='localhost', user='root', passwd='', db=''):
        self.connection = pymysql.connect(host=host,
                             user=user,
                             password=passwd,
                             db=db,
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)



    def select_biller_tagihan(self, data):
        with self.connection.cursor() as cursor:
            sql = "select id_record_tagihan from tagihan where id_record_tagihan = %s"
            hsl = cursor.execute(sql, (data,))
        #self.connection.commit()
        return hsl


####################################################################################
# on validate create biller taghian
# on cancel delete biller tagihan
####################################################################################
class account_invoice(osv.osv):
    _name       = "account.invoice"
    _inherit    = "account.invoice"

    spc_hostname = False
    spc_username = False
    spc_password = False
    spc_dbname   = False

    ####################################################################################
    # get parameters for spc connections
    ####################################################################################
    def get_params(self, cr, uid, context=None):
        self.spc_hostname = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.hostname')
        self.spc_username = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.username')
        self.spc_password = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.password')
        self.spc_dbname   = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.dbname')

    ####################################################################################################
    # Cron Job untuk validasi invoice otomatis jika gagal insert ke spc
    ####################################################################################################
    def cron_validate_invoice_spc(self, cr, uid, ids=None,context=None):
        
        inv_to_validate = self.search(cr,uid,[('state','=','open'),('number','!=',False),('name','=',False)])
        if inv_to_validate :
            for inv in inv_to_validate :
                invs = self.browse(cr,uid,inv)
                if invs.partner_id.status_mahasiswa in ('calon','Mahasiswa'):
                    spc = spc2()
                    self.get_params(cr, uid, context=context)
                    spc.connect(host=self.spc_hostname, user=self.spc_username, passwd=self.spc_password, db=self.spc_dbname)
                    tagihan_exist = spc.select_biller_tagihan(invs.number)
                    from openerp import workflow
                    if not tagihan_exist :
                        #import pdb;pdb.set_trace()
                        workflow.trg_validate(uid, 'account.invoice', invs.id, 'invoice_cancel', cr)
                        _logger.info(" invoice cancelled number : %s" % (invs.number) )
                        cr.commit()
                        self.action_cancel_draft(cr,uid,invs.id)
                        cr.commit()
                        workflow.trg_validate(uid, 'account.invoice', invs.id, 'invoice_open', cr)
                        _logger.info(" invoice second validated number : %s" % (invs.number) )
                        cr.commit()
                        
        return True   