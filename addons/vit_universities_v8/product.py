from openerp.osv import fields,osv

########Product##############
class product_product(osv.Model):

    _name = "product.product"
    _description = "Product2"
    _inherit = "product.product"

    _columns = {
        'is_sks': fields.boolean('SKS',help="Centang jika merupakan beban/biaya SKS"),
        'fakultas_id' : fields.many2one('master.fakultas','Fakultas'),
            }

product_product()
