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
import datetime
import os

LOG_STATE = [
    ('success', 'Success'),
    ('failed', 'Failed'),
]


class ea_import_scheduler(osv.osv):
    _name = 'ea_import.scheduler'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'input_directory': fields.char('Input Directory', size=128, required=True),
        'log_ids': fields.one2many('ea_import.scheduler.log', 'scheduler_id', 'Logs'),
        'import_chain_id': fields.many2one('ea_import.chain', 'Import chain'),
        }

    def run_import(self, cr, uid, ids, context=None):
        context = {}
        log_notes = "*** Init Logging ***\n"
        log_notes += "********************\n"
        import_chain_obj = self.pool.get('ea_import.chain')
        log_obj = self.pool.get('ea_import.scheduler.log')
        result_obj = self.pool.get('ea_import.chain.result')

        for scheduler in self.browse(cr, uid, ids, context=context):

            files_to_import = os.listdir(scheduler.input_directory)

            # loop on file_name list
            for file_name in files_to_import:
                # setup file_name name
                file_name = os.path.join(scheduler.input_directory,  file_name)

                # create log record entry
                log_record = log_obj.create(cr, uid, {
                    'scheduler_id': scheduler.id,
                    'name': file_name,
                    'date_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                }, )

                # open the file_name
                try:
                    f = open(file_name, 'r')
                    log_notes += "Opening file_name - " + file_name + "\n"
                except IOError as e:
                    log_notes += "IO Error - " + e + " stopping import - FAILED!\n"
                    log_obj.write(cr, uid, [log_record], {'log_notes': log_notes, 'state': 'failed'})
                    break

                # load data from CSV file_name
                csv_data = f.read()

                # convert data into base64
                new_file_data = base64.encodestring(csv_data)

                # get the import chain id from the form
                chain_id = scheduler.import_chain_id.id

                # write converted data to the import chain input_file field
                import_chain_obj.write(cr, uid, [chain_id], {'input_file': new_file_data}, context=context)

                # run the import function
                try:
                    import_chain_obj.import_to_db(cr, uid, [chain_id], context=context)
                    log_notes += "Import completed successfully!\n"
                except:
                    log_notes += "Error with import_to_db function - stopping import - FAILED!\n"
                    log_notes += "Run this manually from Import Chains.  There is a problem with the contents of the CSV.\n"
                    log_obj.write(cr, uid, [log_record], {'log_notes': log_notes, 'state': 'failed'}, context=context)
                    break

                # write import results to log entry
                result_obj.write(cr, uid, context['result_ids'], {'scheduler_log_id': log_record, })

                # close file_name
                f.close()

                # delete the file_name
                try:
                    os.remove(file_name)
                    log_notes += "Deleting " + file_name + "\n"
                except OSError as e:
                    log_notes += "OS Error! " + e + " FILE NOT DELETED!\n"
                    log_obj.write(cr, uid, [log_record], {'log_notes': log_notes, 'state': 'failed'}, context=context)
                    break

                # write final log notes
                log_obj.write(cr, uid, [log_record], {'log_notes': log_notes, 'state': 'success'})
        return True


class ea_import_scheduler_log(osv.osv):

    _name = 'ea_import.scheduler.log'
    _order = 'date_time desc'
    _columns = {
        'name': fields.char('Name', size=256, required=True),
        'date_time': fields.datetime('Date',),
        'scheduler_id': fields.many2one('ea_import.scheduler', 'Scheduler ID'),
        'result_ids': fields.one2many('ea_import.chain.result', 'scheduler_log_id', 'Import Results', ),
        'log_notes': fields.text('Log Notes'),
        'state': fields.selection(LOG_STATE, 'State'),
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
