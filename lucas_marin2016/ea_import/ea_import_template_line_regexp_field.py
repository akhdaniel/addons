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
import re


class ea_import_template_line_regexp_field(osv.osv):
    _name = 'ea_import.template.line.regexp_field'

    _columns = {
        'template_line_id': fields.many2one('ea_import.template.line', 'Template Line',),
        'regexp': fields.char('Regexp', size=512, required="1",
                             help='''You can use all power of python regexp.
                              Simple example:
                                input string - "foo"
                                regexp - "foo"
                                replace_by - "bar"
                                =================
                                result - "bar"
                              Edvanced example:
                                input string - "football"
                                regexp - "foo.?"
                                replace_by - "bar"
                                =================
                                result - "barball"
                              Expert example:
                                input string - "ENAPPS is a cool company"
                                regexp - "(ENAPPS)( is )(a)(.*)( company)"
                                replace_by - '\\1 LTD\\2an awesome and\\4 British\\5'
                                =================
                                result - "ENAPPS LTD is an awesome and cool British company"
                              '''),
        'replace_by': fields.char('Replace by', size=512, required=True, ),
        }

    def replace_string(self, cr, uid, ids, target_string, context={}):
        for regexp_field in self.browse(cr, uid, ids, context=context):
            search_result = re.search(regexp_field.regexp, target_string)
            if search_result:
                return re.sub(regexp_field.regexp, regexp_field.replace_by, target_string)
        return target_string


ea_import_template_line_regexp_field()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
