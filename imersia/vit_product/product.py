# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
from openerp.tools.translate import _

#----------------------------------------------------------
# Categories Finishing
#----------------------------------------------------------
class product_finishing(osv.osv):
    _name = "product.finishing"
    _description = "Product Finishing"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.finishing','Parent Finishing', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

#----------------------------------------------------------
# Categories Quality
#----------------------------------------------------------
class product_quality(osv.osv):
    _name = "product.quality"
    _description = "Product Quality"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.quality','Parent Quality', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

#----------------------------------------------------------
# Categories Material
#----------------------------------------------------------
class product_material(osv.osv):
    _name = "product.material"
    _description = "Product Material"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.material','Parent Material', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

class product_customers_description(osv.osv):
    _name = "product.customers.description"

    _columns = {
        'name': fields.char('Customers Description'),
        'partner_id': fields.many2one('res.partner', 'Customers', domain=[('customer','=',True)]),
        'produk_id' : fields.many2one('product.template', 'Product'),
    }

class product_package_type(osv.osv):
    _name = "product.package.type"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)       

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.package.type','Parent Package', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

class product_wood_type(osv.osv):
    _name = "product.wood.type"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.wood.type','Parent Wood', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

class product_collection(osv.osv):
    _name = "product.collection"

    def name_get(self, cr, uid, ids, context=None):
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)  

    _columns = {
        'name': fields.char('Name'),
        'parent_id': fields.many2one('product.collection','Parent Collection', ondelete='cascade'),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
    }

