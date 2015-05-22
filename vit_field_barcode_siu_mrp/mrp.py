import time
import math
import datetime
import calendar
from openerp.osv import osv, fields
import os
import csv



class MaterialRequirement(osv.osv):
    _name = 'material.requirement'
    _inherit  = 'material.requirement'
    homedir = os.path.expanduser('~')

    _columns = {
        'barcode_data': fields.text('Barcode Data'),  
    }

    def plan_change(self, cr, uid, ids, plan):
        Ap1 = "A10"
        Bp1 = "B10"
        p2 = 0
        p3 = 0
        p4 = 1
        p5 = 1
        p6 = 1

        val = self.pool.get('production.plan').browse(cr, uid, plan) 
        product_obj = self.pool.get('product.product')          
        rqn = []
        bcd = []
        for x in val.plan_line:
            rqn.append({
                'product_id': x.product_id.id,
                'product_uom': x.product_uom.id,
                'plan': x.plan,
                'name': product_obj.name_get(cr, uid, [x.product_id.id])[0][1]
            })

        with open("%s"%self.homedir + '/barcode.txt', 'wb') as f:
            writer = csv.writer(f)
            for b, p2 in zip(val.plan_line,range(len(val.plan_line))):
                if b.product_id.ean13 != False:
                    tmpfile = writer.writerow([
                      Ap1+","+str(p2*50)+","+str(p3)+","+str(p4)+","+str(p6)+","+"N"+","+ b.product_id.name,
                      Bp1+","+str(p2*50)+","+str(p3)+","+str(p4)+","+str(p6)+","+"B"+","+ b.product_id.ean13
                        ])

       
        op =  open("%s"%self.homedir + '/barcode.txt', 'r')
        import pdb;pdb.set_trace()

        ln = []
        for line in op:
            ln.append(line)
            
            # cr.execute("select id,barcode_data from material_requirement where id = 11")
            # 'N\nB10,10,0,3,3,7,200,B,"998152-001"\nP1\n'
        ln = ''.join(ln)
        ln = 'N\n'+ln.replace('\"','')+'P\n'
       
        return {'value': {'barcode_data':ln,'requirement_line': rqn}}

MaterialRequirement()
