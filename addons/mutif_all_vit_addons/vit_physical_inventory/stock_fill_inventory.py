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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp.tools import mute_logger
import sets
import logging
_logger = logging.getLogger(__name__)

class stock_fill_inventory(osv.osv_memory):
    _inherit = "stock.fill.inventory"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', required=True),
        'use_serial_number' : fields.boolean('Use Serial Number'),
    }

    _defaults = {
        'use_serial_number': True,
        'location_id'    :14,#Lokasi Barang Jadi
    }


    def fill_inventory(self, cr, uid, ids, context=None):
        """ To Import stock inventory according to products available in the selected locations.
        @param self: The object pointer.
        @param cr: A database cursor
        @param uid: ID of the user currently logged in
        @param ids: the ID or list of IDs if we want more than one
        @param context: A standard dictionary
        @return:
        """
        if context is None:
            context = {}

        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')
        lot_obj = self.pool.get('stock.production.lot')
        if ids and len(ids):
            ids = ids[0]
        else:
             return {'type': 'ir.actions.act_window_close'}
        fill_inventory = self.browse(cr, uid, ids, context=context)
        res = {}
        res_location = {}

        if fill_inventory.recursive:
            location_ids = location_obj.search(cr, uid, [('location_id',
                             'child_of', [fill_inventory.location_id.id])], order="id",
                             context=context)
        else:
            location_ids = [fill_inventory.location_id.id]

        res = {}
        flag = False

        #######################################################custom#######################################################
        if fill_inventory.use_serial_number:
            sql_del = "delete from stock_inventory_line where inventory_id = %s" %(context['active_id'])
            cr.execute(sql_del)

        #     for location in location_ids:
        #         state = 'done'
        #         cr.execute ('select sum(product_qty) from stock_move where location_id = %s and product_id = %s and state = %s',(location,fill_inventory.product_id.id,state))
        #         hasil_keluar = cr.fetchone()
        #         qty_hasil_keluar = list(hasil_keluar or 0)#karena dlm bentuk tuple di list kan dulu
        #         qty_hasil_keluar = qty_hasil_keluar[0]
        #         if qty_hasil_keluar is None:
        #             qty_hasil_keluar = 0.00

        #         cr.execute ('select sum(product_qty) from stock_move where location_dest_id = %s and product_id = %s and state = %s',(location,fill_inventory.product_id.id,state))
        #         hasil_masuk = cr.fetchone()
        #         qty_hasil_masuk = list(hasil_masuk or 0)
        #         qty_hasil_masuk = qty_hasil_masuk[0] 
        #         if qty_hasil_masuk is None:
        #             qty_hasil_masuk = 0.00      

        #         qty_on_hand = qty_hasil_masuk-qty_hasil_keluar
                
        #         if qty_on_hand == 0 :
        #             raise osv.except_osv(_('Warning!'), _('No product in this location. Please select a location in the product form.'))
        #         for qty in range(int(qty_on_hand)):
        #             lot_id = False
        #             lot_ids = lot_obj.search(cr,uid,[('product_id','=',fill_inventory.product_id.id),('is_used','=',False),('flag_physical_inv','=',False)])
        #             if lot_ids:
        #                 lot_id = lot_ids[0]
        #                 #langsung write field flag_physical_inv di lot agar tidak bisa di search
        #                 lot_obj.write(cr,uid,lot_ids[0],{'flag_physical_inv':True},context=context)  
        #             datas = {'inventory_id' : context['active_ids'][0],
        #                     'product_id'    : fill_inventory.product_id.id, 
        #                     'location_id'   : location, 
        #                     'product_qty'   : 1, 
        #                     'product_uom'   : fill_inventory.product_id.uom_id.id, 
        #                     'prod_lot_id'   : lot_id}

        #             inventory_line_obj.create(cr, uid, datas, context=context)
        # #########################################################################################################################
                    
        # else:
        for location in location_ids:
            datas = {}
            res[location] = {}
            move_ids = move_obj.search(cr, uid, ['|',('location_dest_id','=',location),('location_id','=',location),('state','=','done'),('product_id','=',fill_inventory.product_id.id)], context=context)
            local_context = dict(context)
            local_context['raise-exception'] = False
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                lot_id = False
                if move.prodlot_id :
                    lot_id = move.prodlot_id.id
                prod_id = move.product_id.id
                if move.location_dest_id.id != move.location_id.id:
                    if move.location_dest_id.id == location:
                        qty = uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)
                    else:
                        qty = -uom_obj._compute_qty_obj(cr, uid, move.product_uom,move.product_qty, move.product_id.uom_id, context=local_context)


                    if datas.get((prod_id, lot_id)):
                        qty += datas[(prod_id, lot_id)]['product_qty']

                    datas[(prod_id, lot_id)] = {'product_id': prod_id, 'location_id': location, 'product_qty': qty, 'product_uom': move.product_id.uom_id.id, 'prod_lot_id': lot_id}

            if datas:
                flag = True
                res[location] = datas

        if not flag:
            raise osv.except_osv(_('Warning!'), _('No product in this location. Please select a location in the product form.'))

        for stock_move in res.values():
            for stock_move_details in stock_move.values():
                stock_move_details.update({'inventory_id': context['active_ids'][0]})
                domain = []
                for field, value in stock_move_details.items():
                    if field == 'product_qty' and fill_inventory.set_stock_zero:
                         domain.append((field, 'in', [value,'0']))
                         continue
                    domain.append((field, '=', value))

                if fill_inventory.set_stock_zero:
                    stock_move_details.update({'product_qty': 0})

                line_ids = inventory_line_obj.search(cr, uid, domain, context=context)

                if not line_ids:
                    inventory_line_obj.create(cr, uid, stock_move_details, context=context)


        #######################################################custom#######################################################
        if fill_inventory.use_serial_number:
            # #update dulu field flag_physical_inv=False di lot agar serial number bisa di search
            # sql = "update stock_production_lot set flag_physical_inv = False where is_used = False and product_id = %s" % (fill_inventory.product_id.id)
            # cr.execute(sql)
            # cr.commit()
            # #cari jika ada sn di inventory line sdh is used
            # cr.execute('SELECT sil.id FROM stock_production_lot spl '\
            #                 'LEFT JOIN stock_inventory_line sil ON spl.id = sil.prod_lot_id '\
            #                 'WHERE spl.is_used = True '\
            #                 'AND sil.inventory_id = %s '%(context['active_ids'][0]))
            # sn_match = cr.fetchall()   
            # if sn_match:
            #     for inv_is_used in sn_match:
            #         lot_id = False
            #         lot_ids = lot_obj.search(cr,uid,[('product_id','=',fill_inventory.product_id.id),('is_used','=',False),('flag_physical_inv','=',False)])
            #         if lot_ids:
            #             for lot in lot_ids:
            #                 #langsung write field flag_physical_inv di lot agar tidak bisa di search
            #                 lot_obj.write(cr,uid,lot,{'flag_physical_inv':True},context=context)                             
            #                 cr.execute('SELECT spl.id FROM stock_production_lot spl '\
            #                                 'LEFT JOIN stock_inventory_line sil ON spl.id = sil.prod_lot_id '\
            #                                 'WHERE spl.id = \''+str(lot)+'\' '\
            #                                 'AND sil.inventory_id = %s '%(context['active_ids'][0]))
            #                 lot_match = cr.fetchone() 
            #                 if lot_match :
            #                     continue
            #                 lot_id = lot  
            #                 break                             
 
            #         # set 0 utk sn yang sdh is_used
            #         inventory_line_obj.write(cr,uid,inv_is_used[0],{'product_qty':0},context=context)
                
            #         datas2 = {'inventory_id' : context['active_ids'][0],
            #                 'product_id'    : fill_inventory.product_id.id, 
            #                 'location_id'   : inventory_line_obj.browse(cr,uid,inv_is_used[0]).location_id.id, 
            #                 'product_qty'   : 1, 
            #                 'product_uom'   : fill_inventory.product_id.uom_id.id, 
            #                 'prod_lot_id'   : lot_id}

            #         inventory_line_obj.create(cr, uid, datas2, context=context)
            self.pool.get('stock.inventory').write(cr,uid,context['active_ids'][0],{'product_id':fill_inventory.product_id.id},context=context)    

        return {'type': 'ir.actions.act_window_close'}

