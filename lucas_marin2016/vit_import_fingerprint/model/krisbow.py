from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)


class krisbow(osv.osv):
    _name = "vit.krisbow"
    _columns = {
        'number': fields.char("No"),  # 000001
        'machine_no': fields.char("Machine No"),  # 1
        'fingerprint_code'	: fields.char("Fingerprint Code") ,# 000000117
        'name': fields.char("Name"),  # Dian Nurhadi
        'field5': fields.char("Field5"),  # 1
        'field6': fields.char("Field6"),  # 0
        'date': fields.char("Date"),  # 2016/02/25 hh:mm:ss

        'is_imported': fields.boolean('Is Imported'),
        'notes': fields.char("Notes"),
        'date_processed': fields.date("Date Processed"),
    }

    def action_import(self, cr, uid, context=None):
        active_ids = context and context.get('active_ids', False)
        if not context:
            context = {}

        self.actual_import(cr, uid, active_ids, context=context)

    def cron_import(self, cr, uid, context=None):
        import_krisbow_limit = self.pool.get('ir.config_parameter').get_param(cr, uid, 'import_krisbow_limit') or 10000
        _logger.warning('running cron krisbow, limit=%s' % import_krisbow_limit)

        active_ids = self.search(cr, uid, [
            ('is_imported', '=', False),
        ], limit=int(import_krisbow_limit), order="number asc", context=context)
        if active_ids:
            self.actual_import(cr, uid, active_ids, context=context)
        else:
            print "no logs to import"
        return True

    ################################################################
    # the import process
    # baca record ids, insert ke partner dengan field sesuai
    # PARTNER_MAPPING
    ################################################################
    def actual_import(self, cr, uid, ids, context=None):
        i = 0
        ex = 0

        att_obj = self.pool.get('hr.attendance')
        emp_obj = self.pool.get('hr.employee')

        cr.execute("delete from hr_tampung_error")

        for import_krisbow in self.browse(cr, uid, ids, context=context):

            # cari jadwal / shift dari kontrak karyawan berdasarkan fingerprint_code dan machine_no
            #    employee -> contract -> shift_ids (from to) -> schedule_id (hour_from - hour_to)
            # bandingkan dengan jam masuk : jika dekat dengan jam masuk => Sign in
            # else bandingkan dengan jam keluar: jika dekat dengan jam keluar => Sign Out
            # jika tidak ada Sign in / Out , anggap default , ada notes
            # finally insert into hr.attendance
            # date format = 2016/02/25 16:53:48

            fingerprint_code = int(import_krisbow.fingerprint_code)
            no_mesin = int(import_krisbow.machine_no)

            emp_id = emp_obj.search(cr, uid, [
                ('fingerprint_code', '=', fingerprint_code),
                ('no_mesin', '=', no_mesin)
            ], context=context)

            # import pdb; pdb.set_trace()
            if not emp_id:
                self._write_note(cr, uid, import_krisbow, "employee not found")
                ex = ex + 1
                continue

            emp = emp_obj.browse(cr, uid, emp_id[0], context=context)

            lokasi_kerja = emp.work_location2

            try:
                log_date = datetime.strptime(import_krisbow.date, "%Y/%m/%d %H:%M:%S") if import_krisbow.date else False
            except ValueError:
                self._write_note(cr, uid, import_krisbow, "date format error, should be %Y/%m/%d %H:%M:%S")
                ex = ex + 1
                continue

            data = {
                'fingerprint_code': fingerprint_code,
                'no_mesin': no_mesin,
                'name': log_date.strftime("%Y-%m-%d %H:%M:%S"),
                'lokasi_kerja': lokasi_kerja,
            }
            att_obj.create(cr, uid, data, context=context)

            # commit per record
            cr.execute("update vit_krisbow set is_imported='t', date_processed=NOW() where id=%s" % import_krisbow.id)
            cr.commit()
            i = i + 1

        _logger.info('Done creating %s partner and skipped/updated %s' % (i, ex))


    def _write_note(self, cr, uid, import_krisbow, notes, context=None):
        self.write(cr, uid, import_krisbow.id, {'notes': notes}, context=context)
        cr.commit()
        return
