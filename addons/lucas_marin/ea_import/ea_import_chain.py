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
import base64
import csv
import datetime
from cStringIO import StringIO


def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, charset='utf-8', **kwargs):
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(utf_8_encoder(unicode_csv_data, charset),
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, charset) for cell in row]


def utf_8_encoder(unicode_csv_data, charset):
    for line in unicode_csv_data:
        yield line
        #yield line.decode(charset).encode('utf-8', 'ignore')


class ea_import_chain(osv.osv):

    _name = 'ea_import.chain'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'input_file': fields.binary('Test Importing File', required=False),
        'header': fields.boolean('Header'),
        'link_ids': fields.one2many('ea_import.chain.link', 'chain_id', 'Chain Links', ),
        'result_ids': fields.one2many('ea_import.chain.result', 'chain_id', 'Import Results', ),
        'separator': fields.selection([
            (",", '<,> - Coma'),
            (";", '<;> - Semicolon'),
            ("\t", '<TAB> - Tab'),
            (" ", '<SPACE> - Space'),
        ], 'Separator', required=True),
        'delimiter': fields.selection([
            ("'", '<\'> - Single quotation mark'),
            ('"', '<"> - Double quotation mark'),
            (None, 'None'),
        ], 'Delimiter', ),
        'charset': fields.selection([
            ('us-ascii', 'US-ASCII'),
            ('utf-7', 'Unicode (UTF-7)'),
            ('utf-8', 'Unicode (UTF-8)'),
            ('utf-16', 'Unicode (UTF-16)'),
            ('windows-1250', 'Central European (Windows 1252)'),
            ('windows-1251', 'Cyrillic (Windows 1251)'),
            ('iso-8859-1', 'Western European (ISO)'),
            ('iso-8859-15', 'Latin 9 (ISO)'),
        ], 'Encoding', required=True)
        }

    _defaults = {
        'separator': ",",
        'charset': 'utf-8',
        'delimiter': None,
    }


    def import_to_db(self, cr, uid, ids, context={}):
        time_of_start = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        context.update({'time_of_start': time_of_start})
        context['result_ids'] = []
        result_pool = self.pool.get('ea_import.chain.result')
        for chain in self.browse(cr, uid, ids, context=context):
            csv_reader = unicode_csv_reader(StringIO(base64.b64decode(chain.input_file)), delimiter=str(chain.separator), quoting=(not chain.delimiter and csv.QUOTE_NONE) or csv.QUOTE_MINIMAL, quotechar=chain.delimiter and str(chain.delimiter) or None, charset=chain.charset)
            if chain.header:
                csv_reader.next()
            result_ids = {}
            for chain_link in chain.link_ids:
                result_ids.update({chain_link.template_id.target_model_id.model: set([])})
            for record_list in csv_reader:
                for chain_link in sorted(chain.link_ids, key=lambda k: k.sequence):
                    result_id = chain_link.template_id.generate_record(record_list, context=context)
                    result_ids[chain_link.template_id.target_model_id.model] = result_ids[chain_link.template_id.target_model_id.model] | set(result_id)
            for model_name, ids_set in result_ids.iteritems():
                result_ids_file = base64.b64encode(str(list(ids_set)))
                result_ids = result_pool.create(cr, uid, {
                    'chain_id': chain.id,
                    'result_ids_file': result_ids_file,
                    'name': model_name,
                    'import_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                context['result_ids'].append(result_ids)
        return True

ea_import_chain()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
