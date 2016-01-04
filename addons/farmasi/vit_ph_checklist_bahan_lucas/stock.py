from datetime import date, datetime
from dateutil import relativedelta
import json
import time

from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement
import logging




class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"

    def _get_default_checklist(self, cr, uid, context=None):
        if context is None:
            context = {}
        checklist_value_ids = []
        ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        master_checklist_obj   = self.pool.get('vit_ph_checklist_bahan_lucas.master_checklist')
        master_ids   = master_checklist_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])
   
        # import pdb;pdb.set_trace()
        for master_id in master_ids:
            checklist_value_ids.append((0,0,{'master_checklist_id':master_id}))
        return checklist_value_ids

    def _get_default_advance_checklist(self, cr, uid, context=None):
        if context is None:
            context = {}
        checklist_value_ids = []
        ir_model_id   = self.pool.get('ir.model').search(cr,uid,[('model','=',self._name)])
        master_advance_checklist_obj   = self.pool.get('vit_ph_checklist_bahan_lucas.master_advance_checklist')
        master_ids   = master_advance_checklist_obj.search(cr, uid,[('appeareance','=',ir_model_id[0])])
        for master_id in master_ids:
            checklist_value_ids.append((0,0,{'master_checklist_id':master_id}))
        return checklist_value_ids

  

    _columns = {
        'stock_checklist_ids':fields.one2many('vit_ph_checklist_bahan_lucas.stock_checklist','stock_move_id','Stock Checklist'), 
        'stock_advance_checklist_ids':fields.one2many('vit_ph_checklist_bahan_lucas.stock_advance_checklist','stock_move_id','Stock Advance Checklist'), 
    }

    _defaults = {
        'stock_checklist_ids' : _get_default_checklist,
        'stock_advance_checklist_ids' : _get_default_advance_checklist,
    }
    
class stock_checklist(osv.osv):
    _name = "vit_ph_checklist_bahan_lucas.stock_checklist"
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock Move Reference',required=True, ondelete='cascade', select=True),
        'master_checklist_id': fields.many2one('vit_ph_checklist_bahan_lucas.master_checklist', 'Parameter',required=True),
        'sesuai_ada' : fields.boolean('Sesuai/ada'),
        'tidak_sesuai' : fields.boolean('Tidak Sesuai/Tidak ada'),
        'note' : fields.char('Keterangan'),
    }

class stock_advance_checklist(osv.osv):
    _name = "vit_ph_checklist_bahan_lucas.stock_advance_checklist"
    _columns = {
        'stock_move_id': fields.many2one('stock.move', 'Stock Move Reference',required=True, ondelete='cascade', select=True),
        'master_checklist_id': fields.many2one('vit_ph_checklist_bahan_lucas.master_advance_checklist', 'Parameter',required=True),
        'sesuai_ada' : fields.boolean('Sesuai/ada'),
        'tidak_sesuai' : fields.boolean('Tidak Sesuai/Tidak ada'),
        'note' : fields.char('Keterangan'),
    }


