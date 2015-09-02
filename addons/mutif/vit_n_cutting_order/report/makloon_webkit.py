# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 Camptocamp Austria (<http://www.camptocamp.at>)
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
from report import report_sxw
from osv import osv

class makloon_webkit(report_sxw.rml_parse):

    def get_lines(self, user,objects):
        lines=[]
        for obj in objects:
            if user.id==obj.user_id.id:
                lines.append(obj)
        return lines
        
    def __init__(self, cr, uid, name, context):
        super(makloon_webkit, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'cr':cr,
            'uid': uid,
        })
        
report_sxw.report_sxw('report.makloon_webkit',
                       'vit.makloon.order', 
                       'addons/vit_n_cutting_order/report/makloon_webkit.mako',
                       parser=makloon_webkit)
