# -*- coding: utf-8 -*-
from datetime import date
from openerp.osv import fields, osv

class hr_xport_xcel(osv.osv_memory):
    _name = 'hr.xport.xcel'

    _columns = {
        'date_from':fields.date('Period',help='Date start periode'),
        'date_to':fields.date('To',help='Date end periode'),
        'trans_date':fields.date('Transfer Date'),
    }

    _defaults = {
    	'trans_date' : date.today().strftime('%Y-%m-%d'),
    }