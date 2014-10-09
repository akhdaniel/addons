from openerp.osv import fields,osv

class res_users(osv.osv):
    _inherit = "res.users"
    _name = "res.users"

    _columns = {
        'location_ids'  : fields.many2many('stock.location','stock_loc_res_users_rel','user_id','location_id',"User's Location"),
        'principal_ids' : fields.many2many('res.partner','res_user_res_partner_rel','user_id','partner_id',"User's Principal",domain=[('supplier','=',True)]),
        }

res_users()


# class purchase_order(osv.osv):
#     _inherit = "purchase.order"
#     _name = "purchase.order"

#     _columns = {
#         'location_ids'  : fields.many2many('stock.location','stock_loc_po_rel','po_id','location_id','Related Location'),
#         'principal_ids' : fields.many2many('res.partner','res_partner_po_rel','po_id','user_id',"User's Principal"),
#         # 'loc_x'         : fields.many2one('stock.location',"Destination",domain="[('id','in',location_ids[0][2])]"),
#         # 'partner_x'     : fields.many2one('res.partner',"Supplier",domain="[('id','in',location_ids[0][2])]"),
#         }

    # def _get_default_loc(self, cr, uid, context=None):  
    #     if context is None:
    #         context = {}
    #     location_ids = []
    #     cr.execute('SELECT sl.id FROM stock_location sl JOIN stock_loc_res_users_rel m2m on sl.id=m2m.location_id '\
    #         'JOIN res_users ru on ru.id=m2m.user_id WHERE sl.active=TRUE AND ru.id = '+ str(uid))
    #     loc = cr.fetchall() 
    #     if loc <> []:
    #         for x in loc:
    #             location_ids.append(x[0])
    #         return [(6, 0, location_ids)]
    #     return False

    # def _get_default_principal(self, cr, uid, context=None):  
    #     if context is None:
    #         context = {}
    #     principal_ids = []
    #     # import pdb;pdb.set_trace()
    #     cr.execute('SELECT rp.id FROM res_partner rp JOIN res_user_res_partner_rel m2m on rp.id=m2m.partner_id '\
    #         'JOIN res_users ru on ru.id=m2m.user_id WHERE rp.active=TRUE AND ru.id = '+ str(uid))
    #     loc = cr.fetchall() 
    #     if loc <> []:
    #         for x in loc:
    #             principal_ids.append(x[0])
    #         return [(6,0,principal_ids)]
    #     return False
        
    # _defaults = {
    #     'location_ids':_get_default_loc,
    #     'principal_ids':_get_default_principal,
    # }

# purchase_order()