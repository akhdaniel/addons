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

from openerp.osv import fields
from openerp.osv import osv
import time
import datetime
from openerp.tools.translate import _
from dateutil import parser

class mrp_production(osv.osv):
    _inherit = 'mrp.production'


    def _compute_planned_workcenter(self, cr, uid, ids, context=None, mini=False):
        res = super(mrp_production, self)._compute_planned_workcenter(cr, uid, ids, context={}, mini={})
        """ Update Scedule Date (date_planned)
            Misal dalam 6 atau 7 hari, workcenter (mesin) dapat digunakan dalam 2 shift per 1 hari
            maka diperkirakan MO atau WO dalam satu minggu kira2 12 atau 14 MO/WO 
        """
        date_planned = self.browse(cr, uid, ids, context=context).date_planned
        # date_planned = strptime(date_planned, '%Y-%m-%d %H:%M:%S')
        wps_id = self.browse(cr, uid, ids, context=context).wps_id
        mrp_id = self.browse(cr, uid, ids, context=context).id
       
        """ Cari Dahulu mrp_id - Terfilter wps_id """
        wps_id_list = self.search(cr, uid, [('wps_id','=',wps_id.id)]) #[466, 465, 467]
        wps_id_list.sort()
        # import pdb;pdb.set_trace() 
        # for wps in wps_id_list:
        #     index_n = wps_id_list.index(wps)
        #     if mrp_id == wps:
                
        #         """ Jika Shift = 2, 6 hari kerja, Maksimum WO = 12 Shift """
        #         if len(wps_id_list) <= 6:
        #             for wl in self.browse(cr, uid, ids, context=context).workcenter_lines:
        #                 wl.id
        #                 date_p = parser.parse(date_planned) +  datetime.timedelta(days=index_n)
        #                 self.pool.get('mrp.production.workcenter.line').write(cr, uid, [wl.id],  {
        #                 'date_planned': date_p.strftime('%Y-%m-%d %H:%M:%S'),
        #                 'date_planned_end': date_p.strftime('%Y-%m-%d %H:%M:%S')
        #             },context=context, update=False)



        return res
        
        # """ Computes planned and finished dates for work order.
        # @return: Calculated date
        # """
        # dt_end = datetime.now()
        # if context is None:
        #     context = {}
        # for po in self.browse(cr, uid, ids, context=context):
        #     dt_end = datetime.strptime(po.date_planned, '%Y-%m-%d %H:%M:%S')
        #     if not po.date_start:
        #         self.write(cr, uid, [po.id], {
        #             'date_start': po.date_planned
        #         }, context=context, update=False)
        #     old = None
        #     for wci in range(len(po.workcenter_lines)):
        #         wc  = po.workcenter_lines[wci]
        #         if (old is None) or (wc.sequence>old):
        #             dt = dt_end
        #         if context.get('__last_update'):
        #             del context['__last_update']
        #         if (wc.date_planned < dt.strftime('%Y-%m-%d %H:%M:%S')) or mini:

        #             self.pool.get('mrp.production.workcenter.line').write(cr, uid, [wc.id],  {
        #                 'date_planned': dt.strftime('%Y-%m-%d %H:%M:%S')
        #             }, context=context, update=False)
        #             i = self.pool.get('resource.calendar').interval_get(
        #                 cr,
        #                 uid,
        #                 #passing False makes resource_resource._schedule_hours run 1000 iterations doing nothing
        #                 wc.workcenter_id.calendar_id and wc.workcenter_id.calendar_id.id or None,
        #                 dt,
        #                 wc.hour or 0.0
        #             )
        #             import pdb;pdb.set_trace()       
        #             if i:
        #                 dt_end = max(dt_end, i[-1][1])
        #         else:
        #             dt_end = datetime.strptime(wc.date_planned_end, '%Y-%m-%d %H:%M:%S')

        #         old = wc.sequence or 0
        #     super(mrp_production, self).write(cr, uid, [po.id], {
        #         'date_finished': dt_end
        #     })
        # return dt_end

    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
