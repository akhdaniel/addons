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

from openerp import tools
from openerp.osv import fields, osv

class sale_report_garment(osv.osv):
    _name = "sale.report.garment"
    _description = "Sales Orders Statistics Garment"
    _auto = False
    _rec_name = 'date'
    _columns = {
        'date': fields.date('Date Order', readonly=True),
        'date_confirm': fields.date('Date Confirm', readonly=True),
        'year': fields.char('Year', size=4, readonly=True),
        'month': fields.selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
            ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')], 'Month', readonly=True),
        'day': fields.char('Day', size=128, readonly=True),
        'product_id': fields.many2one('product.product', 'Product', readonly=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', readonly=True),
        'product_uom_qty': fields.integer('Real Order Qty', readonly=True),
        'gap_order': fields.integer('Gap Order Qty', readonly=True),
        'total_order': fields.integer('Total Order Qty', readonly=True),
        'percentage': fields.float('Percentage (%)', readonly=True, group_operator="avg"),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'price_total': fields.float('Total Price', readonly=True),

        'categ_id': fields.many2one('product.category','Category of Product', readonly=True),
        'state': fields.selection([
            ('draft', 'Quotation'),
            ('waiting_date', 'Waiting Schedule'),
            ('manual', 'Manual In Progress'),
            ('progress', 'In Progress'),
            ('invoice_except', 'Invoice Exception'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')
            ], 'Order Status', readonly=True),

        'master_model_id': fields.many2one('vit.master.type', 'Model', readonly=True),
        'size': fields.char('Size', readonly=True),
        'sale_order_id': fields.many2one('sale.order','SO', readonly=True),         
    }
    _order = 'date desc'

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'sale_report_garment')
        cr.execute("""
            create or replace view sale_report_garment as (
                select
                    min(foo.id) as id,
                    foo.date as date,
                    foo.date_confirm as date_confirm,
                    foo.year as year,
                    foo.month as month,
                    foo.day as day,                    
                    foo.product_id as product_id,
                    sum(foo.product_uom_qty) as product_uom_qty,
                    sum(foo.gap_order) as gap_order,
                    sum(foo.product_uom_qty)+sum(foo.gap_order) as total_order,
                    sum(foo.product_uom_qty)*100 / nullif((sum(foo.product_uom_qty)+sum(foo.gap_order)),0) as percentage,
                    sum(foo.price_total) as price_total,
                    foo.partner_id as partner_id,
                    foo.state,
                    foo.categ_id as categ_id,
                    foo.sale_order_id as sale_order_id
                from
                    (select
                        min(l.id) as id,
                        s.date_order as date,
                        s.date_confirm as date_confirm,
                        to_char(s.date_order, 'YYYY') as year,
                        to_char(s.date_order, 'MM') as month,
                        to_char(s.date_order, 'YYYY-MM-DD') as day,                    
                        l.product_id as product_id,
                        avg(l.product_uom_qty / u.factor * u2.factor) as product_uom_qty,
                        0 as gap_order,
                        avg((l.product_uom_qty * l.price_unit * (100.0-l.discount) / 100.0)* (100.0-l.discount2) / 100.0) as price_total,
                        s.partner_id as partner_id,
                        s.state,
                        t.categ_id as categ_id,
                        s.id as sale_order_id
                    from
                        sale_order_line l
                          join sale_order s on (l.order_id=s.id) 
                            left join product_product p on (l.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=l.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join mrp_bom mb on (p.id = mb.product_id)
                    group by
                        l.product_id,
                        l.order_id,
                        t.categ_id,
                        s.date_order,
                        s.date_confirm,
                        s.partner_id,
                        s.state,
                        mb.master_model_id,
                        mb.size,                   
                        s.id

                    union

                    select                
                        min(sul.id) as id,
                        s.date_order as date,
                        s.date_confirm as date_confirm,
                        to_char(s.date_order, 'YYYY') as year,
                        to_char(s.date_order, 'MM') as month,
                        to_char(s.date_order, 'YYYY-MM-DD') as day,                    
                        sul.product_id as product_id,
                        0 as product_uom_qty,
                        avg(sul.product_uom_qty / u.factor * u2.factor) as gap_order,
                        0 as price_total,
                        s.partner_id as partner_id,
                        s.state,
                        t.categ_id as categ_id,
                        s.id as sale_order_id

                    from
                        sale_unordered_line sul 
                          join sale_order s on (s.id = sul.unordered_id)
                            left join product_product p on (sul.product_id=p.id)
                                left join product_template t on (p.product_tmpl_id=t.id)
                        left join product_uom u on (u.id=sul.product_uom)
                        left join product_uom u2 on (u2.id=t.uom_id)
                        left join mrp_bom mb on (p.id = mb.product_id)

                    group by
                        sul.product_id,
                        sul.unordered_id,
                        t.categ_id,
                        s.date_order,
                        s.date_confirm,
                        s.partner_id,
                        s.state,
                        mb.master_model_id,
                        mb.size,                   
                        s.id) as foo

                group by
                    foo.date,
                    foo.date_confirm,
                    foo.year,
                    foo.month,
                    foo.day,                    
                    foo.product_id,
                    foo.partner_id,
                    foo.state,
                    foo.categ_id,
                    foo.sale_order_id               
            )
        """)
sale_report_garment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


        # select
        # foo.product,
        # sum(foo.qty)
        # from
        #        ( select
        # l.product_id as product,
        # l.product_uom_qty as qty
        #         from
        #             sale_order_line l
        # where
        # l.order_id = 10313
        # union
        #         select
        #             sul.product_id as product,
        #             sul.product_uom_qty as qty
        #         from
        #             sale_unordered_line sul
        # where
        # sul.unordered_id = 10313) as foo
        # group by
        # foo.product

        #                    (avg(l.product_uom_qty / u.factor * u2.factor))+(avg(l.product_uom_qty / u.factor * u2.factor))-(avg(l.real_max_order / u.factor * u2.factor)) as total_order,