from osv import osv, fields
import base64
import zipfile

class vit_sync_master_attach(osv.osv):
	_name = "vit.sync.master.attach"

	def cron_process_unzip_sync(self, cr, uid, context=None):
		import pdb;pdb.set_trace()
		mail_message_obj 	= self.pool.get('mail.message')
		mail_message_obj_ids = mail_message_obj.search(cr,uid,[('subject','=','move.csv.zip')])
		
		for mail_message_obj_id in mail_message_obj_ids:
			attachment_id = cr.execute('SELECT attachment_id FROM message_attachment_rel WHERE message_id = %i' % (mail_message_obj_id,))
			attachment_id = cr.fetchone()
			attachment = self.pool.get('ir.attachment').browse(cr, uid, attachment_id[0], context=context)

			#decode datas yang diperoleh
			file_data = base64.b64decode(attachment.datas)
			
			#buat file zip nya di path ex: /home/wn/move_zip/
			fz = open('/home/wn/move_zip/move.csv.zip','wb').write(file_data)
			with zipfile.ZipFile('/home/wn/move_zip/move.csv.zip', "r") as z:
				z.extractall("/home/wn/move_zip/")

			pass

		

		