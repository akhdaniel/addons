import logging
from datetime import datetime


_logger = logging.getLogger(__name__)

class converter(object):

	def convert_date(self, cr, uid, rec_obj, record, fieldname, format_string, ex, context=None):
		date_obj = False
		in_string = getattr(record, fieldname)
		rec_id = getattr(record, "id")
		try:
			date_obj = datetime.strptime(in_string, format_string)
		except ValueError:
			rec_obj.write(cr, uid, rec_id, {'notes': '%s: date format error, use %s' % (fieldname,format_string)}, context=context)
			ex = ex + 1
			cr.commit()

		return date_obj

	def convert_float(self,cr, uid, rec_obj,record, fieldname, thousands, decimals, ex, context=None):
		float_data = False
		in_string = getattr(record, fieldname)
		rec_id = getattr(record, "id")
		try:
			in_string=in_string.strip()
			float_data = float(in_string)
		except ValueError:
			rec_obj.write(cr, uid, rec_id, {'notes': '%s: float format error: use "%s" and "%s" as thousands and decimal separator, eg 1,000.00' % (fieldname,thousands,decimals)}, context=context)
			ex = ex + 1
			cr.commit()

		return float_data