stock_fill_inventory()



class stock_inventory(osv.osv):
    _inherit = "stock.inventory"

    def _get_total_line(self, cr, uid, ids, field_names, arg=None, context=None):
        if not ids: return {}
        res = {}
        for phy in self.browse(cr, uid, ids, context=context):
            cr.execute ("""SELECT SUM(product_qty) FROM stock_inventory_line 
                            WHERE inventory_id = %s
                            """%(phy.id))

            t_qty = cr.fetchone()

            t_qty = list(t_qty or 0)#karena dlm bentuk tuple di list kan dulu
            value = t_qty[0]

            if value is None:
                value = 0.00

            res[phy.id] = value

        return res

    def _get_total_serial_number(self, cr, uid, ids, field_names, arg=None, context=None):
        if not ids: return {}
        res = {}
        #import pdb;pdb.set_trace()
        for phy in self.browse(cr, uid, ids, context=context):  
            total_sn = self.pool.get('stock.physical.serial.number').search(cr,uid,[('inventory_id','=',phy.id)],context=context)
            value = 0
            if total_sn:
                value = len(total_sn)
            res[phy.id] = value
        return res

    _columns = {
        'product_id'                    : fields.many2one('product.product', 'Product', readonly=True),
        'total_qty_line'                : fields.function(_get_total_line,type='integer',string='Total Qty Line'),
        'total_qty_serial_number'       : fields.function(_get_total_serial_number,type='integer',string='Total Qty Serial Number'),
        'difference'                    : fields.integer('Checklist Difference'),
        'origin_difference'             : fields.integer('Physical Difference'),
        'serial_number_ids'             : fields.one2many('stock.physical.serial.number','inventory_id','Check Serial Number'),
        'serial_number_insert_ids'      : fields.one2many('stock.physical.serial.number.insert','inventory_id','Create Serial Number'),
        'serial_number_toremove_ids'    : fields.one2many('stock.physical.serial.number.toremove','inventory_id','Remove Serial Number'),
        'location_id'                   : fields.many2one('stock.location','Location'),
        'message'                       : fields.text('Message'),
        'message2'                      : fields.text('Message2'),
    }

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm the inventory and writes its finished date
        @return: True
        """
        if context is None:
            context = {}
        # to perform the correct inventory corrections we need analyze stock location by
        # location, never recursively, so we use a special context
        product_context = dict(context, compute_child=False)

        location_obj = self.pool.get('stock.location')
        for inv in self.browse(cr, uid, ids, context=context):
            if inv.product_id.id:
                move_ids = []
                lot_ids = []
                for line in inv.inventory_line_id:
                    
                    pid = line.product_id.id
                    product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                    amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                    change = line.product_qty - amount
                    lot_id = line.prod_lot_id.id
                    if lot_id not in lot_ids:

                        if change:
                            location_id = line.product_id.property_stock_inventory.id
                            if lot_id:
                                lot_ids.append(lot_id)
                                value = {
                                    'name': _('INV:') + (line.inventory_id.name or ''),
                                    'product_id': line.product_id.id,
                                    'product_uom': line.product_uom.id,
                                    'prodlot_id': lot_id,
                                    'date': inv.date,
                                }

                                if change > 0:
                                    value.update( {
                                        'product_qty': change,
                                        'location_id': location_id,
                                        'location_dest_id': line.location_id.id,
                                    })
                                else:
                                    value.update( {
                                        'product_qty': 1,#-change,
                                        'location_id': line.location_id.id,
                                        'location_dest_id': location_id,
                                    })
                                move_ids.append(self._inventory_line_hook(cr, uid, line, value))


                #import pdb;pdb.set_trace()            
                self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
                self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)
            else:
                move_ids = []
                for line in inv.inventory_line_id:
                    pid = line.product_id.id
                    product_context.update(uom=line.product_uom.id, to_date=inv.date, date=inv.date, prodlot_id=line.prod_lot_id.id)
                    amount = location_obj._product_get(cr, uid, line.location_id.id, [pid], product_context)[pid]
                    change = line.product_qty - amount
                    lot_id = line.prod_lot_id.id
                    if change:
                        location_id = line.product_id.property_stock_inventory.id
                        value = {
                            'name': _('INV:') + (line.inventory_id.name or ''),
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom.id,
                            'prodlot_id': lot_id,
                            'date': inv.date,
                        }

                        if change > 0:
                            value.update( {
                                'product_qty': change,
                                'location_id': location_id,
                                'location_dest_id': line.location_id.id,
                            })
                        else:
                            value.update( {
                                'product_qty': -change,
                                'location_id': line.location_id.id,
                                'location_dest_id': location_id,
                            })
                        move_ids.append(self._inventory_line_hook(cr, uid, line, value))
                self.write(cr, uid, [inv.id], {'state': 'confirm', 'move_ids': [(6, 0, move_ids)]})
                self.pool.get('stock.move').action_confirm(cr, uid, move_ids, context=context)                
        return True

    def search_duplicate_entry(self, cr, uid, inv_id, context=None):
        cr.execute("""SELECT * FROM (
                      SELECT id,serial_number,
                      ROW_NUMBER() OVER(PARTITION BY serial_number ORDER BY id asc) AS Row
                      FROM stock_physical_serial_number
                      WHERE inventory_id = """+str(inv_id)+"""
                        ) dups
                        WHERE 
                        dups.Row > 1   
                    """)     
        duplicate = cr.fetchall()
        return duplicate

    def check_serial_number_inventory(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_line_obj = self.pool.get('stock.inventory.line')
        sn_toremove_obj = self.pool.get('stock.physical.serial.number.toremove')
        for inv in self.browse(cr, uid, ids, context=context):
            sql = "update stock_inventory_line set is_check = False where inventory_id = %s" % (inv.id)
            cr.execute(sql)
            total_sn = self.pool.get('stock.physical.serial.number').search(cr,uid,[('inventory_id','=',inv.id)],context=context)
            teory = 0
            # search duplicate dulu
            duplicate = self.search_duplicate_entry(cr, uid, inv.id, context=context)
            if duplicate :
                duplicates = []
                for dup in duplicate:
                    duplicates.append(dup[1])
                    #hapus otomatis jika duplicate
                    self.pool.get('stock.physical.serial.number').unlink(cr,uid,dup[0],context=context)
                cr.commit()    
                #raise osv.except_osv(_('Warning!'), _("Duplicates serial number entry %s !") % (str(duplicates)))              
            if total_sn:
                teory = len(total_sn)            
            reality = inv.total_qty_line
            difference = reality-teory
            self.write(cr,uid,inv.id,{'difference':difference},context=context)
            cr.commit() 
            for sn in inv.serial_number_ids:
                serial = str(sn.serial_number)
                self.write(cr,uid,inv.id,{'difference':difference},context=context)
                cr.execute('SELECT spl.id,sil.id FROM stock_production_lot spl '\
                                'LEFT JOIN stock_inventory_line sil ON spl.id = sil.prod_lot_id '\
                                'WHERE spl.name = \''+serial+'\' '\
                                'AND sil.inventory_id = %s '%(inv.id))
                sn_match = cr.fetchone()  
                if sn_match :
                    inv_line_obj.write(cr,uid,sn_match[1],{'is_check':True},context=context)
                    continue  
                else :
                    prodlot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','ilike',serial),('is_used','=',False),('product_id','=',inv.product_id.id)])
                    if not prodlot_id :
                        raise osv.except_osv(_('Warning!'), _("Tidak ditemukan serial number %s untuk product %s di master serial number / SN ini sudah pernah di DO !") % (serial,inv.product_id.name))   
                	
            cr.commit()
            #cari sn yang is_used dan ceklist = False
            cr.execute('SELECT sil.id,spl.id FROM stock_production_lot spl '\
                            'LEFT JOIN stock_inventory_line sil ON spl.id = sil.prod_lot_id '\
                            'WHERE spl.is_used = False '\
                            'AND sil.is_check = False '\
                            'AND sil.inventory_id = %s '%(inv.id))
            sn_match_toremove = cr.fetchall()
            #import pdb;pdb.set_trace()
            if sn_match_toremove:
                sql_del = "delete from stock_physical_serial_number_toremove where inventory_id = %s" %(inv.id)
                cr.execute(sql_del)
                sn_toremove = 0            
                for remove in sn_match_toremove:
                    if sn_toremove < difference :
                        sn_toremove_obj.create(cr,uid,{'inventory_id'       :inv.id,
                                                        'inventory_line_id' :remove[0],
                                                        'serial_number_id'  :remove[1],
                                                        },
                                                        context=context)
                        sn_toremove += 1
                    else:
                        break    
                
            return {'warning' : {
                        'title': _("Done processing"),
                        'message': _("Success.."),
                    }
            }                        
            # view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_physical_inventory', 'vit_view_inventory_form')
            # view_id = view_ref and view_ref[1] or False,    
            # return {
            #     'warning': {'title': _('OK!'),'message': _('Done processing. %s Checked' % (serial) )}, 
            #     'name' : _('Work Orders'),
            #     'view_type': 'form',
            #     'view_mode': 'form',            
            #     'res_model': 'stock.inventory',
            #     'res_id': ids[0],
            #     'type': 'ir.actions.act_window',
            #     'view_id': view_id,
            #     'target': 'current',
            #     "context":"{}",
            #     'nodestroy': False,
            # }

    def insert_and_create_serial_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_line_obj = self.pool.get('stock.inventory.line')
        lot_obj = self.pool.get('stock.production.lot')
        for inv in self.browse(cr, uid, ids, context=context):
            if not inv.location_id:
                raise osv.except_osv(_('Warning!'), _("Untuk menggunakan fitur ini lokasi gudang harus diisi !"))
            if not inv.product_id:
                raise osv.except_osv(_('Warning!'), _("Untuk menggunakan fitur ini product harus diisi ketika fill inventory!"))                
            if not inv.serial_number_insert_ids:
                raise osv.except_osv(_('Warning!'), _("Untuk menggunakan fitur ini serial number tidak boleh kosong!"))
            for insert_sn in inv.serial_number_insert_ids:
                prodlot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','=',insert_sn.serial_number)])
                if prodlot_id:
                    raise osv.except_osv(_('Warning!'), _("Serial number %s sudah ada!") % (insert_sn.serial_number))                
                 
                lot_id = lot_obj.create(cr,uid,{'name'          : insert_sn.serial_number,
                                                'product_id'    : inv.product_id.id,
                                                'ref'           : inv.product_id.default_code or False,
                                                },context=context)
                inv_line_obj.create(cr,uid,{'inventory_id'  : inv.id,
                                            'location_id'   : inv.location_id.id,
                                            'product_id'    : inv.product_id.id,
                                            'product_qty'   : 1,
                                            'product_uom'   : inv.product_id.uom_id.id,
                                            'prod_lot_id'   : lot_id,
                                            },context=context)
            msg = inv.message
            if not msg:
                msg = '* '
            self.write(cr,uid,inv.id,{'message': msg+str(len(inv.serial_number_insert_ids))+' Serial Number Created, ',
                                        'origin_difference':inv.origin_difference+int(len(inv.serial_number_insert_ids))})
            return True    


    def remove_serial_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        inv_line_obj = self.pool.get('stock.inventory.line')
        for inv in self.browse(cr, uid, ids, context=context):
            history = inv.message2
            if not history:
                history = '#'
            if inv.serial_number_toremove_ids:
                hist = []
                for mv in inv.serial_number_toremove_ids:
                    inv_line_id = mv.inventory_line_id.id
                    inv_line_obj.write(cr,uid,inv_line_id,{'product_qty':0},context=context)
                    hist.append(mv.serial_number_id.name)
                self.write(cr,uid,inv.id,{'message2':history+' '+str(hist)+' ,',
                                            'origin_difference':inv.origin_difference+int(len(inv.serial_number_toremove_ids))},context=context)    
            return True        

class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns = {
        'flag_physical_inv'   : fields.boolean('Is Used Physical Inventory'),
    }
    
    _defaults = {
        'flag_physical_inv'   : False,
    }

stock_production_lot()


class stock_physical_serial_number(osv.osv):
    _name = 'stock.physical.serial.number'

    def onchange_serial_number(self, cr, uid, ids, serial_number, context=None):
        if not serial_number:
            return {}        
        prodlot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','ilike',serial_number),('is_used','=',False)])

        if not prodlot_id :
            raise osv.except_osv(_('Warning!'), _("Serial number %s belum di input atau sudah di Delivery Order!") % (serial_number))
        desc = self.pool.get('stock.production.lot').browse(cr,uid,prodlot_id[0],context=context).product_id.name   

        return {'value':{'description':desc}} 

    _columns = {
        'inventory_id'      : fields.many2one('stock.inventory', 'Inventory'),
        'serial_number'     : fields.char('Serial Number',size=100,required=True),
        'description'       : fields.char('Description', size=128),
        'qty'               : fields.integer('Qty',readonly=True)
    }

    _defaults = {
        'qty'   : 1,
    }


class stock_inventory_line(osv.osv):
    _inherit = "stock.inventory.line"

    _columns = {
        'is_used'       : fields.related('prod_lot_id','is_used',type='boolean',string='U',readonly=True),
        'is_check'      : fields.boolean('C',readonly=True),

    }
    _defaults = {
        'is_used'   : False,
        'is_check'  : False,
    }

class stock_physical_serial_number_insert(osv.osv):
    _name = 'stock.physical.serial.number.insert'

    def onchange_serial_number(self, cr, uid, ids, serial_number, context=None):
        if not serial_number:
            return {}        
        prodlot_id = self.pool.get('stock.production.lot').search(cr,uid,[('name','ilike',serial_number)])

        if prodlot_id :
            raise osv.except_osv(_('Warning!'), _("Serial number %s sudah ada!") % (serial_number))

        return {} 

    _columns = {
        'inventory_id'      : fields.many2one('stock.inventory', 'Inventory'),
        'serial_number'     : fields.char('Serial Number',size=100,required=True),
        'qty'               : fields.integer('Qty',readonly=True)
    }

    _defaults = {
        'qty'   : 1,
    }


class stock_physical_serial_number_toremove(osv.osv):
    _name = 'stock.physical.serial.number.toremove'

    _columns = {
        'inventory_id'      : fields.many2one('stock.inventory', 'Inventory'),
        'inventory_line_id'  : fields.many2one('stock.inventory.line','Line ID'),
        'serial_number_id'     : fields.many2one('stock.production.lot','Serial Number',size=100),
        'qty'               : fields.integer('Qty',readonly=True)
    }

    _defaults = {
        'qty'   : 1,
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
