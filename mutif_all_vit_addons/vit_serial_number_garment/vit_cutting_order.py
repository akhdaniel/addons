from osv import osv, fields
import platform
import os
import csv
import logging
import time
import openerp.addons.decimal_precision as dp
from openerp.tools.amount_to_text_en import amount_to_text
from openerp.addons.vit_upi_uang_persediaan import terbilang_func
import datetime 

_logger = logging.getLogger(__name__)


class vit_cutting_order(osv.osv):
	_inherit = "vit.cutting.order"


	_columns = {
		'is_used_handtag': fields.boolean('Is Used HangTag'),
			}

	_defaults = {
		'is_used_handtag': False, 
	}		

vit_cutting_order()


class vit_makloon_order(osv.osv):
	_inherit = "vit.makloon.order"

	_columns = {
		'is_used_handtag': fields.boolean('Is Used HangTag'),
			}	

	_defaults = {
		'is_used_handtag': False, 
	}			

vit_makloon_order()	