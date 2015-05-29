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

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)
        
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
        # 'complete_name': fields.function(_name_get_fnc, type="char", string='Complete Name'),
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
    }

class product_template(osv.osv):
    _inherit = 'product.template'

    # def _get_material_volume(self, cr, uid, ids, field_name, arg, context=None):
    #     if context==None:context={}
    #     res = dict.fromkeys(ids, False)
    #     for i in self.browse(cr, uid, ids, context=context):
    #         bom_id=self.pool.get('mrp.bom').search(cr,uid,[('product_tmpl_id','=',i.id)],context=context)
    #         if bom_id:bom_id=bom_id[0]
    #         bom_obj=self.pool.get('mrp.bom').browse(cr,uid,bom_id)
    #         volume=0.0
    #         for j in bom_obj.bom_line_ids:
    #             volume += j.product_id.product_tmpl_id.product_cubic_volume
    #         res[i.id]=volume
    #     return res

    def _get_material_volume2(self, cr, uid, ids, field_name, arg, context=None):
        result = dict.fromkeys(ids, False)
        def cek_vol(produk):
            res = 0.00
            categ = produk.product_category
            if categ == 'cylindrical' : res = produk.product_cylindrical_volume
            if categ == 'cubic' : res = produk.product_cubic_volume
            if categ == 'volume' : res = produk.product_volume_volume
            else : 
                res =  produk.material_vol      
                # print("%s not saleable %d" % (produk.name,produk.material_vol))
            return res
        bom_obj = self.pool.get('mrp.bom')
        for i in self.browse(cr, uid, ids, context=context):
            bom_ids = bom_obj.search(cr,uid,[('product_tmpl_id','in',ids)])
            com_vol = cek_vol(i)
            try : 
                if bom_ids:
                    com_vol = 0.00
                    bom_lines = bom_obj.browse(cr,uid,bom_ids,)
                    # Cek bom > 1 ?
                    if len(bom_lines) > 1:
                        raise osv.except_osv(_('Product has more than one BoM'), _('Pls Check BoM for this product in Manufacturing'))
                    for bom in bom_lines:
                        if bom.bom_line_ids:
                            for bom1 in bom.bom_line_ids :
                                vol = cek_vol(bom1.product_id)
                                com_vol += vol
                        elif not bom.bom_line_ids:
                            vol = cek_vol(bom.product_tmpl_id)
                            com_vol += vol
                elif not bom_ids and i.product_category == 'cubic':
                    com_vol = (i.product_length * i.product_height * i.product_larg)/1000000000.0
            except ZeroDivisionError:
                raise osv.except_osv(_('No could not divide by zero'), _('Pls Check The values of Product Mesurement Tab'))
            result[i.id] = com_vol
        return result


    def compute_vol(self, cr, uid, ids, context=None):
        def cek_vol(produk):
            res = 0.00
            categ = produk.product_category
            if categ == 'cylindrical' : res = produk.product_cylindrical_volume
            if categ == 'cubic' : res = produk.product_cubic_volume
            if categ == 'volume' : res = produk.product_volume_volume       
            return res
        data    = self.browse(cr,uid,ids[0],)
        bom_obj = self.pool.get('mrp.bom')
        bom_ids = bom_obj.search(cr,uid,[('product_tmpl_id','in',ids)])
        com_vol = cek_vol(data)
        try : 
            if bom_ids:
                com_vol = 0.00
                bom_lines = bom_obj.browse(cr,uid,bom_ids,)
                if bom_lines.bom_line_ids:
                    for bom1 in bom_lines.bom_line_ids :
                        vol = cek_vol(bom1.product_id)
                        com_vol += vol
                elif not bom_lines.bom_line_ids:
                    vol = cek_vol(bom_lines.product_tmpl_id)
                    com_vol += vol
            elif not bom_ids and data.product_category == 'cubic':
                com_vol = (data.product_length * data.product_height * data.product_larg)/1000000000.0
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zero'), _('Pls Check The values of Product Mesurement Tab'))
        return self.write(cr,uid,ids,{'product_material_volume12': com_vol},)

    _columns = {
        'finishing_id': fields.many2one('product.finishing', 'Finishing'),
        'quality_id': fields.many2one('product.quality', 'Quality'),
        'material_id': fields.many2one('product.material', 'Material'),
        # 'is_furniture': fields.boolean('is Furniture?'),
		'material_vol' : fields.float("Material Volume (m3)", digits=(12,9),help="Volume sum of all sub-component material vol"),
    	'packaging_id' : fields.many2one('product.package.type', "Package type"),
		'description_ids' : fields.one2many('product.customers.description','produk_id',string="Customers description",),
        'colection_ids': fields.many2many('product.collection','product_collection_rel', id1='prod_id', id2='coll_id', string='Collection', ondelete='restrict'),
		'wood_type_id' : fields.many2one('product.wood.type','Wood'),
		'product_category':fields.selection([('cylindrical','Cylindrical'),('cubic','Cubic'),('volume','Volume')],'Product Category'),
        'product_length':fields.float('Length (mm)'),
        'product_diameter':fields.float('Diameter (mm)'),
        'product_larg':fields.float('Larg (mm)'),
        'product_height':fields.float('Height (mm)'),
        'product_weight':fields.float('Weight (Kg)'),
        'product_cylindrical_volume': fields.float('Volume (m3)',digits=(12, 9)),
        'product_cubic_volume': fields.float('Component (m3)',help="Length x width x Height",digits=(12, 9)),
        'product_volume_volume': fields.float('Volume (Liter)',digits=(12, 9)),
        'product_cylindrical_density':fields.float('Density (Kg/m3)'),
        'product_cubic_density':fields.float('Density (Kg/m3)'),
        'product_volume_density':fields.float('Density (Kg/Liter)'),
        'product_material_volume12':fields.function(_get_material_volume2,type='float',store=False,digits=(12, 9),string='Material Volume (m3)',help="Volume sum of all sub-component vol"),
        'product_classic_volume12':fields.float('Classic Volume (m3)',help="Length x width x Height"),
        'product_unbuilt_volume12':fields.float('Unbuilt (m3)',digits=(12, 9),help="Volume of the disassemble furniture, ready to be packed"),
        'product_packed_volume12':fields.float('Packed (m3)',digits=(12, 9),help="Volume of the packed furniture"),
    }

    _defaults = {
        'product_length': 1.0,
        'product_diameter': 1.0,
        'product_larg': 1.0,
        'product_height': 1.0,
        'product_category' : False,
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

product_template()