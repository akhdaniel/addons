# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import fields, osv
import time
from openerp import netsvc
import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _


class hotel_reservation(osv.Model):
    _inherit = "hotel.reservation"

    _columns = {
        'folio_id2': fields.many2one('hotel.folio','Folio ID',readonly=True,),
        'reservation_line':fields.one2many('hotel_reservation.line', 'line_id', readonly=True, states={'draft':[('readonly', False)]},string='Reservation Line', help='Hotel room reservation details. '),
        }

    def confirmed_reservation(self, cr, uid, ids, context=None):
        reservation_line_obj = self.pool.get('hotel.room.reservation.line')
        for reservation in self.browse(cr, uid, ids, context=context):
            cr.execute("select count(*) from hotel_reservation as hr " \
                        "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                        "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                        "where (checkin,checkout) overlaps ( timestamp %s , timestamp %s ) " \
                        "and hr.id <> cast(%s as integer) " \
                        "and hr.state = 'confirm' " \
                        "and hrlrr.hotel_reservation_line_id in (" \
                        "select hrlrr.hotel_reservation_line_id from hotel_reservation as hr " \
                        "inner join hotel_reservation_line as hrl on hrl.line_id = hr.id " \
                        "inner join hotel_reservation_line_room_rel as hrlrr on hrlrr.room_id = hrl.id " \
                        "where hr.id = cast(%s as integer) )" \
                        , (reservation.checkin, reservation.checkout, str(reservation.id), str(reservation.id)))
            res = cr.fetchone()
            roomcount = res and res[0] or 0.0
            if roomcount:
                raise osv.except_osv(_('Warning'), _('You tried to confirm reservation with room those already reserved in this reservation period'))
            #protek jika tidak isi ruangan yg di booking    
            if not reservation.reservation_line :
                raise osv.except_osv(_('Error!'), _('Reservation Line is Empty!'))   
            else:
                self.write(cr, uid, ids, {'state':'confirm'}, context=context)
                for line_id in reservation.reservation_line:
                    line_id = line_id.reserve
                    for room_id in line_id:
                        vals = {
                            'room_id': room_id.id,
                            'check_in': reservation.checkin,
                            'check_out': reservation.checkout,
                            'state': 'assigned',
                            'reservation_id': reservation.id,
                        }
                        reservation_line_obj.create(cr, uid, vals, context=context)
        return True

    #tambah fungsi cancel
    def cancel_reservation(self, cr, uid, ids, context=None):
        reservation_line_obj = self.pool.get('hotel.room.reservation.line')
        #import pdb;pdb.set_trace()
        for reservation in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, ids, {'state':'cancel'}, context=context)
            for line_id in reservation.reservation_line:
                line_id = line_id.reserve
                for room_id in line_id:
                    #hapus data hotel.room.reservation.line yg telah di confirm sebelumnya
                    rev_id = reservation_line_obj.search(cr,uid,[('reservation_id','=',reservation.id)])
                    reservation_line_obj.unlink(cr, uid, rev_id, context=context)
        return True

    def _create_folio(self, cr, uid, ids, context=None):
        hotel_folio_obj = self.pool.get('hotel.folio')
        room_obj = self.pool.get('hotel.room')
        for reservation in self.browse(cr, uid, ids, context=context):
            folio_lines = []
            checkin_date, checkout_date = reservation['checkin'], reservation['checkout']
            if not checkin_date < checkout_date:
                raise osv.except_osv(_('Error'), _('Invalid values in reservation.\nCheckout date should be greater than the Checkin date.'))
            duration_vals = hotel_folio_obj.onchange_dates(cr, uid, [], checkin_date=checkin_date, checkout_date=checkout_date, duration=False)
            duration = duration_vals.get('value', False) and duration_vals['value'].get('duration') or 0.0
            folio_vals = {
                'date_order':reservation.date_order,
                'warehouse_id':reservation.warehouse_id.id,
                'partner_id':reservation.partner_id.id,
                'pricelist_id':reservation.pricelist_id.id,
                'partner_invoice_id':reservation.partner_invoice_id.id,
                'partner_shipping_id':reservation.partner_shipping_id.id,
                'checkin_date': reservation.checkin,
                'checkout_date': reservation.checkout,
                'duration': duration,
                'reservation_id': reservation.id,
                'service_lines':reservation['folio_id']
            }
            for line in reservation.reservation_line:
                for r in line.reserve:
                    folio_lines.append((0, 0, {
                        'checkin_date': checkin_date,
                        'checkout_date': checkout_date,
                        'product_id': r.product_id and r.product_id.id,
                        'name': reservation['reservation_no'],
                        'product_uom': r['uom_id'].id,
                        'price_unit': r['lst_price'],
                        'product_uom_qty': (datetime.datetime(*time.strptime(reservation['checkout'], '%Y-%m-%d %H:%M:%S')[:5]) - datetime.datetime(*time.strptime(reservation['checkin'], '%Y-%m-%d %H:%M:%S')[:5])).days
                    }))
                    room_obj.write(cr, uid, [r.id], {'status': 'occupied'}, context=context)
            folio_vals.update({'room_lines': folio_lines})
            folio = hotel_folio_obj.create(cr, uid, folio_vals, context=context)
            cr.execute('insert into hotel_folio_reservation_rel (order_id, invoice_id) values (%s,%s)', (reservation.id, folio))
            # masukan id folio di reservation form
            self.write(cr, uid, ids, {'state': 'done','folio_id2':folio}, context=context)
        return True

