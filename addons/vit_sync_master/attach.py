from osv import osv, fields
import base64
import zipfile
import platform
import os
import csv

class vit_sync_master_attach(osv.osv):
	_name = "vit.sync.master.attach"
	homedir = os.path.expanduser('~')

	def cron_process_unzip_sync(self, cr, uid, context=None):
		
		self.cek_folder(cr, uid, context)
		mail_message_obj 	= self.pool.get('mail.message')
		mail_message_obj_ids = mail_message_obj.search(cr,uid,[('subject','=','move.csv.zip'),('is_imported','=',False)], limit=5)
		
		if mail_message_obj_ids != []:
			##Cek folder dan buat folder bila belum ada##
			
			import pdb;pdb.set_trace()
			for mail_message_obj_id in mail_message_obj_ids:
				attachment_id = cr.execute('SELECT attachment_id FROM message_attachment_rel WHERE message_id = %i' % (mail_message_obj_id,))
				attachment_id = cr.fetchone()
				attachment = self.pool.get('ir.attachment').browse(cr, uid, attachment_id[0], context=context)

				#decode datas yang diperoleh
				file_data = base64.b64decode(attachment.datas)
				
				#buat file zip nya di path ex: /home/../move_zip/
				fz = open('%s/move_zip/move.csv.zip' % self.homedir,'wb').write(file_data)

				# import pdb;pdb.set_trace()
				with zipfile.ZipFile('%s/move_zip/move.csv.zip' % self.homedir, "r") as z:
					z.extractall("%s/move_zip/" % self.homedir)
				self.read_csv(cr, uid, mail_message_obj_id, context)


	def read_csv(self, cr, uid, mail_message_obj_id, context=None):
		import pdb;pdb.set_trace()
		#Simpan Di base_import_import
		csvfile = open('%s/move_zip/move.csv' % self.homedir,'r')
		# csvfile = open('%s/Documents/move2.csv' % self.homedir,'r')
		base_import_pool = self.pool.get('base_import.import')
		base_id = base_import_pool.create(cr, uid, {
			'file_type' : "text/csv",
            'file': csvfile.read(),
            'file_name': "move.csv",
            'res_model': 'account.move',
            })
		# fields = ['name', 'journal_id/.id', 'period_id/.id', 'ref', 'date', 'to_check', 'line_id/name']
		fields = ['name', 'journal_id', 'period_id', 'ref', 'date', 'to_check', 'line_id/name', 'line_id/quantity',
				  False, False, 'line_id/debit', 'line_id/credit', 'line_id/account_id', False, 'line_id/ref',
				  False, 'line_id/reconcile_id', False, False, False, False, False, 'line_id/journal_id', False, 'line_id/partner_id',
				  False, False, False, False, 'line_id/centralisation', False, False, False, False, False, False, False,
				  'line_id/name']

		options = {'headers': True, 'quoting': '"', 'separator': ',', 'encoding': 'utf-8'}
		import_csv = base_import_pool.do(cr, uid, int(base_id) , fields, options, dryrun=False, context=None)
		
		import pdb;pdb.set_trace()
		if isinstance(import_csv, list) or import_csv == []:
			self.set_imported(cr,uid,mail_message_obj_id,context)
		# if import_csv == []:
		# 	self.set_imported(cr,uid,mail_message_obj_id,context)



	####################################################################################
	# update to true 
	####################################################################################
	def set_imported(self, cr, uid, mail_message_obj_id, context=None):
		#update record jadi is_processed = True
		cr.execute("UPDATE mail_message set is_imported='t' where id = %s" % (mail_message_obj_id))


				
	####################################################################################
	#Cek Folder dan Buat bila tidak ada
	####################################################################################
	def cek_folder(self, cr, uid, context=None):
		if platform.system() == 'Linux':
			if not os.path.exists('%s/move_zip' % self.homedir):
				os.mkdir('%s/move_zip' % self.homedir)
				return True
	



	#############################################################
	#Create Journal Entries (account.move dan account.move.line)#
	#############################################################
	def create_journal_entries(self,cr,uid,lines,context):

		entries_id  = self.pool.get('account.move').create(cr,uid,{
			'date'			:	person_info[ 'date'][0],
		    'journal_id'	:	person_info[ 'journal_id'][0],
		    'period_id'		:	person_info[ 'period_id'][0],
			# 'date'			: temp.date,
		 #    'journal_id'	: journal_id,
		 #    'period_id'		:
		 #    'move_line_id'	: lines,
		    })		
		_logger.info("   created account move id:%d" % (entries_id) )
		return 




		# return base_id

		# with open('%s/move_zip/move.csv' % self.homedir, 'rb') as csv_data:
		# 	reader = csv.reader(csv_data)
		# 	# eliminate blank rows if they exist
		# 	rows = [row for row in reader if row]
  #   		headings = rows[0] # get headings
  #   		person_info = {}
  #   		for row in rows[1:]:
  #   		# append the dataitem to the end of the dictionary entry
  #       	# set the default value of [] if this key has not been seen
  #       		for col_header, data_column in zip(headings, row):
  #       			person_info.setdefault(col_header, []).append(data_column)
  #       	import pdb;pdb.set_trace()

  #       	entries_id  = self.pool.get('account.move').create(cr,uid,{
		# 			'date'			:	person_info[ 'date'][0],
		# 		    'journal_id'	:	person_info[ 'journal_id'][0],
		# 		    'period_id'		:	person_info[ 'period_id'][0],
		# 		    'line_id'		:	person_info[ 'line.name'],

		#     })


  #       	i = 0
  #       	while(i < len(person_info[ 'journal_id'])):
  #       		am_pool = self.pool.get('account.move')
		#         lines 			= []
		#         lines.append((0,0,{
		# 						'name'			:  person_info[ 'line.name'][i],
		# 						'account_id'	:  person_info[ 'line.account_id.code'][i],
		# 						})
		#         )

		        # am_pool.create(cr,uid,{
		        # 	'date'			:	person_info[ 'date'][0],
		        # 	'journal_id'	:	person_info[ 'journal_id'][0],
		        # 	'period_id'		:	person_info[ 'period_id'][0],
		        # 	# 'line_id'		:	lines,
		        # 	})
		        # entries_id 		= self.create_journal_entries(cr, uid, lines, context)

		        # self.pool.get('account.move').create(cr,uid,{
		        # 	'date'			:	person_info[ 'date'][i],
		        # 	'journal_id'	:	person_info[ 'journal_id'][i],
		        # 	'period_id'		:	person_info[ 'period_id'][i],
		        # 	'lines'			:	lines,
		        # 	}
		        # i+=1
		# self.create_journal_entries(cr,uid,person_info,context)
    		 


	
		

		