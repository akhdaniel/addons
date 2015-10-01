from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import time
import logging
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT
_logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import datetime
import sets


class stock_location(osv.osv):
    _inherit = 'stock.location'

    _columns={
    	'is_gudang_bahan_baku' 	: fields.boolean('Gudang Bahan Baku'),
    	'is_gudang_karantina'	: fields.boolean('Gudang Karantina'),
    }


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns={
    	'alert_date' 	: fields.date('Retest Date'),
    }

    ####################################################################################################
    # Cron Job untuk generate internal move otomatis, sesuai tanggal retest date pada product
    # jika ada tanggal yang sesuai maka akan tergenerate int move atas product-prodduct tsb
    ####################################################################################################
    def cron_product_retest(self, cr, uid, ids=None,context=None):

        location_obj    = self.pool.get('stock.location')
        move_obj        = self.pool.get('stock.move')
        picking_obj     = self.pool.get('stock.picking')
        product_obj     = self.pool.get('product.template')
        quant_obj       = self.pool.get('stock.quant')
        #import pdb;pdb.set_trace()
        product_retest_date = self.search(cr,uid,[('alert_date','=',time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[:10])],context=context)
        if product_retest_date :
            picking_id = picking_obj.create(cr,uid,{'origin':'Cron Job '+ time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)[:10],'picking_type_id'   : 8,}) # id 3 == internal transfer
            for lot in self.browse(cr,uid,product_retest_date):
                if lot.product_id.type != 'service':
                    loc_bb = location_obj.search(cr,uid,[('is_gudang_bahan_baku','=',True)])
                    if not loc_bb :
                        raise osv.except_osv(_('Error !'),_("Tidak ada gudang yang di set sebagai gudang bahan baku !") )
                    if len(loc_bb) > 1 :
                        raise osv.except_osv(_('Duplicate Location !'),_("Terdapat %s gudang yang di set gudang bahan baku !")%(len(loc_bb)) )
                    else :
                        loc_karantina = location_obj.search(cr,uid,[('is_gudang_karantina','=',True)])
                        if not loc_karantina :
                            raise osv.except_osv(_('Error !'),_("Tidak ada gudang yang di set sebagai gudang karantina bahan baku !") )
                        if len(loc_karantina) > 1 :
                            raise osv.except_osv(_('Duplicate Location !'),_("Terdapat %s gudang yang di set gudang karantina bahan baku !")%(len(loc_karantina)) )                        
                        
                        else :

                            location_id = location_obj.browse(cr,uid,loc_bb[0]).id 
                            location_dest_id = location_obj.browse(cr,uid,loc_karantina[0]).id 

                            cr.execute ('select sum(qty) from stock_quant \
                                where location_id = %s and lot_id = %s',(location_id,lot.id))
                            hasil	= cr.fetchone()
                            if hasil :
	                            total 	= hasil[0]
	                            move_obj.create(cr,uid,{'picking_id'        : picking_id,
	                                                    'product_id'        : lot.product_id.id,
	                                                    'product_uom_qty'   : total,
	                                                    'product_uom'       : lot.product_id.uom_id.id,
	                                                    'name'              : lot.product_id.name,
	                                                    'location_id'       : location_id,
	                                                    'location_dest_id'  : location_dest_id,
	                                })

        return True
