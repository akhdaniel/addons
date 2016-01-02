# -*- coding: utf-8 -*-
from openerp.osv import osv, fields, expression
from datetime import datetime as dt

class chk_mo(osv.osv_memory):
    _name = 'chk_mo.chk_mo'

    _columns={
        'limit':fields.integer('Limit Lines per grouping'),
        'message':fields.char('Message'),
        'memo':fields.text('Memo'),
        'mo_lines':fields.text('MO Lines'),
        'mo_del_ids':fields.text('MO Lines Sisa'),
    }

    _defaults={
        'limit':1,
    }

    def execute(self,cr,uid,ids,context=None):
        lim=self.browse(cr,uid,ids,).limit
        batas = lim > 0 and 'LIMIT %d' % lim or ''
        
        results={};mos=[]
        sql="""SELECT origin,produk_id,state,name_template FROM (SELECT s.origin, state, count(product_id) produk, min(product_id) produk_id, p.name_template, raw_material_production_id as mo_id FROM stock_move s JOIN product_product p on s.product_id = p.id WHERE raw_material_production_id is not null GROUP BY product_id, s.origin, state, p.name_template, mo_id ORDER BY origin,product_id) T1 WHERE produk > 1 %s""" % batas
        cr.execute(sql)
        res = cr.fetchall()

        for r in res:
            mos+=self.pool.get('stock.move').search(cr,uid,[('origin','=',r[0]),('product_id','=',r[1])])
        results.update({'mo_lines':str(mos),'memo':str(res),'message': str("Data tanggal     " + dt.strftime(dt.now(),"%c")),})
        self.write(cr,uid,ids,results,)
        
        moids=len(mos)>0 and str(mos)[1:-1] or ''
        sql1="""SELECT MAX(id) FROM stock_move WHERE state = 'confirmed' AND id in (%s) GROUP BY origin, product_id""" % moids
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'chk_mo', 'view_chk_mo_updated')
        view_id = view_rec[1] or False
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'chk_mo.chk_mo',
            'type': 'ir.actions.act_window',
            'target': 'inline',
        }

    def filtermo(self,cr,uid,ids,context=None):
        mos=self.browse(cr,uid,ids,).mo_lines
        
        res=[];moids=len(mos)>0 and str(mos)[1:-1] or ''
        sql="""SELECT MAX(id) FROM stock_move WHERE state = 'confirmed' AND id in (%s) GROUP BY origin, product_id""" % moids
        cr.execute(sql)
        result = cr.fetchall()
        # res perlu diparsing
        if result != (None,) : 
            for r in result :
                res=map(lambda x:x[0],result)
        self.write(cr,uid,ids,{'mo_del_ids':res},)
        
        view_rec = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'chk_mo', 'view_chk_mo_deleted')
        view_id = view_rec[1] or False
        return {
            'view_type': 'form',
            'view_id' : [view_id],
            'view_mode': 'form',
            'res_id': ids[0],
            'res_model': 'chk_mo.chk_mo',
            'type': 'ir.actions.act_window',
            'target': 'inline',
        }

    def deletemo(self,cr,uid,ids,context=None):
        ID1=self.browse(cr,uid,ids,).mo_lines
        ID2=self.browse(cr,uid,ids,).mo_del_ids
        sql="""DELETE FROM stock_move WHERE id in (%s) and id not in (%s)""" % (ID1 and str(ID1)[1:-1] or '',ID2 and str(ID2)[1:-1] or '')
        print(sql)
        cr.execute(sql)
        cr.commit()
        return True