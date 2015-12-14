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
{
    "name" : "Exam Management",
    "version" : "2.0",
    "author" : "Serpent Consulting Services Pvt. Ltd.",
    "website" : "http://www.serpentcs.com",
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to manage the school examination:
        1. Define Exam Timetable
        2. Conduct Exams
        3. Generate Results
""",
    "depends" : [
            "timetable"
        ],
    "data" : [
            "exam_view.xml",
            "exam_sequence.xml",
            "security/ir.model.access.csv",
            "report/exam_report_view.xml",
            "wizard/exam_class_result.xml",
            "wizard/exam_create_result_view.xml",
            "wizard/subject_result.xml",
            "report/add_exam_result_view.xml",
        ],
    "installable": True,
    "application": True,
    'demo': [
             "demo/exam_demo.xml"
             ],
    'test':[
            "test/exam_test.yml"
        ],
    "auto_install": False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=