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

class school_teacher_assignment(osv.Model):
	
	_name = 'school.teacher.assignment'
	_description = 'Teacher Assignment Information'
	_columns = {
		'name': fields.char("Assignment Name", size = 30),
		'subject_id': fields.many2one("subject.subject","Subject",required=True),
		'standard_id': fields.many2one("school.standard","Standard"),
		'teacher_id': fields.many2one("hr.employee","Teacher",required=True),
		'assign_date': fields.date("Assign Date", required=True),
		'due_date': fields.date("Due Date", required=True),
		'attached_homework': fields.binary("Attached Home work"),
		'state': fields.selection([('draft','Draft'), ('active','Active')],"Status",readonly=True),
		'school_id':fields.related('standard_id','school_id',relation="school.school", string="School Name", type="many2one", store=True),
		'cmp_id':fields.related('school_id','company_id',relation="res.company", string="Company Name", type="many2one", store=True),
	}
	_defaults = {
		'state': lambda *a: 'draft'
	}
	
	def active_assignment(self, cr, uid, ids, context=None):
		'''  This method change state as active state and create assignment line
		@param self : Object Pointer
		@param cr : Database Cursor
		@param uid : Current Logged in User
		@param ids : Current Records
		@param context : standard Dictionary
		@return : True
		'''
		if context is None:
			context = {}
		assignment_obj = self.pool.get("school.student.assignment")
		std_obj = self.pool.get('student.student')
		for ass_data in self.browse(cr, uid, ids, context=context):
			std_ids = std_obj.search(cr, uid, [('standard_id', '=', ass_data.standard_id.id)], context=context)
			for std in std_obj.browse(cr, uid, std_ids, context=context):
				assignment_id = assignment_obj.create(cr, uid,{
									'name': ass_data.name,
									'subject_id': ass_data.subject_id.id,
									'standard_id': ass_data.standard_id.id,
									'assign_date': ass_data.assign_date,
									'due_date': ass_data.due_date,
									'state': 'active',
									'attached_homework': ass_data.attached_homework,
									'teacher_id': ass_data.teacher_id.id,
									'student_id' : std.id
								})
				if ass_data.attached_homework:
					data_attach = {
							'name': 'test',
							'datas':str(ass_data.attached_homework),
							'description': 'Assignment attachment',
							'res_model': 'school.student.assignment',
							'res_id': assignment_id,
						}
					self.pool.get('ir.attachment').create(cr, uid, data_attach, context=context)
			self.write(cr, uid, ids, {'state': 'active'}, context=context)
			return True

class school_student_assignment(osv.Model):

	_name = 'school.student.assignment'
	_description = 'Student Assignment Information'
	_columns = {
			
				'name': fields.char("Assignment Name", size = 30 ),
				'subject_id': fields.many2one("subject.subject","Subject",required=True),
				'standard_id': fields.many2one("school.standard","Standard",required=True),
				'teacher_id': fields.many2one("hr.employee","Teacher",required=True),
				'assign_date': fields.date("Assign Date" ,required=True),
				'due_date': fields.date("Due Date",required=True),
				'state': fields.selection([('draft','Draft'),('active','Active'),('done','done')],"Status",readonly = True),
				'student_id' : fields.many2one('student.student', 'Student', required=True),
				'attached_homework': fields.binary("Attached Home work"),
				
				}
			
	def done_assignment(self, cr, uid, ids, context=None):
		'''  This method change state as active state and create assignment line
		@param self : Object Pointer
		@param cr : Database Cursor
		@param uid : Current Logged in User
		@param ids : Current Records
		@param context : standard Dictionary
		@return : True
		'''
		if context is None:
			context = {}
		self.write(cr, uid, ids, {'state': 'done'}, context=context)
		return True

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