class hotel_folio(osv.Model):
    _inherit = 'hotel.folio'
    _rec_name = 'name'      
    #terjadi error disini (fungsi dari modul asli hotel) ketika confirm folio form
    def action_ship_create(self, cr, uid, ids, context=None):
        order_ids = [folio.order_id.id for folio in self.browse(cr, uid, ids)]  
        #ValueError: "'NoneType' object is not iterable" while evaluating
        #self.pool.get('sale.order').action_ship_create(cr, uid, order_ids, context=None)
        return True

    def _get_duration(self, cr, uid, ids, name, arg, context=None):
        ''' Fungsi otomatis utk menghitung jml hari menginap'''
        res = {}
        for folio in self.browse(cr, uid, ids, context=context):  
            company_obj = self.pool.get('res.company')
            configured_addition_hours = 0
            company_ids = company_obj.search(cr, uid, [])
            if company_ids:
                company = company_obj.browse(cr, uid, company_ids[0])
                configured_addition_hours = company.additional_hours

            duration = 0
            checkin_date = folio.checkin_date
            checkout_date = folio.checkout_date
            if checkin_date and checkout_date:
                chkin_dt = datetime.datetime.strptime(checkin_date, '%Y-%m-%d %H:%M:%S')
                chkout_dt = datetime.datetime.strptime(checkout_date, '%Y-%m-%d %H:%M:%S')
                dur = chkout_dt - chkin_dt
                duration = dur.days
                if configured_addition_hours > 0:
                    additional_hours = abs((dur.seconds / 60) / 60)
                    if additional_hours >= configured_addition_hours:
                        duration += 1
            res[folio.id] = duration     
        return res           

    def _get_invoice(self, cr, uid, ids, name, arg, context=None):
        res = {}
        inv_obj = self.pool.get('account.invoice')
        order_number = self.browse(cr,uid,ids[0]).order_id.name
        inv_id = inv_obj.search(cr,uid,[('origin','=',order_number)])  
        if inv_id == []:
            return res
        else: 
            res[ids[0]] = inv_id[0]   
        return res  

    _columns = {
        'duration2': fields.function(_get_duration, type='integer', readonly=True, string='Duration'),
        'invoice_id': fields.function(_get_invoice,type='many2one',readonly=True,relation='account.invoice', string='Invoice')
    }

class hotel_folio_line(osv.Model):
    _inherit = 'hotel.folio.line'

    def copy(self, cr, uid, id, default=None, context=None):
        return self.pool.get('sale.order.line').copy(cr, uid, id, default=None, context=context)

    def _amount_line(self, cr, uid, ids, field_name, arg, context):
        return self.pool.get('sale.order.line')._amount_line(cr, uid, ids, field_name, arg, context)

    def _number_packages(self, cr, uid, ids, field_name, arg, context):
        return self.pool.get('sale.order.line')._number_packages(cr, uid, ids, field_name, arg, context)

    def create(self, cr, uid, vals, context=None, check=True):
        
        if 'folio_id' in vals:
            folio = self.pool.get("hotel.folio").browse(cr, uid, vals['folio_id'], context=context)
            vals.update({'order_id':folio.order_id.id})
        return super(osv.Model, self).create(cr, uid, vals, context)


class hotel_room(osv.Model):
    _inherit = 'hotel.room'
    _description = 'Hotel Room'
    _columns = {
        'room_reservation_line_ids': fields.one2many('hotel.room.reservation.line', 'room_id', 'Room Reservation Line'),
    }

    def cron_room_line(self, cr, uid, context=None):
        
        reservation_line_obj = self.pool.get('hotel.room.reservation.line')
        now = datetime.datetime.now()
        curr_date = now.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        room_ids = self.search(cr, uid, [], context=context)
        for room in self.browse(cr, uid, room_ids, context=context):
            status = {}
            reservation_line_ids = [reservation_line.id for reservation_line in room.room_reservation_line_ids]
            reservation_line_ids = reservation_line_obj.search(cr, uid, [('id', 'in', reservation_line_ids), ('check_in', '<=', curr_date), ('check_out', '>=', curr_date)], context=context)
            if reservation_line_ids:
                status = {'status': 'occupied'}
            else:
                status = {'status': 'available'}
            self.write(cr, uid, [room.id], status, context=context)
        return True


