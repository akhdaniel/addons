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
import datetime
from tools.translate import _
import base64


class ea_import_template_line(osv.osv):

    _name = 'ea_import.template.line'
    _rec_name = 'target_field'

    def _get_related_field_model(self, cr, uid, ids, name, args, context=None):
        if not ids:
            return {}
        result = {}
        for template_line in self.browse(cr, uid, ids, context=context):
            result[template_line.id] = template_line.target_field.relation
        return result

    def _get_next_sequence(self, cr, uid, context={}):
        template_id = context.get('template_id')
        if template_id:
            cr.execute("""
                SELECT MAX(sequence) + 1
                FROM ea_import_template_line
                WHERE template_id = %s
                      """, (template_id, ))
            for (next_sequence, ) in cr.fetchall():
                return next_sequence or 1
        return 1

    _columns = {
        'target_field': fields.many2one('ir.model.fields', string="Field Name", select=True),
        'template_id': fields.many2one('ea_import.template', 'Template', select=True),
        'target_model_id': fields.related('template_id', 'target_model_id', type='many2one', relation='ir.model', string='Target Object', readonly=True, store=False,),
        'related_field': fields.many2one('ir.model.fields', string="Related Field", select=True),
        'related_field_model': fields.char('related_field_model', size=512,),
        'sequence': fields.integer('Sequence', required=True, select=True),
        'real_field_type': fields.related('target_field', 'ttype', type='char', relation='ir.model.fields', string='Field type', readonly=True, store=False,),
        'test_result_field': fields.char('Test Result', size=512,),
        'default_value': fields.char('Default Value', size=512,),
        'use_only_defaults': fields.boolean('Use only defaults',),
        'test_result_record_number': fields.integer('Record Number'),
        'key_field': fields.boolean('Key field for updating', select=True),
        'required': fields.boolean('Required for creating new', select=True),
        'calculated': fields.boolean('Calculated', select=True),
        'calc_field_ids': fields.one2many('ea_import.template.line.calc_field', 'template_line_id', 'Calculated Field',),
        'boolean_field_ids': fields.one2many('ea_import.template.line.boolean_field', 'template_line_id', 'Boolean Fields',),
        'replace': fields.boolean('Replace field before processing', select=True),
        'regexp_field_ids': fields.one2many('ea_import.template.line.regexp_field', 'template_line_id', 'Regexp Fields',),
        'header_column_name': fields.char('Header Column Name', size=64,),
        'time_format': fields.char('Time Format', size=128, help="""DIRECTIVE       MEANING
%a	Locale’s abbreviated weekday name.
%A	Locale’s full weekday name.
%b	Locale’s abbreviated month name.
%B	Locale’s full month name.
%c	Locale’s appropriate date and time representation.
%d	Day of the month as a decimal number [01,31].
%H	Hour (24-hour clock) as a decimal number [00,23].
%I	Hour (12-hour clock) as a decimal number [01,12].
%j	Day of the year as a decimal number [001,366].
%m	Month as a decimal number [01,12].
%M	Minute as a decimal number [00,59].
%p	Locale’s equivalent of either AM or PM.
%S	Second as a decimal number [00,61].
%U	Week number of the year (Sunday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Sunday are considered to be in week 0.
%w	Weekday as a decimal number [0(Sunday),6].
%W	Week number of the year (Monday as the first day of the week) as a decimal number [00,53]. All days in a new year preceding the first Monday are considered to be in week 0.
%x	Locale’s appropriate date representation.
%X	Locale’s appropriate time representation.
%y	Year without century as a decimal number [00,99].
%Y	Year with century as a decimal number.
%Z	Time zone name (no characters if no time zone exists).
%%	A literal '%' character.),"""),
        'field_type': fields.selection([('char', 'char'),
                                  ('text', 'text'),
                                  ('boolean', 'boolean'),
                                  ('integer', 'integer'),
                                  ('date', 'date'),
                                  ('datetime', 'datetime'),
                                  ('float', 'float'),
                                  ('selection', 'selection'),
                                  ('binary', 'binary'),
                                  ('many2one', 'many2one'),
                                 ], 'Field Type'),
        'many2one_rel_type': fields.selection([
            ('dbid', 'Database ID'),
            ('subfield', 'Subfield'),
            ('template', 'Template')
        ], 'Relation type',),
        'related_template_id': fields.many2one('ea_import.template', 'Related Template', select=True),
        }

    _defaults = {
        'time_format': '%d/%m/%Y',
        'sequence': lambda self, cr, uid, context: self._get_next_sequence(cr, uid, context=context),
        'many2one_rel_type': 'subfield',
        'default_value': None,
    }

    def name_get(self, cr, uid, ids, context={}):
        result = []
        for template_line in self.browse(cr, uid, ids, context=context):
            template_line_name = "%s/%s" % (template_line.target_model_id.name, template_line.related_field.name)
            result.append((template_line.id, template_line_name))
        return result

    def default_get(self, cr, uid, fields, context={}):
        result = super(ea_import_template_line, self).default_get(cr, uid, fields, context=context)
        template_id = context.get('template_id')
        target_model_id = context.get('target_model_id')
        result.update({'template_id': template_id, 'target_model_id': target_model_id})
        return result

    def onchange_target_field(self, cr, uid, ids, field_id, context={}):
        if field_id:
            model_fields_pool = self.pool.get('ir.model.fields')
            field_obj = model_fields_pool.browse(cr, uid, field_id, context=context)
            return {'value': {'field_type': field_obj.ttype, 'related_field_model': field_obj.relation}}
        else:
            return {'value': {}}

    def get_field(self, cr, uid, ids, input_list, context={}, testing=False):
        template_line_boolean_field_pool = self.pool.get('ea_import.template.line.boolean_field')
        template_line_regxp_field_pool = self.pool.get('ea_import.template.line.regexp_field')

        def test_many2one_result(result_list, template_line, target_string):
            if len(result_list) > 1:
                raise osv.except_osv(_('Error !'), _("For %s/%s relation there more then 1 record." % (template_line.target_field.field_description, template_line.related_field.field_description)))
            elif not result and template_line.target_field.required:
                raise osv.except_osv(_('Error !'), _("""Model - %s\nField - %s\nThere no related field '%s' in %s/%s relation (field is required)""" % (template_line.template_id.name, template_line.target_field.model, target_string, template_line.target_field.model, template_line.related_field.model)))

        for template_line in self.browse(cr, uid, ids, context=context):
            if not all([bool(field_str) == False for field_str in input_list]):
                if template_line.use_only_defaults:
                    target_string = template_line.default_value
                else:
                    target_string = input_list[template_line.sequence - 1]
                    if not target_string.strip() and template_line.default_value:
                        target_string = template_line.default_value
                if template_line.replace:
                    target_string = template_line_regxp_field_pool.replace_string(cr, uid,
                                                                                  [regexp_field.id for regexp_field in template_line.regexp_field_ids],
                                                                                  target_string, context=context)
                template_line_type = template_line.field_type
                if template_line.calculated and template_line_type in ['integer', 'float']:
                    calc_fields = sorted(template_line.calc_field_ids, key=lambda k: k.sequence)
                    result = float(input_list[calc_fields.pop(0).column_number - 1].strip() or "0")
                    for calc_field in calc_fields:
                        result = calc_field.calculate(result, input_list)
                    return result
                elif template_line_type in ['text', 'char']:
                    return target_string
                if template_line_type == 'selection':
                    return template_line.get_selection_from_name(target_string)
                if template_line_type == 'binary':
                    return base64.b32encode(target_string)
                elif template_line_type == 'integer':
                    return int(target_string)
                elif template_line_type == 'float':
                    return float(target_string)
                elif template_line_type == 'boolean':
                    if template_line.boolean_field_ids:
                        return template_line_boolean_field_pool.get_value(cr, uid,
                                                                          [boolean_field.id for boolean_field in template_line.boolean_field_ids],
                                                                          target_string, context=context)
                    else:
                        return bool(target_string)
                elif template_line_type == 'date':
                    try:
                        target_time = datetime.datetime.strptime(target_string, template_line.time_format)
                        return target_time.strftime("%Y-%m-%d")
                    except ValueError:
                        return None
                elif template_line_type == 'datetime':
                    try:
                        target_time = datetime.datetime.strptime(target_string, template_line.time_format)
                        return target_time.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        return None
                elif template_line_type == 'time':
                    try:
                        target_time = datetime.datetime.strptime(target_string, template_line.time_format)
                        return target_time.strftime("%H:%M:%S")
                    except ValueError:
                        return None
                elif template_line_type == 'many2one':
                    target_obj_pool = self.pool.get(template_line.target_field.relation)
                    if template_line.many2one_rel_type == 'dbid':
                        return int(target_string)
                    elif template_line.many2one_rel_type == 'subfield':
                        result = target_obj_pool.search(cr, uid, [(template_line.related_field.name, '=', target_string)], context=context)
                        if testing:
                            test_many2one_result(result, template_line, target_string)
                            return result and result[0] or False
                        elif not result:
                            return None
                        else:
                            return result[0]
                    elif template_line.many2one_rel_type == 'template':
                        result = template_line.related_template_id.get_related_id(input_list)
                        if testing:
                            test_many2one_result(result, template_line, target_string)
                        return result[0]
            else:
                continue

    def get_selection_from_name(self, cr, uid, ids, target_string, context={}):
        for template_line in self.browse(cr, uid, ids, context=context):
            target_model_pool = self.pool.get(template_line.target_model_id.model)
            selection_dict = dict(target_model_pool._columns[template_line.target_field.name].selection)
            revrese_selection_dict = dict((v, k) for k, v in selection_dict.iteritems())
            return revrese_selection_dict.get(target_string)

ea_import_template_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
