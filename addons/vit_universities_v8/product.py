from openerp.osv import fields,osv

########Product##############
class product_product(osv.Model):

    _name = "product.product"
    _description = "Product2"
    _inherit = "product.product"

    _columns = {
        'is_sks'		: fields.boolean('SKS',help="Centang jika merupakan beban/biaya SKS"),
        'fakultas_id' 	: fields.many2one('master.fakultas','Fakultas'),
        'split_invoice' : fields.boolean('Split Invoice',help="jika dicentang maka invoice yg digenerate dari KRS akan tersplit sesuai angka yang diisi pada partner"),
        # master price UP dan UK
        'angsuran1'		: fields.float('Angsuran 1'),
        'angsuran2'		: fields.float('Angsuran 2'),
        'angsuran3'		: fields.float('Angsuran 3'),
        'angsuran4'		: fields.float('Angsuran 4'),
        'angsuran5'		: fields.float('Angsuran 5'),
        'angsuran6'		: fields.float('Angsuran 6'),
        'total_persmt'	: fields.float('Total'),

            }

product_product()