class hotel_reservation_line(osv.Model):
    _inherit = "hotel_reservation.line"

    _columns = {
         'reserve':fields.many2many('hotel.room', 'hotel_reservation_line_room_rel', 'room_id', 'hotel_reservation_line_id', domain="[('isroom','=',True),('categ_id','=',categ_id),('status','=','available')]"),
        }

    def on_change_categ(self, cr, uid, ids, categ_ids, checkin, checkout, context=None):
        hotel_room_obj = self.pool.get('hotel.room')
        hotel_room_ids = hotel_room_obj.search(cr, uid, [('categ_id', '=', categ_ids)], context=context)
        assigned = False
        room_ids = []
        if not checkin:
            raise osv.except_osv(_('No Checkin date Defined!'), _('Before choosing a room,\n You have to select a Check in date or a Check out date in the reservation form.'))
        #import pdb;pdb.set_trace()    
        for room in hotel_room_obj.browse(cr, uid, hotel_room_ids, context=context):
            assigned = False
            for line in room.room_reservation_line_ids:
                if line.check_in == checkin and line.check_out == checkout:
                    assigned = True
            if not assigned:
                room_ids.append(room.id)
        domain = {'reserve': [('id', 'in', room_ids)]}
        return {'domain': domain}

hotel_reservation_line()


class hotel_housekeeping(osv.Model):
    _inherit = "hotel.housekeeping"
    _rec_name = "room_no"

class hotel_restaurant_kitchen_order_tickets(osv.Model):
    _inherit = "hotel.restaurant.kitchen.order.tickets"
    _rec_name = "orderno"
  
class hotel_restaurant_order(osv.Model):
    _inherit = "hotel.restaurant.order"
    _rec_name = "order_no"

    _defaults = {
        'o_date': fields.date.context_today,
    }


class hotel_reservation_order(osv.Model):
    _inherit = "hotel.reservation.order"
    _rec_name = "order_number"


class hotel_restaurant_reservation(osv.Model):
    _inherit = "hotel.restaurant.reservation"
    _rec_name = "reservation_id"


class hotel_housekeeping(osv.Model):
    _inherit = "hotel.housekeeping"

    _columns = {
        'name' : fields.char('Number',required=True,readonly=True),
        'current_date':fields.date("Today's Date", required=True,readonly=True),
        'inspect_date_time':fields.datetime('Inspect Date Time', required=True),
        'quality':fields.selection([('bad', 'Bad'), ('good', 'Good'), ('ok', 'Ok')], 'Quality', required=True, help='Inspector inspect the room and mark as Bad, Good or Ok. '),
    }

    _sql_constraints = [('name_uniq', 'unique(name)','Number of housekeeping must be uniq')]    

    _defaults = {
        'name':lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'hotel.housekeeping'), 
        'quality':'ok',
        'inspect_date_time':fields.date.context_today,
    }   

    def action_set_to_dirty(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'dirty'})
        wf_service = netsvc.LocalService('workflow')
        for id in ids:
            wf_service.trg_create(uid, self._name, id, cr)

        #set activity line supaya sama statusnya dengan state housekeeping
        for act in self.browse(cr,uid,ids[0]).activity_lines :
            self.pool.get('hotel.housekeeping.activities').write(cr,uid,act.id,{'state': 'dirty'}) 

        return True

    def room_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state':'cancel'
        })
        #set activity line supaya sama statusnya dengan state housekeeping
        for act in self.browse(cr,uid,ids[0]).activity_lines :
            self.pool.get('hotel.housekeeping.activities').write(cr,uid,act.id,{'state': 'cancel'}) 

        return True

    def room_done(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state':'done'
        })
        #set activity line supaya sama statusnya dengan state housekeeping
        for act in self.browse(cr,uid,ids[0]).activity_lines :
            self.pool.get('hotel.housekeeping.activities').write(cr,uid,act.id,{'state': 'done'}) 

        return True

    def room_inspect(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state':'inspect'
        })
        #set activity line supaya sama statusnya dengan state housekeeping
        for act in self.browse(cr,uid,ids[0]).activity_lines :
            self.pool.get('hotel.housekeeping.activities').write(cr,uid,act.id,{'state': 'inspect'}) 

        return True

    def room_clean(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {
            'state':'clean'
        })
        if not self.browse(cr,uid,ids[0]).activity_lines :
            raise osv.except_osv(_('Error!'), _('Activity Lines is empty!'))

        #set activity line supaya sama statusnya dengan state housekeeping
        for act in self.browse(cr,uid,ids[0]).activity_lines :
            self.pool.get('hotel.housekeeping.activities').write(cr,uid,act.id,{'state': 'clean'}) 

        return True

class hotel_housekeeping_activities(osv.Model):
    _inherit = "hotel.housekeeping.activities"

    _columns = {
        'state': fields.selection([('dirty', 'Dirty'), ('clean', 'Clean'), ('inspect', 'Inspect'), ('done', 'Done'), ('cancel', 'Cancelled')], 'State', select=True,readonly=True),   
        }

    _defaults = {
        'state':'dirty', 
    }  

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: