import zipfile,os.path

DONE_FOLDER = '/done'

class ftp_utils(object):

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

