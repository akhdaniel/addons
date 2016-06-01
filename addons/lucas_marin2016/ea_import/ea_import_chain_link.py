# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Enapps LTD (<http://www.enapps.co.uk>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import osv
from osv import fields


class ea_import_chain_link(osv.osv):
    _name = 'ea_import.chain.link'
    _order = 'sequence'
    _columns = {
        'chain_id': fields.many2one('ea_import.chain',),
        'template_id': fields.many2one('ea_import.template', 'Template',),
        'sequence': fields.integer('Sequence',),
        }

    _defaults = {
        'sequence': 1,
    }

    def name_get(self, cr, uid, ids, context={}):
        result = []
        for chain_link in self.browse(cr, uid, ids, context=context):
            chain_link_name = "%s/%s" % (chain_link.chain_id.name, chain_link.template_id)
            result.append((chain_link.id, chain_link_name))
        return result

    def default_get(self, cr, uid, fields, context={}):
        result = super(ea_import_chain_link, self).default_get(cr, uid, fields, context=context)
        chain_id = context.get('chain_id')
        result.update({'chain_id': chain_id, })
        return result

ea_import_chain_link()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
