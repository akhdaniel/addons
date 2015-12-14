# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp.osv import fields, osv
from openerp.tools.translate import _

class transfer_vehicle(osv.TransientModel):
    _name = "transfer.vehicle"
    _description = "transfer vehicle"
    _columns = {
        'name':fields.many2one('student.student','Student Name', readonly=True),
        'participation_id':fields.many2one('transport.participant','Participation', required=True),
        'root_id':fields.many2one('student.transport','Root', required=True),
        'old_vehicle_id':fields.many2one('transport.vehicle','Old Vehicle No', required=True),
        'new_vehicle_id':fields.many2one('transport.vehicle','New Vehicle No', required=True),  
    }

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        result = super(transfer_vehicle, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            student = self.pool.get('student.student').browse(cr, uid, context.get('active_id'), context=context)
            if 'name' in fields:
                result.update({'name': student.id})
        return result
    
    def onchange_participation_id(self, cr, uid, ids, transport, context=None):
        if not transport:
            return {}
        transport_obj = self.pool.get('transport.participant').browse(cr, uid, transport, context)
        return {'value': {'root_id': transport_obj.transport_id.id, 'old_vehicle_id': transport_obj.vehicle_id.id}}

    def vehicle_transfer(self, cr, uid, ids, context=None):
        stu_prt_obj = self.pool.get('transport.participant')
        vehi_obj = self.pool.get('transport.vehicle')
        for new_data in self.browse(cr, uid, ids, context=context):
            vehi_data = vehi_obj.browse(cr, uid, new_data.old_vehicle_id.id, context=context)
            vehi_new_data = vehi_obj.browse(cr, uid, new_data.new_vehicle_id.id, context=context)
            #check for transfer in same vehicle
            if new_data.old_vehicle_id.id == new_data.new_vehicle_id.id:
                raise osv.except_osv(_('Error !'),_('Sorry you can not transfer in same vehicle.'))
            # First Check Is there vacancy or not
            person = int(vehi_data.participant) + 1
            if vehi_data.capacity < person:
                raise osv.except_osv(_('Error !'),_('There is No More vacancy on this vehicle.'))
            #remove entry of participant in old vehicle.
            participants = [prt_id.id for prt_id in vehi_data.vehi_participants_ids]
            participants.remove(new_data.participation_id.id)
            vehi_obj.write(cr, uid, new_data.old_vehicle_id.id, {'vehi_participants_ids':[(6,0,participants)]}, context=context)
            #entry of participant in new vehicle.
            participants = [prt_id.id for prt_id in vehi_new_data.vehi_participants_ids]
            participants.append(new_data.participation_id.id)
            vehi_obj.write(cr, uid, new_data.new_vehicle_id.id, {'vehi_participants_ids':[(6,0,participants)]}, context=context)
            stu_prt_obj.write(cr, uid, new_data.participation_id.id, {'vehicle_id': new_data.new_vehicle_id.id,}, context=context)  
        return {}

transfer_vehicle()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
