from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class netpro_syntech(osv.osv):
    _name = 'netpro.syntech'

    _columns = {
    	'CARD_NUMB' : fields.char('Card Number', select=1),
        'NO_POLICY' : fields.char('NO POLICY', select=1),
    	'BIRTH_DATE' : fields.date('Birth Date', select=1),
    	'PAT_NAME' : fields.char('Pat Name', select=1),
    	'PAT_NAME1' : fields.char('Pat Name1', select=1),
    	'PAT_SEX' : fields.char('Pat Sex', select=1),
    	'PAT_ADD1' : fields.text('Pat Add1'),
    	'PAT_ADD2' : fields.text('Pat Add2'),
    	'PAT_ADD3' : fields.text('Pat Add3'),
    	'PAT_ADD4' : fields.text('Pat Add4'),
    	'CITY' : fields.char('City'),
    	'ZIP_CODE' : fields.char('ZIP Code'),
    	'PAT_TELP' : fields.char('Pat Telp'),
    	'START_DATE' : fields.date('Start Date', select=1),
    	'XPIRY_DATE' : fields.date('Xpiry Date', select=1),
    	'COMP_NAME' : fields.char('Comp Name', select=1),
    	'COMP_TEL1' : fields.char('Comp Tel1'),
    	'COMP_FAX1' : fields.char('Comp Fax1'),
    	'CARD_NO' : fields.char('Card No', select=1),
    	'UPD_CODE' : fields.selection([('D','D'),('N','N'),('R','R'),('L','L'),('U','U'),('T','T')], 'Update Code', select=1),
    	'SERV_CODE' : fields.char('Service Code', select=1),
    	'SEQ_NO' : fields.integer('Sequence No.', select=1),
    	'UPD_DATE' : fields.date('Update Date', select=1),
    	'R_AND_B' : fields.float('Room And Board', select=1),
    	'MAX_LIMIT' : fields.char('MAX. LIMIT', select=1),
    	'LAST_BAL' : fields.char('LAST BALANCE', select=1),
    	'INDICATOR' : fields.char('INDICATOR'),
    	'CLINIC1' : fields.char('CLINIC1'),
    	'CLINIC2' : fields.char('CLINIC2'),
    	'PLAN_X' : fields.char('PLAN_X', select=1),
    	'CLASS' : fields.char('CLASS', select=1),
    	'RMKS1' : fields.text('RMKS1'),
    	'RMKS2' : fields.text('RMKS2'),
    	'RMKS3' : fields.text('RMKS3'),
        'is_processed' : fields.boolean('Is Processed?'),
    }

    _defaults = {
        'is_processed' : False,
    }

    def process_convert_syntech(self, cr, uid, ids, context=None):
        syntech_obj = self.pool.get('netpro.syntech')
        
        # SEDOT DATA FROM SYNTECH
        if(syntech_obj):
            syntech_ids = syntech_obj.search(cr,uid,[('is_processed', '=', False)])
            if syntech_ids:
                syntech_data = syntech_obj.browse(cr, uid, syntech_ids, context=context)
                inc = 1
                for syntech in syntech_data:

                    ####################################
                    # collect data from syntech object #
                    ####################################
                    member_data = {
                        'card_no' : syntech.CARD_NUMB,
                        'date_of_birth' : syntech.BIRTH_DATE,
                        'name' : syntech.PAT_NAME,
                        'gender_id' : self.pool.get('netpro.gender').search(cr,uid,[('name','=',syntech.PAT_SEX)])[0],
                        'street' : syntech.PAT_ADD1,
                        'zip' : syntech.ZIP_CODE,
                        'phone' : syntech.PAT_TELP,
                        'insurance_period_start' : syntech.START_DATE,
                        'insurance_period_end' : syntech.XPIRY_DATE,
                        'upd_code' : syntech.UPD_CODE,
                        'upd_date' : syntech.UPD_DATE,
                        'remarks' : 'Syntech Data ' + str(inc),
                        'parent_id' : False,
                        'member_no' : False,
                    }

                    #################################################
                    # insert record to member object and activating #
                    #################################################
                    member_obj = self.pool.get('netpro.member')
                    member_syntech_id = member_obj.create(cr, uid, member_data, context)
                    member_syntech_id.action_confirm()

                    ###########################################
                    # add increment number for member remarks #
                    ###########################################
                    inc += 1