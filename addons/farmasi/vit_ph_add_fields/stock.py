import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
from openerp import api
import os
import csv
import re




class stock_picking(osv.osv):
    _name = "stock.picking"
    _inherit = "stock.picking"
    _description = "Picking List"


    _columns = {

        'note_release': fields.char('Note Release'),


    }


