import zipfile,os.path
import time
import logging
import csv
import glob

_logger = logging.getLogger(__name__)

DONE_FOLDER = '/done'

class ftp_utils(object):

	###########################################################
	# check or create done folder
	###########################################################
	def check_done_folder(self, folder):
		# check done folders
		if not os.path.exists(folder + DONE_FOLDER):
			os.makedirs(folder + DONE_FOLDER)


	###########################################################
	# unzip the uploaded file
	###########################################################
	def unzip(self, source_filename, dest_dir):
		files = []

		with zipfile.ZipFile(source_filename) as zf:
			for member in zf.infolist():
				words = member.filename.split('/')
				path = dest_dir
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word)
					head, word = os.path.split(word)
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word)
				zf.extract(member, path)
				files.append(member.filename)
				
		return files

	###########################################################
	# rename to done file
	###########################################################
	def done_filename(self, cr, uid, csv_file, context=None):
		basename = os.path.basename(csv_file)
		done = os.path.dirname(csv_file) + DONE_FOLDER + '/' + basename + '.' + context.get('date_start',False)
		return done 


	###########################################################
	# read csv, insert to dest_obj
	# according to fields_map
	###########################################################
	def read_csv_insert(self, cr, uid, csv_file, fields_map, dest_obj, 
		delimiter=',', quotechar='"', cron_id=False, cron_obj=False, context=None):

		paused = False
		i = 0
		row=[]
		last_row = 0 #what is the last CSV rows commited
		rows_per_batch=1000 # how many csv rows to commit

		try:
			#pause cron, exception if failed to pause
			self.pause_cron(cr,uid,cron_id,cron_obj,context=context)
			paused = True

			with open( csv_file, 'rb') as csvfile:
				spamreader = csv.reader(csvfile, delimiter= delimiter, quotechar=quotechar)
				i = 0
				for row in spamreader:
					if not row:
						continue					
					
					if i==0:
						_logger.warning("header")
						_logger.warning(row)
						if len(row) == 1:
							raise Exception('delimiter not match?') 
						i = i+1
						continue

					# start processing at last_row
					if i < last_row:
						i = i+1
						continue

					data = {}
					r = 0
					for field in fields_map:
						data.update({field: row[r]})
						r = r + 1

					data.update({"source": csv_file})
					dest_obj.create(cr, uid, data, context=context)
					#_logger.warning("insert %s" %(i));

					if i == last_row + rows_per_batch:
						last_row = last_row + rows_per_batch
						_logger.warning("commiting %s records and updating last_row to %s" , i, last_row)
						cr.commit()

					i = i +1

			return i

		except IOError as e:
			data = {
				'notes': "I/O error({0}): {1}".format(e.errno, e.strerror),
				'date_start' : context.get('date_start',False),
				'date_end' 	: time.strftime('%Y-%m-%d %H:%M:%S'),
				'input_file' : csv_file,
			}
			return data

		except Exception as e:
			data = {
				'notes': "Exception: %s @row:%s row=%s" % ( str( e ) , i , delimiter.join(row) ),
				'date_start' : context.get('date_start',False),
				'date_end' 	: time.strftime('%Y-%m-%d %H:%M:%S'),
				'input_file' : csv_file,
			}
			return data
		finally:
			if paused:
				self.resume_cron(cr, uid, cron_id, cron_obj, context=context)

	###########################################################
	# try to pause the cron job
	###########################################################
	def pause_cron(self,cr,uid,cron_id,cron_obj, context=None):
		if cron_obj:
			cron_obj.write(cr, uid ,cron_id,{'active': False}, context=context)
			cr.commit()

	###########################################################
	# resume the cron job
	###########################################################
	def resume_cron(self,cr,uid,cron_id,cron_obj, context=None):
		if cron_obj:
			cron_obj.write(cr, uid ,cron_id,{'active': True}, context=context)
			cr.commit()

	def insensitive_glob(self,pattern):
		# type: () -> object
		def either(c):
			return '[%s%s]'%(c.lower(),c.upper()) if c.isalpha() else c
		return glob.glob(''.join(map(either,pattern)))

