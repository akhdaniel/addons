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

from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
from operator import itemgetter
from itertools import groupby

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)



class vit_hand_tag(osv.osv):
    _name = 'vit.hand.tag'

    def _get_total_sn(self, cr, uid, ids, field_name, arg, context=None):

        if context is None:
            context = {}
        result = {}
        for obj in self.browse(cr,uid,ids,context=context):          
            total_qty_sn = obj.vit_hand_tag_barcode_ids
            result[obj.id] = len(total_qty_sn)
        return result

    _columns = {
        'name'              : fields.char('Nomor Penyerahan',required=True,readonly=True),
        'spk_cutting_id'    : fields.many2one('vit.cutting.order',string='SPK Cutting'),#readonly=True,states={'draft':[('readonly',False)]}),
        'spk_makloon_id'    : fields.many2one('vit.makloon.order',string='SPK Makloon'),#readonly=True,states={'draft':[('readonly',False)]}),
        'makloon'           : fields.related('spk_makloon_id','partner_id',type='many2one',relation='res.partner',string='Makloon',readonly=True,store=True),  
        'tanggal'           : fields.date('Tanggal Penyerahan',required=True,readonly=True,states={'draft':[('readonly',False)]}),
        'notes'             : fields.text('Notes'),
        'vit_hand_tag_barcode_ids' : fields.one2many('vit.hand.tag.barcode','vit_hand_tag_id',string='Barcode',readonly=True,states={'draft':[('readonly',False)]}),
        'state'             : fields.selection([('draft','Draft'),('confirm','Confirm')],string='State'),
        'total_qty_sn'      : fields.function(_get_total_sn,type='integer',string="Total Serial Number Input"),
    }

    _defaults = {
        
        'tanggal': fields.date.context_today,
        'state' : 'draft',
        'name': '/',
    }

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.hand.tag.seq') or '/'
        return super(vit_hand_tag, self).create(cr, uid, vals, context=context)

    def confirm(self,cr,uid,ids,context=None):
        makloon_obj    = self.pool.get('vit.makloon.order')
        cutting_obj    = self.pool.get('vit.cutting.order')
        sn_obj         = self.pool.get('stock.production.lot')
        spk_makloon_id = False
        spk_cutting_id = False
        makloon_code   = False
        for my_form in self.browse(cr,uid,ids):
            if my_form.spk_makloon_id:
                makloon_code     = my_form.spk_makloon_id.partner_id.code
                makloon_name     = my_form.spk_makloon_id.partner_id.name
                spk_makloon_id   = my_form.spk_makloon_id.id
                # True kan agar hanya bisa di pakai satu kali per handtag
                makloon_obj.write(cr,uid,spk_makloon_id,{'is_used_handtag':True},context=context)
            if my_form.spk_cutting_id:
                spk_cutting_id = my_form.spk_cutting_id.id
                # True kan agar hanya bisa di pakai satu kali per handtag
                cutting_obj.write(cr,uid,spk_cutting_id,{'is_used_handtag':True},context=context)
            tanggal        = my_form.tanggal
            number         = my_form.name

            if not my_form.vit_hand_tag_barcode_ids:
                raise osv.except_osv(_('Error!'), _('Daftar barcode tidak boleh kosong !'))
            for tag in my_form.vit_hand_tag_barcode_ids:
                #import pdb;pdb.set_trace()
                name = tag.name
                sn_exist = sn_obj.search(cr,uid,[('name','=',name)],context=context)
                if sn_exist :
                    raise osv.except_osv(_('Duplicate Serial Number!'), _(' Serial Number %s sudah ada !') % (name))
                if makloon_code:
                    #cek 2 digit awal barcode harus sama dengan 2 digit awal
                    if name[:2] != makloon_code[:2] :
                        raise osv.except_osv(_('Galat !'), _(' Serial Number %s tidak sesuai dengan kode makloon %s ( %s)!') % (name,makloon_name,makloon_code[:2]))
                sn_obj.create(cr,uid,{'name'            : name,
                                    'spk_makloon_id'    : spk_makloon_id,
                                    'spk_cutting_id'    : spk_cutting_id,
                                    'tanggal'           : tanggal,
                                    'ref'               : number},
                                    context=context)
               
            self.write(cr,uid,my_form.id,{'state':'confirm'},context=context)
        return True 

    def update_spk_cutting_dan_spk_makloon(self,cr,uid,ids,context=None):
        makloon_obj    = self.pool.get('vit.makloon.order')
        cutting_obj    = self.pool.get('vit.cutting.order')        
        sn_obj         = self.pool.get('stock.production.lot')
        spk_makloon_id = False
        spk_cutting_id = False
        for my_form in self.browse(cr,uid,ids):
            if my_form.spk_makloon_id:
                spk_makloon_id = my_form.spk_makloon_id.id
                # True kan agar hanya bisa di pakai satu kali per handtag
                makloon_obj.write(cr,uid,spk_makloon_id,{'is_used_handtag':True},context=context)                
            if my_form.spk_cutting_id:
                spk_cutting_id = my_form.spk_cutting_id.id
                # True kan agar hanya bisa di pakai satu kali per handtag
                cutting_obj.write(cr,uid,spk_cutting_id,{'is_used_handtag':True},context=context)                
            for tag in my_form.vit_hand_tag_barcode_ids:
                
                name = tag.name
                sn_id = sn_obj.search(cr,uid,[('name','=',name)],context=context)
                if sn_id :
                    sn_obj.write(cr,uid,sn_id[0],{'spk_makloon_id':spk_makloon_id,
                                                    'spk_cutting_id':spk_cutting_id},
                                                    context=context)
        return True         

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Allows to delete in draft state"""
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
        return super(vit_hand_tag, self).unlink(cr, uid, ids, context=context)

vit_hand_tag()


class vit_hand_tag_barcode(osv.osv):
    _name = 'vit.hand.tag.barcode'


    _columns ={
        'name'  : fields.char('Barcode',required=True,size=64),
        'vit_hand_tag_id'   : fields.many2one('vit.hand.tag','Hang Tag'),
    }

vit_hand_tag_barcode()  