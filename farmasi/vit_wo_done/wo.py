from openerp.osv import fields
from openerp.osv import osv
import time
from datetime import datetime
from openerp.tools.translate import _

import logging
_logger = logging.getLogger(__name__)


class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def modify_production_order_state(self, cr, uid, ids, action):
        """ Modifies production order state if work order state is changed.
        @param action: Action to perform.
        @return: Nothing
        """
        prod_obj_pool = self.pool.get('mrp.production')
        oper_obj = self.browse(cr, uid, ids)[0]
        prod_obj = oper_obj.production_id

        _logger.warning("action=%s" % action)
        _logger.warning("mo state=%s" % prod_obj.state)

        if action == 'start':
            if prod_obj.state =='confirmed':

                _logger.warning("force_production" )
                prod_obj_pool.force_production(cr, uid, [prod_obj.id])

                _logger.warning("signal_workflow button_produce" )
                prod_obj_pool.signal_workflow(cr, uid, [prod_obj.id], 'button_produce')

            elif prod_obj.state =='ready':
                _logger.warning("signal_workflow button_produce" )
                prod_obj_pool.signal_workflow(cr, uid, [prod_obj.id], 'button_produce')

            elif prod_obj.state =='in_production':
                _logger.warning("in_production skip" )
                return

            else:
                raise osv.except_osv(_('Error!'),_('Manufacturing order cannot be started in state "%s"!') % (prod_obj.state,))
        else:
            _logger.warning("action_produce: consume_produce" )
            _logger.warning("signal_workflow: button_produce_done" )
            _logger.warning("skipped" )
            return 
            
            open_count = self.search_count(cr,uid,[('production_id','=',prod_obj.id), ('state', '!=', 'done')])
            flag = not bool(open_count)
            if flag:
                for production in prod_obj_pool.browse(cr, uid, [prod_obj.id], context= None):
                    if production.move_lines or production.move_created_ids:
                        prod_obj_pool.action_produce(cr,uid, production.id, production.product_qty, 'consume_produce', context = None)
                prod_obj_pool.signal_workflow(cr, uid, [oper_obj.production_id.id], 'button_produce_done')
        return