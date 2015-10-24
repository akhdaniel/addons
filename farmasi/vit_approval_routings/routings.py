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


class mrp_routing_workcenter(osv.osv):

    _inherit = 'mrp.routing.workcenter'

    _columns={
        'waiting_previous_wo_to_start': fields.boolean('Waiting Finished Previous WO to Start', 
            help="Centang jika WO ini hanya bisa start ketika WO sebelumnya finish"),
        'sampling' : fields.boolean('Sampling',help="Centang jika untuk pengambilan sample"),
        'waiting_approval_to_start_next_wo' : fields.boolean('Waiting Approval to Start Next WO',
            help="Centang jika WO selanjutnya bisa lanjut ketika WO in sudah di approve"),
    }

    _defaults = {
        'sampling' : False
    }

class mrp_production_workcenter_line(osv.osv):
    _inherit = 'mrp.production.workcenter.line'

    def cek_previous_wo_finished(self, cr, uid, sequence, routing_id, workcenter_id, context=None):
        result             = False
        #import pdb;pdb.set_trace()
        detail_routing_obj = self.pool.get('mrp.routing.workcenter')
        routing_workorders = detail_routing_obj.search(cr,uid,[('sequence','=',sequence),
                                                                ('routing_id','=',routing_id),
                                                                ('workcenter_id','=',workcenter_id)],
                                                                context=context)
        if routing_workorders :
            previous_wo_finished = detail_routing_obj.browse(cr,uid,routing_workorders[0]).waiting_previous_wo_to_start
            result               = previous_wo_finished
        return result

    def cek_sample(self, cr, uid, sequence, routing_id, workcenter_id, context=None):
        result             = False
        #import pdb;pdb.set_trace()
        detail_routing_obj = self.pool.get('mrp.routing.workcenter')
        routing_workorders = detail_routing_obj.search(cr,uid,[('sequence','=',sequence),
                                                                ('routing_id','=',routing_id),
                                                                ('workcenter_id','=',workcenter_id)],
                                                                context=context)
        if routing_workorders :
            sample = detail_routing_obj.browse(cr,uid,routing_workorders[0]).sampling
            result = sample
        return result

    def _get_previous_wo_finished(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result      = {}
        previous    = True
        for obj in self.browse(cr,uid,ids,context=context):            
            routing       = obj.production_id.routing_id
            mo_id         = obj.production_id.id
            workcenter_id = obj.workcenter_id.id
            if routing :
                routing_id = routing.id
                if routing_id :
                    #cek dahulu di routing apakah WO ini waiting_previous_wo_to_start nya di centang
                    previous_wo_finished = self.cek_previous_wo_finished(cr, uid, obj.sequence, routing_id, workcenter_id,context=context)
                    if previous_wo_finished :
                        routing_workorders   = self.search(cr,uid,[('production_id','=',mo_id),('sequence','<',obj.sequence)],context=context)
                        if routing_workorders :
                            #cari sequence paling dekat di bawah sequence work center ini
                            cr.execute("""SELECT sequence, COUNT(*) AS count
                                        FROM mrp_routing_workcenter 
                                        WHERE routing_id = """+ str(routing_id) +""" 
                                        AND sequence < """+ str(obj.sequence) +"""
                                        AND (sampling IS NULL OR sampling = False)
                                        GROUP BY sequence 
                                        HAVING COUNT(*) > 0""")           
                            sequence         = cr.fetchall()
                            #sort dulu dari sequence yang terbesar
                            biggest_sequence = sorted(sequence,reverse=True)
                            #angka sequence yang paling dekat
                            seq              = biggest_sequence[0][0]                  
                            #jumlah sequence terbesar yang sama
                            total_sequence   = int(biggest_sequence[0][1])
                            
                            previous_wo      = len(routing_workorders)
                            previous_count   = 0
                            for wo in routing_workorders :
                                obj_state = self.browse(cr,uid,wo).state
                                workorders_sec = self.browse(cr,uid,wo).sequence
                                #cek dahulu apakah WO in sampling atau bukan
                                sample = self.cek_sample(cr, uid, obj.sequence, routing_id, workcenter_id,context=context)
                                #jika merupakan sampling dan sequence nya sama
                                if not sample and workorders_sec == seq :
                                    #jika masih ada state sebelumnya yang belum finish langsung di false kan sajah
                                    if obj_state != 'done' :
                                        result[obj.id] = False
                                        return result
                                #jika bukan merupakan sampling dan sequence nya sama        
                                elif sample and workorders_sec == seq :
                                    previous_count += 1
                                    #jika sudah ada state sebelumnya yang running/start(inprogress) langsung di true kan sajah
                                    #berlaku jika proses sebelumnya terdapat sequence yang sama maka akan dilihat satu sequence saja
                                    #tidak dilihat keseluruhan sequence yang sama tersebut
                                    if obj_state == 'startworking' :
                                        result[obj.id] = True
                                        return result
                                    else : 
                                        result[obj.id] = False
                                        return result                                                                      
            result[obj.id] = previous
        return result 


    _columns = {
        'previous_wo_finished': fields.function(_get_previous_wo_finished, type="boolean",string='Previous WO Finished'),
        #'sampling'            : fields.function(_get_sample,type="boolean",string='Sampling'),


    }    