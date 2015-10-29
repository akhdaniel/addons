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
    	'CARD_NUMB' : fields.char('Card Number'),
    	'BIRTH_DATE' : fields.date('Birth Date'),
    	'PAT_NAME' : fields.char('Pat Name'),
    	'PAT_NAME1' : fields.char('Pat Name1'),
    	'PAT_SEX' : fields.char('Pat Sex'),
    	'PAT_ADD1' : fields.text('Pat Add1'),
    	'PAT_ADD2' : fields.text('Pat Add2'),
    	'PAT_ADD3' : fields.text('Pat Add3'),
    	'PAT_ADD4' : fields.text('Pat Add4'),
    	'CITY' : fields.char('City'),
    	'ZIP_CODE' : fields.char('ZIP Code'),
    	'PAT_TELP' : fields.char('Pat Telp'),
    	'START_DATE' : fields.date('Start Date'),
    	'XPIRY_DATE' : fields.date('Xpiry Date'),
    	'COMP_NAME' : fields.char('Comp Name'),
    	'COMP_TEL1' : fields.char('Comp Tel1'),
    	'COMP_FAX1' : fields.char('Comp Fax1'),
    	'CARD_NO' : fields.char('Card No'),
    	'UPD_CODE' : fields.selection([('D','D'),('N','N'),('R','R'),('L','L'),('U','U'),('T','T')], 'Update Code'),
    	'SERV_CODE' : fields.char('Service Code'),
    	'SEQ_NO' : fields.integer('Sequence No.'),
    	'UPD_DATE' : fields.date('Update Date'),
    	'R_AND_B' : fields.float('Room And Board'),
    	'MAX_LIMIT' : fields.char('MAX. LIMIT'),
    	'LAST_BAL' : fields.char('LAST BALANCE'),
    	'INDICATOR' : fields.char('INDICATOR'),
    	'CLINIC1' : fields.char('CLINIC1'),
    	'CLINIC2' : fields.char('CLINIC2'),
    	'PLAN_X' : fields.char('PLAN_X'),
    	'CLASS' : fields.char('CLASS'),
    	'RMKS1' : fields.text('RMKS1'),
    	'RMKS2' : fields.text('RMKS2'),
    	'RMKS3' : fields.text('RMKS3'),
    }