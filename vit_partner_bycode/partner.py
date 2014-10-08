from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class partner(osv.osv):
    _name = 'res.partner'
    _description = 'Partner'
    _inherit = "res.partner"

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        # import pdb;pdb.set_trace()
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like', '=like'):
            # search on the name of the contacts and of its company
            search_name = name
            if operator in ('ilike', 'like'):
                search_name = '%%%s%%' % name
            if operator in ('=ilike', '=like'):
                operator = operator[1:]
            query_args = {'name': search_name}
            limit_str = ''
            if limit:
                limit_str = ' limit %(limit)s'
                query_args['limit'] = limit
            # TODO: simplify this in trunk with _rec_name='display_name', once display_name
            # becomes a stored field
            cr.execute('''SELECT partner.id FROM res_partner partner
                          LEFT JOIN res_partner company ON partner.parent_id = company.id
                          WHERE partner.email ''' + operator +''' %(name)s OR
                             partner.code ''' + operator +''' %(name)s OR
                             CASE WHEN company.id IS NULL OR partner.is_company 
                                      THEN partner.name
                                  ELSE
                                      company.name || ', ' || partner.name
                             END
                          ''' + operator + ' %(name)s ' + limit_str, query_args)
            ids = map(lambda x: x[0], cr.fetchall())
            ids = self.search(cr, uid, [('id', 'in', ids)] + args, limit=limit, context=context)
            # import pdb;pdb.set_trace()
            if ids:
                return self.name_get(cr, uid, ids, context)

        return super(partner,self).name_search(cr, uid, name, args, operator=operator, context=context, limit=limit)

partner()