# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp.osv import fields,osv
from openerp.tools.translate import _

class move_standards(osv.TransientModel):

    _name = 'move.standards'

    _columns = {
        'academic_year_id':fields.many2one('academic.year', 'Academic Year', required=True),
    }

    def move_start(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not context.get('active_ids'):
            return {}
        academic_obj = self.pool.get('academic.year')
        school_standard_obj = self.pool.get('school.standard')
        standard_obj = self.pool.get("standard.standard")
        result_obj = self.pool.get('exam.result')
        student_obj = self.pool.get('student.student')
        student_history_obj = self.pool.get("student.history")
        for data in self.browse(cr, uid, ids, context):
            for standards in school_standard_obj.browse(cr, uid, context.get('active_ids'), context):
                for student in standards.student_ids:
                    stud_year_ids = student_history_obj.search(cr, uid, [('academice_year_id', '=', data.academic_year_id.id), ('student_id', '=', student.id)])
                    year_id = academic_obj.next_year(cr, uid,  student.year.sequence, context)
                    if year_id and year_id != data.academic_year_id.id:
                        continue
                    if stud_year_ids:
                        raise osv.except_osv(_('Warning !'), _('Please Select Next Academic year.'))
                    else:
                        result_exists = result_obj.search(cr, uid, [('standard_id', '=', student.standard_id.id), ('standard_id.division_id', '=', student.division_id.id), ('standard_id.medium_id', '=', student.medium_id.id), ('student_id','=', student.id)])
                        if result_exists:
                            result_data = result_obj.browse(cr, uid, result_exists[0], context)
                            if result_data.result == "Pass":
                                next_class_id = standard_obj.next_standard(cr, uid, standards.standard_id.sequence, context)
                                if next_class_id:
                                    student_obj.write(cr, uid, student.id, {'year': data.academic_year_id.id,
                                                                            'standard_id': next_class_id,
                                                                            })
                                    student_history_obj.create(cr, uid, {'student_id':student.id,
                                                                         'academice_year_id':student.year.id,
                                                                         'standard_id': standards.standard_id.id,
                                                                         'division_id': standards.division_id.id,
                                                                         'medium_id': standards.medium_id.id,
                                                                         'result': result_data.result,
                                                                        'percentage': result_data.percentage})
                            else:
                                raise osv.except_osv(_("Error!"), _("Student is not eligible for Next Standard."))
        return {}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