class product_template(osv.osv):
    _inherit = 'product.template'

    def _get_material_volume2(self, cr, uid, ids, field_name, arg, context=None):
        result  = dict.fromkeys(ids, False)
        bom_obj = self.pool.get('mrp.bom')
        for i in self.browse(cr, uid, ids, context=context):
            bom_ids = bom_obj.search(cr,uid,[('product_tmpl_id','=',i.id)])
            com_vol = 0.00
            print("bom_ids %s " % str(bom_ids))
            try : 
                if bom_ids:
                    bom = bom_obj.browse(cr,uid,bom_ids[0],)
                    # Cek bom > 1 ?
                    if len(bom_ids) > 1:
                        raise osv.except_osv(_('Product has more than one BoM'), _('Pls Check BoM for this product in Manufacturing'))
                    if bom.bom_line_ids:
                        for bom1 in bom.bom_line_ids :
                            print("produk %s category %s" % (bom1.product_id.name,bom1.product_id.product_category))
                            if bom1.product_id.product_category == 'cubic':
                                com_vol += bom1.product_qty * bom1.product_id.product_material_volume12 
                    elif not bom.bom_line_ids:
                        if bom.product_tmpl_id.product_category == 'cubic':
                            com_vol += bom.product_qty * bom.product_tmpl_id.product_material_volume12 
                elif i.product_category == 'cubic':
                    com_vol = (i.product_length * i.product_height * i.product_larg)/1000000000.0
            except ZeroDivisionError:
                raise osv.except_osv(_('No could not divide by zero'), _('Pls Check The values of Product Mesurement Tab'))
            print("vol %s " % str(com_vol))
            result[i.id] = com_vol
        return result

    def compute_vol(self, cr, uid, ids, context=None):
        # self.write(cr,uid,ids,{'product_material_volume12': com_vol},)
        return True

    _columns = {
        'finishing_id': fields.many2one('product.finishing', 'Finishing'),
        'quality_id': fields.many2one('product.quality', 'Quality'),
        'material_id': fields.many2one('product.material', 'Material'),
		'material_vol' : fields.float("Material Volume (m3)", digits=(12,9),help="Volume sum of all sub-component material vol"),
    	'packaging_id' : fields.many2one('product.package.type', "Package type"),
		'description_ids' : fields.one2many('product.customers.description','produk_id',string="Customers description",),
        'colection_ids': fields.many2many('product.collection','product_collection_rel', id1='prod_id', id2='coll_id', string='Collection', ondelete='restrict'),
		'wood_type_id' : fields.many2one('product.wood.type','Wood'),
		'product_category':fields.selection([('cylindrical','Cylindrical'),('cubic','Cubic'),('volume','Volume')],'Measurement Type'),
        'product_length':fields.float('Length (mm)'),
        'product_diameter':fields.float('Diameter (mm)'),
        'product_larg':fields.float('Width (mm)'),
        'product_height':fields.float('Thickness (mm)'),
        'product_weight':fields.float('Weight (Kg)'),
        'product_cylindrical_volume': fields.float('Volume (m3)',digits=(12, 9)),
        'product_cubic_volume': fields.float('Component (m3)',help="Length x Width x Thickness",digits=(12, 9)),
        'product_volume_volume': fields.float('Volume (Liter)',digits=(12, 9)),
        'product_cylindrical_density':fields.float('Density (Kg/m3)'),
        'product_cubic_density':fields.float('Density (Kg/m3)'),
        'product_volume_density':fields.float('Density (Kg/Liter)'),
        'product_material_volume12':fields.function(_get_material_volume2,type='float',store=False,digits=(12, 9),string='Material Volume (m3)',help="Volume sum of all sub-component vol"),
        'product_classic_volume12':fields.float('Classic Volume (m3)',help="Length x Width x Thickness"),
        'product_unbuilt_volume12':fields.float('Unbuilt (m3)',digits=(12, 9),help="Volume of the disassemble furniture, ready to be packed"),
        'product_packed_volume12':fields.float('Packed (m3)',digits=(12, 9),help="Volume of the packed furniture"),
    }

    _defaults = {
        'product_length': 1.0,
        'product_diameter': 1.0,
        'product_larg': 1.0,
        'product_height': 1.0,
        # 'product_category' : False,
        #'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.supplierinfo', context=c),
    }

    def product_weight_change(self, cr, uid, ids, product_category, 
        product_weight, product_cylindrical_volume,product_cubic_volume,product_volume_volume):
        density= None
        try:
            if product_category:
                if product_category == 'cylindrical':
                    density = product_weight/float(product_cylindrical_volume)
                    return {'value': {'product_cylindrical_density': density}}
                elif product_category == 'cubic':
                    density = product_weight/float(product_cubic_volume)
                    return {'value': {'product_cubic_density': density}}
                elif product_category == 'volume':
                    density = product_weight/float(product_volume_volume)
                    return {'value': {'product_volume_density': density}}
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
        return True
    
    def product_qty_change(self, cr, uid, ids, product_category, 
        product_height, product_larg, product_diameter, product_length):
        volume = None
        try:
            if product_category:
                if product_category == 'cylindrical':
                    volume = (product_length * (product_diameter/2.0) * float(22/7))/1000000000.0
                    return {'value': {'product_cylindrical_volume': volume}}
                elif product_category == 'cubic':
                    volume = (product_length * product_height * product_larg)/1000000000.0
                    #volume = (product_length * (product_diameter/2.0) * float(22/7))/1000000000.0
                    return {'value': {'product_cubic_volume': volume,'product_classic_volume12':volume}}
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
        return True
    
    def product_density_change(self, cr, uid, ids, product_category, 
        product_cylindrical_density, product_cubic_density, product_volume_density,
        product_cylindrical_volume, product_cubic_volume, product_volume_volume):
        weight = None
        try:
            if product_category:
                if product_category == 'cylindrical':
                    weight = product_cylindrical_density * float(product_cylindrical_volume)
                    #return {'value': {'product_weight': weight}}
                elif product_category == 'cubic':
                    weight = product_cubic_volume * float(product_cubic_density)
                    #volume = (product_length * (product_diameter/2.0) * float(22/7))/1000000000.0
                    #return {'value': {'product_weight': weight}}
                elif product_category == 'volume':
                    weight = product_volume_density * float(product_volume_volume)
                    #return {'value': {'product_weight': weight}}
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zero'), _('Pls Check The values of Product Mesurement Tab'))
        return {'value': {'product_weight': weight}}

    def product_volumn_change(self, cr, uid, ids ,product_category, product_volume_volume, product_weight):
        density = None
        try:
            if product_category:
                if product_category == 'volume':
                   density = product_weight/float(product_volume_volume)
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
        return {'value': {'product_volume_density': density}}

    def categ_change(self, cr, uid, ids ,product_category,sale_ok):
        if sale_ok :
            return {'value': {'product_category': 'cubic'}}

product_template()


class product_product(osv.osv):
    _name = "product.product"
    _inherit = "product.product"

    def categ_change(self, cr, uid, ids ,product_category,sale_ok):
        if sale_ok :
            return {'value': {'product_category': 'cubic'}}

    def product_qty_change(self, cr, uid, ids, product_category, 
        product_height, product_larg, product_diameter, product_length):
        volume = None
        try:
            if product_category:
                if product_category == 'cylindrical':
                    volume = (product_length * (product_diameter/2.0) * float(22/7))/1000000000.0
                    return {'value': {'product_cylindrical_volume': volume}}
                elif product_category == 'cubic':
                    volume = (product_length * product_height * product_larg)/1000000000.0
                    #volume = (product_length * (product_diameter/2.0) * float(22/7))/1000000000.0
                    return {'value': {'product_cubic_volume': volume,'product_classic_volume12':volume}}
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
        return True

product_product()