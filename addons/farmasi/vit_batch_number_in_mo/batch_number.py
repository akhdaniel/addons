# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import tools, SUPERUSER_ID
from openerp.addons.product import _common

class batch_number(osv.osv):
    _name = 'batch.number'

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['number'], context=context)
        res = []
        for record in reads:
            name= record['number']
            if record['number']:
                name = record['number']
            res.append((record['id'], name))
        return res

    def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if context is None:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('number','=',name)] + args, limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('number',operator,name)] + args, limit=limit, context=context)
        return self.name_get(cr, user, ids, context)

    def create(self, cr, uid, vals, context=None):
        year        = vals['year_id']
        short_year  = self.pool.get('batch.year').browse(cr,uid,year,context=context).name
        short_year0 = tuple(short_year)
        short_year1 = short_year0[2]+short_year0[3]#ambil 2 digit paling belakang dari tahun saja                           
        month       = vals['month']
        date         = vals['date']
        sequence    = vals['name']
        vals['number'] = short_year1+month+date+sequence

        return super(batch_number, self).create(cr, uid, vals, context=context)

    _columns = {
        'name'      : fields.char('Sequence',required=True),
        'number'    : fields.char('Number', readonly=True),
        'year_id'   : fields.many2one('batch.year',string="Year",required=True,ondelete='cascade'),
        'month'     : fields.selection([('A','January'),
                                        ('B','February'),
                                        ('C','March'),
                                        ('D','April'),
                                        ('E','May'),
                                        ('F','June'),
                                        ('G','July'),
                                        ('H','August'),
                                        ('J','September'),#ga pake i
                                        ('K','October'),
                                        ('L','November'),
                                        ('M','December')],required=True,string='Month'),
        'is_used'   : fields.boolean('Used'),
        'date'     : fields.selection([('1','1'),
                                        ('2','2'),
                                        ('3','3'),
                                        ('4','4'),
                                        ('5','5'),
                                        ('6','6'),
                                        ('7','7'),
                                        ('8','8'),
                                        ('9','9'),
                                        ('A','10'),
                                        ('B','11'),
                                        ('C','12'),
                                        ('D','13'),
                                        ('E','14'),
                                        ('F','15'),
                                        ('G','16'),
                                        ('H','17'),
                                        ('I','18'),
                                        ('J','19'),
                                        ('K','20'),
                                        ('L','21'),
                                        ('M','22'),
                                        ('N','23'),
                                        ('O','24'),
                                        ('P','25'),
                                        ('Q','26'),
                                        ('R','27'),
                                        ('S','28'),
                                        ('T','29'),
                                        ('U','30'),
                                        ('V','31'),
                                        ],required=True,string='Date')
    }

    _defaults = {  
        'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'batch.number'), 
                }

    _sql_constraints = [('number', 'unique(number)','Number must be unique !')]   


batch_number()



class batch_year(osv.osv):
    _name = 'batch.year'

    _columns = {
        'name'  : fields.char('Year',required=True,size=4),
    }
    
    _sql_constraints = [('name', 'unique(name)','Year must be unique !')] 

batch_year()