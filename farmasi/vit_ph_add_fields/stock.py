import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re




class stock_move(osv.osv):
    _name = "stock.move"
    _inherit = "stock.move"
    _columns = {

        'note_release': fields.char('Note Release'),
        
    }

class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _columns = {

       
        'release_date': fields.datetime('Release Date'),

    }


