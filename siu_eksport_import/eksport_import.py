import csv
import time
import base64
import tempfile
import datetime
import StringIO
import cStringIO
from dateutil import parser
from openerp.osv import fields, osv
from openerp.tools.translate import _


class EksportImport(osv.osv_memory):
    _name = "eksport.import"
    _columns = {
                'type': fields.selection((('eks','Export'), ('imp','Import')), 'Type'),
                'name': fields.char('File Name', 16),
                'tabel' : fields.many2one('ir.model', 'Object Model', required=True),
                'data_file': fields.binary('File'),
    }   
    _defaults = {'type' :'eks'}
    
    
    def eksport_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        
        #[x for x in range(89153,91498)]
        idd = self.pool.get(val.tabel.model).search(cr, uid, [])
        data = self.pool.get(val.tabel.model).read(cr, uid, idd)
      
        result = ';'.join(data[0].keys())   
        value = [d.values() for d in data]
        
        for v in value:
            for x in v:
                if isinstance(x, tuple):
                    v[v.index(x)] = x[0]
        
        for row in value:
            result += '\n' + ';'.join([str(v) for v in row]) 
            
        out = base64.encodestring(result)
        self.write(cr, uid, ids, {'data_file':out, 'name': 'eksport.csv'}, context=context)
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'siu_eksport_import', 'view_wizard_eksport_import')
        view_id = view_rec[1] or False
    
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': val.id,
            'res_model': 'eksport.import',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }
             
    def import_excel(self, cr, uid, ids, context=None):
        val = self.browse(cr, uid, ids)[0]
        if not val.data_file:
            raise osv.except_osv(_('Error'), _("Silahkan memilih file yang akan diimport !"))
        
        filename = val.name
        filedata = base64.b64decode(val.data_file)
        input = cStringIO.StringIO(filedata)
        input.seek(0)

        (fileno, fp_name) = tempfile.mkstemp('.csv', 'openerp_')
        file = open(fp_name, "w")
        file.write(filedata)
        file.close()
        
        crd = csv.reader(open(fp_name,"rb"))
        head = crd.next()[0].split(';')


        if val.tabel.model == 'mrp.bom':
            self.create_bom(cr, uid, crd, head)
            return {}
        if val.tabel.model == 'stock.inventory':
            self.opname(cr, uid, crd, head)
            return {}
                
        for row in crd:
            res = {}
            for x in range (0, len(row[0].split(';'))):
                r = row[0].split(';')[x]
                if r.upper() == 'FALSE':
                    r = False
                elif r.upper() == 'TRUE':
                    r = True
                else:
                    try:
                        r = float(r)
                    except:
                        pass
                res[head[x]] = r
                print r
                            
            self.pool.get(str(val.tabel.model)).create(cr, uid, res) 

        return {}                


    def opname(self, cr, uid, data, col):
        product_obj = self.pool.get('product.product')
        inv = self.pool.get("stock.inventory").create(cr, uid, {'name': 'Opname Stock Inventory ' + time.strftime('%d-%m-%Y'), 'date': time.strftime('%Y-%m-%d')})
        for row in data:
            lis = row[0].split(';')
            product = product_obj.browse(cr, uid, int(lis[0]))
            self.pool.get("stock.inventory.line").create(cr, uid, {
                                                                   'inventory_id': inv,
                                                                   'product_id': int(lis[0]),
                                                                   'product_qty': float(lis[1]),
                                                                   'location_id': int(lis[2]),
                                                                   'product_uom': int(lis[3]), 
                                                                   #'prod_lot_id': int(lis[4]),
                                                                   'price_unit': product.standard_price,
                                                                   })


     
    def create_bom(self, cr, uid, data, col):
        no = []
        res = {}
        bom_obj = self.pool.get('mrp.bom')
        product_obj = self.pool.get('product.product') 
        for row in data:
            lis = row[0].split(';')
            print lis
            name = product_obj.browse(cr, uid, int(lis[6])).name_template
            if lis[1]:
                bom_id = bom_obj.create(cr, uid, {
                                                  'name': name,
                                                  'type': lis[5],
                                                  'product_id': int(lis[6]), 
                                                  'product_qty': float(lis[3]),
                                                  'product_uom': int(lis[4])})
                res[lis[0]] = bom_id
                
            elif lis[2]:
                bom_obj.create(cr, uid, {
                                          'name': name,
                                          'type': lis[5],
                                          'bom_id': res[lis[0]],
                                          'product_id': int(lis[6]), 
                                          'product_qty': float(lis[3]),
                                          'product_uom': int(lis[4])})



EksportImport()
