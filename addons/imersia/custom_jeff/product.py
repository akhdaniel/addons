import re
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)


##############""" patches by harsh jain"""####################start

# class product_package_type(osv.osv):
#     _name='product.package.type'
#     _columns={'name':fields.char('Package Type')}

# class product_collection_type(osv.osv):
#     _name='product.collection.type'
#     _columns={'name':fields.char('Collection Type')}
    
# class product_customer_description(osv.osv):
#     _name='product.customer.description'
#     _columns={'customer':fields.many2one('res.partner',String='Customer'),
#               'description':fields.text(string='Description'),
#               'product_template_rel':fields.many2one('product.template')
#               }
    

################################################################################

class product_template(osv.osv):
    _inherit = 'product.template'

    #####edited by harsh jain
    
    def _get_material_volume(self, cr, uid, ids, field_name, arg, context=None):
        if context==None:context={}
        res = dict.fromkeys(ids, False)
        for i in self.browse(cr, uid, ids, context=context):
            bom_id=self.pool.get('mrp.bom').search(cr,uid,[('product_tmpl_id','=',i.id)],context=context)
            if bom_id:bom_id=bom_id[0]
            bom_obj=self.pool.get('mrp.bom').browse(cr,uid,bom_id)
            volume=0.0
            for j in bom_obj.bom_line_ids:
                volume += j.product_id.product_tmpl_id.product_cubic_volume
            res[i.id]=volume
        return res
    
    #####edited by harsh jain
    
    _columns = {
            'product_category':fields.selection([('cylindrical','Cylindrical'),('cubic','Cubic'),('volume','Volume')],'Product Category'),
            'product_length':fields.float('Length (mm)'),
            'product_diameter':fields.float('Diameter (mm)'),
            'product_larg':fields.float('Larg(mm)'),
            'product_height':fields.float('Height(mm)'),
            'product_weight':fields.float('Weight(Kg)'),
            'product_cylindrical_volume': fields.float('Volume(m3)',digits=(12, 9)),
            'product_cubic_volume': fields.float('Component Volume(m3)',digits=(12, 9)),#####edited by harsh jain #########
            'product_volume_volume': fields.float('Volume(Liter)',digits=(12, 9)),
            'product_cylindrical_density':fields.float('Density(Kg/m3)'),
            'product_cubic_density':fields.float('Density(Kg/m3)'),
            'product_volume_density':fields.float('Density (Kg/Liter)'),
            'product_finishing12':fields.text('Finishing'),
            'product_material_volume12':fields.function(_get_material_volume,type='float',digits=(12, 9),string='Material volume (m3)',help="Volume sum of all sub-component vol"),
            'product_classic_volume12':fields.float('Classic Volume',help="L*l*H"),
            'product_unbuilt_volume12':fields.float('Unbuilt Volume (m3)',help="Volume of the disassemble furniture, ready to be packed"),
            'product_packed_volume12':fields.float('Packed Volume (m3)',help="Volume of the packed furniture"),
            # 'product_package_type12':fields.many2one('product.package.type','Package Type'),
            # 'product_customer_description12':fields.one2many('product.customer.description','product_template_rel','Customer Description'),
            # 'product_collection_type12':fields.many2one('product.collection.type','Collection'),
            # 'product_wood_description12':fields.text('Wood'),
            ########""" patches by harsh jain"""
            
    }
    _defaults = {
        'product_length': 1.0,
        'product_diameter': 1.0,
        'product_larg': 1.0,
        'product_height': 1.0,
        #'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'product.supplierinfo', context=c),
    }
    """
    def create(self, cr, uid, vals, context=None):
        volume = None
        density = None
        weight= None
        try:
            if vals.get('product_category') == 'cylindrical':
                volume = (vals.get('product_length') * (vals.get('product_diameter')/2.0) * float(22/7))/1000000000.0
                if vals.get('compute_selection') == 'compute_weight':
                    density = vals.get('product_weight')/float(volume)
                    vals.update({'product_cylindrical_density':density})
                elif vals.get('compute_selection') == 'compute_density':
                    weight = vals.get('product_cylindrical_density') * float(volume)
                    vals.update({'product_weight':weight})
                vals.update({'product_cylindrical_volume':volume})
                
            elif vals.get('product_category') == 'cubic':
                volume = (vals.get('product_length') * vals.get('product_height')* vals.get('product_larg'))/1000000000.0
                if vals.get('compute_selection') == 'compute_weight':
                    density = vals.get('product_weight')/float(volume)
                    vals.update({'product_cubic_density':density})
                elif vals.get('compute_selection') == 'compute_density':
                    weight = vals.get('product_cubic_volume') * float(volume)
                    vals.update({'product_weight':weight})
                vals.update({'product_cubic_volume':volume})
            elif vals.get('product_category') == 'volume':
                
                volume = vals.get('product_volume_volume')
                if vals.get('compute_selection') == 'compute_weight':
                    density = vals.get('product_weight')/float(volume)
                    vals.update({'product_volume_density':density})
                elif vals.get('compute_selection') == 'compute_density':
                    weight = vals.get('product_volume_density') * float(volume)
                    vals.update({'product_weight':weight})
                vals.update({'volume':volume,})
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
        vals.update({'volume':volume,'weight':vals.get('product_weight')})
        return super(product_template, self).create(cr, uid, vals, context=context)

    """
    """
    def write(self, cr, uid, ids, vals, context=None):
        ''' Store the standard price change in order to be able to retrieve the cost of a product template for a given date'''
        if isinstance(ids, (int, long)):
            ids = [ids]
            
        product_obj = self.browse(cr, uid, ids)
        category = None
        category, lenght, diameter, height, larg, volume, weight, compute_selection = False, False, False, False, False, False, False, False
        cylindrical_density, cubic_density, volume_density = False, False, False
        if vals.has_key('product_category'):
            category = vals.get('product_category')
        else:
            category = product_obj.product_category
        
        if vals.has_key('compute_selection'):
            compute_selection = vals.get('compute_selection')
        else:
            compute_selection = product_obj.compute_selection
            
            
        if vals.has_key('product_length'):
            lenght = vals.get('product_length')
        else:
            lenght = product_obj.product_length
            
        if vals.has_key('product_diameter'):
            diameter = vals.get('product_diameter')
        else:
            diameter = product_obj.product_diameter
            
        if vals.has_key('product_height'):
            height = vals.get('product_height')
        else:
            height = product_obj.product_height
            
        if vals.has_key('product_larg'):
            larg = vals.get('product_larg')
        else:
            larg = product_obj.product_larg
            
        if vals.has_key('product_weight'):
            weight = vals.get('product_weight')
        else:
            weight = product_obj.product_weight
            
            
        if vals.has_key('product_cylindrical_volume'):
            cylindrical_volume = vals.get('product_cylindrical_volume')
        else:
            cylindrical_volume = product_obj.product_cylindrical_volume
        
        if vals.has_key('product_cubic_volume'):
            cubic_volume = vals.get('product_cubic_volume')
        else:
            cubic_volume = product_obj.product_cubic_volume
            
        if vals.has_key('product_volume_volume'):
            volume = vals.get('product_volume_volume')
        else:
            volume = product_obj.product_volume_volume
            
            
        if vals.has_key('product_cylindrical_density'):
            cylindrical_density = vals.get('product_cylindrical_density')
        else:
            cylindrical_density = product_obj.product_cylindrical_density
        
        if vals.has_key('product_cubic_density'):
            cubic_density = vals.get('product_cubic_density')
        else:
            cubic_density = product_obj.product_cubic_density
            
        if vals.has_key('product_volume_density'):
            volume_density = vals.get('product_volume_density')
        else:
            volume_density = product_obj.product_volume_density
        
        
        try :               
            if category == 'cylindrical':
                cylindrical_volume = (lenght * (diameter/2.0) * float(22/7))/1000000000.0
                print"Vaolumn >>>>",cylindrical_volume
                if compute_selection == 'compute_weight':
                    density = weight/float(cylindrical_volume)
                    vals.update({'product_cylindrical_density':density})
                elif compute_selection == 'compute_density':
                    weight = cylindrical_density * float(cylindrical_volume)
                    vals.update({'product_weight':weight})
                vals.update({'product_cylindrical_volume':cylindrical_volume,'volume':cylindrical_volume})
                
            elif category == 'cubic':
                cubic_volume = (lenght * height* larg)/1000000000.0
                if compute_selection == 'compute_weight':
                    density = weight/float(cubic_volume)
                    vals.update({'product_cubic_density':density})
                elif compute_selection == 'compute_density':
                    weight = cubic_density * float(cubic_volume)
                    print"Weight>>>>",weight
                    vals.update({'product_weight':weight})
                vals.update({'product_cubic_volume':cubic_volume,'volume':cubic_volume})
            elif category == 'volume':
                if compute_selection == 'compute_weight':
                    density = weight/float(volume)
                    vals.update({'product_volume_density':density})
                elif compute_selection == 'compute_density':
                    weight = volume_density * float(volume)
                    vals.update({'product_weight':weight})
                vals.update({'volume':volume})
        except ZeroDivisionError:
            raise osv.except_osv(_('No could not divide by zero'), _('Pls Check The values of Product Mesurement Tab'))
        vals.update({'weight':weight})
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        return res
    """
    
    def product_weight_change(self, cr, uid, ids, product_category, product_weight, product_cylindrical_volume,product_cubic_volume,product_volume_volume):
        
        volume = None
        density = None
        weight= None
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
    
    def product_qty_change(self, cr, uid, ids, product_category, product_height, product_larg, product_diameter, product_length):
        
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
    
    def product_density_change(self, cr, uid, ids, product_category, product_cylindrical_density, product_cubic_density, product_volume_density,product_cylindrical_volume, product_cubic_volume, product_volume_volume):
        
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
            raise osv.except_osv(_('No could not divide by zwero'), _('Pls Check The values of Product Mesurement Tab'))
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
    
    
    
    
    


            
 





