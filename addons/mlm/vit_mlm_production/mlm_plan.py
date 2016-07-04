from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

MEMBER_STATES =[('draft','Draft'),('open','Sedang Verifikasi'), ('reject','Ditolak'),
				 ('aktif','Aktif'),('nonaktif','Non Aktif')]

class mlm_plan(osv.osv):
	_inherit	= "mlm.mlm_plan"

	_columns 	= {
		'bonus_produksi': fields.float("Bonus Production (%)",
			help='Bonus percentage from joining package price'),
			# help='Bonus persentase dari harga join paket'),
		'max_bonus_produksi_level'	: fields.integer('Max Bonus Production Depth (Up)',
			help='Number of levels (up) where Upline still get the Production Bonus, fill with 0 if only it''s sponsor got the bonus'),
			# help='Berapa jumlah level (keatas) dimana Upline masih dapat Bonus Production, isi dengan 0 jika yang mendapatkan bonus hanya sponsornya saja'),
		'bonus_produksi_percent_decrease': fields.float("Bonus Production Percent Decrease",
			help='Number of percent decrease of the Production Bonus for each level up. Fill with 0.0-1.0. The value 1.0 means no decrease'),		
			# help='Berapa persen penurunan Bonus Production untuk setiap level ke atasnya. Isi dengan 0.0-1.0, nilai 1 artinya tidak ada penurunan'),		

	}


class member(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"

	# untransfered
	def _total_bonus_produksi(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '7', 'False', context=context)
		return results


	# trasfered
	def _total_bonus_produksi_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '7', 'True', context=context)
		return results


	_columns 	= {
		# untransfered
		'total_bonus_produksi' 					: fields.function(_total_bonus_produksi, string="Total Bonus Production"),

		# trasfered
		'total_bonus_produksi_transfered' 		: fields.function(_total_bonus_produksi_transfered, string="Total Bonus Production"),

		# field yang menentukan apakah pernah memberi bonus produksi ke sponsor_id (dari invoice pertama)
		'is_bonus_produksi'						: fields.boolean('Terima Bonus Production?', readonly=True)
		}

	def hitung_bonus_produksi(self, cr, uid, ids, context=None):
		
		mlm_plan 						= self.get_mlm_plan(cr, uid, context=context)
		presentase_bns 					= mlm_plan.bonus_produksi
		max_bonus_produksi_level		= mlm_plan.max_bonus_produksi_level
		bonus_produksi_percent_decrease	= mlm_plan.bonus_produksi_percent_decrease
		new_member 						= self.browse(cr, uid, ids[0], context=context)

		
		if presentase_bns == 0 :
			return True

		###########################################################################################
		#Cek invoice atas nama bersangkutan harus sudah berstatus paid untuk mendapatkan bonus ini
		###########################################################################################
		inv_obj		= self.pool.get('account.invoice')
		inv_id		= inv_obj.search(cr,uid,[('partner_id','=',ids[0])],context=context)
		
		############################################################################
		# cari id invoice pertama atau yg paling kecil (invoice pendaftaran member),
		# dan setting batasan upline di isi kurang dari atau sama dengan nol
		############################################################################
		if inv_id and max_bonus_produksi_level <= 0.00 :
			inv_id_pertama = sorted(inv_id)[0]
			inv_id_state = inv_obj.browse(cr, uid, inv_id_pertama, context=context).state
			if inv_id_state == 'paid' :

				#####################################################################
				# bonus produksi langsung
				#####################################################################
				member_bonus 	= self.pool.get('mlm.member_bonus')				
				sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
				bns_produksi 	= (new_member.paket_id.price * presentase_bns) /100
				member_bonus.addBonusProduction(cr, uid, new_member.id, sponsor.id, 
					bns_produksi, 'New Member Bonus Production Paket %s' % (new_member.paket_id.name), context=context)

				##############################################
				#beri status bahwa sdh terima bonus produksi
				##############################################
				self.write(cr,uid,ids[0],{'is_bonus_produksi':True},context=context)

		elif inv_id and max_bonus_produksi_level > 0.00 :
			inv_id_pertama = sorted(inv_id)[0]
			inv_id_state = inv_obj.browse(cr, uid, inv_id_pertama, context=context).state
			if inv_id_state == 'paid' : 
				######################################################################################################################################
				# cari upline sd ke max level
				######################################################################################################################################
				# tulis ulang sql ini karena jika memanggil fungsi aslinya komen "-- and (is_affiliate <> 't' or is_affiliate is null)" masih terbaca
				######################################################################################################################################
				sql = "select id, name, path_ltree,\
						nlevel(path_ltree) as level,\
						nlevel(path_ltree) - nlevel('%s') as level\
						from res_partner as p where path_ltree @> '%s'\
						and id <> %d \
						order by path_ltree desc\
						limit %d" % (new_member.path, new_member.path, new_member.id, max_bonus_produksi_level)
				_logger.warning( sql )
				cr.execute(sql)
				upline1 = cr.fetchall()

				#################################################################
				# loop setiap upline mulai dari yg paling atas:
				#################################################################				
				member_bonus 	= self.pool.get('mlm.member_bonus')
				for upline in upline1:
					upline_id    = upline[0]; upline_name  = upline[1]; upline_path  = upline[2]; upline_level = upline[3]
					#import pdb;pdb.set_trace()
					#####################################################################
					# bonus produksi bertingkat ke atas (upline)
					#####################################################################
					bns_produksi 	= (new_member.paket_id.price * presentase_bns) /100
					member_bonus.addBonusProduction(cr, uid, new_member.id, upline_id, 
						bns_produksi, 'New Member Bonus Production Paket %s' % (new_member.paket_id.name), context=context)						

				##############################################
				#beri status bahwa sdh terima bonus produksi
				##############################################
				self.write(cr,uid,ids[0],{'is_bonus_produksi':True},context=context)							

		return True


	#########################################################################
	#set to "aktif" state
	#########################################################################
	def action_aktif(self,cr,uid,ids,context=None):

		#########################################################################
		# yang mau diaktifkan
		#########################################################################		
		new_member = self.browse(cr, uid, ids[0], context=context)

		#########################################################################
		# create user 
		#########################################################################		
		self.create_user(cr, uid, new_member, context=context)

		#########################################################################
		# hitung bonus level utk upline si new_member
		#########################################################################
		self.hitung_bonus_level(cr, uid, ids, context=context)

		#########################################################################
		# hitung bonus pasangan utk upline si new_member
		#########################################################################		
		self.hitung_bonus_pasangan(cr, uid, ids, context=context)

		#########################################################################
		# hitung bonus produksi utk yang mensponsori si new_member
		#########################################################################
		self.hitung_bonus_produksi(cr, uid, ids, context=context)

		#########################################################################
		# langsung commit database, supaya bisa hitung sub member
		#########################################################################		
		cr.commit()

		#########################################################################
		# hitung bonus sponsor:
		# process paket join, khusus binary plan saja
		# jika lebih dari satu titik, maka bonus sponsor milik yg mensponsori
		#########################################################################		
		if new_member.paket_id:

			if new_member.paket_id.hak_usaha == 1:
				#########################################################################
				# hitung bonus sponsor utk yang mensponsori si new_member
				#########################################################################
				self.hitung_bonus_sponsor(cr, uid, ids, context=context)

			else:
				#########################################################################
				# aktivasi sub member di bawahnya, 
				# hitung bonus sponsor yang mensponsori
				# hitung bonus level untuk setiap titik dengan nilai 0 (cashback)
				# hitung bonus pasangan untuk setiap titik dengan nilai 0 (cashback)
				#########################################################################
				self.activate_sub_member(cr, uid, ids, context=context)


		return self.write(cr,uid,ids,{'state':MEMBER_STATES[3][0]},context=context)


	#########################################################################
	#set to "nonaktif" state
	#########################################################################
	def action_nonaktif(self,cr,uid,ids,context=None):
		self.hitung_bonus_sponsor(cr, uid, ids, context=context)
		self.hitung_bonus_produksi(cr, uid, ids, context=context)
		self.hitung_bonus_level(cr, uid, ids, context=context)
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[4][0]},context=context)	


	####################################################################################################
	# Cron Job Bonus Production yang mengecek invoice pertama pada member baru
	# jika invoice pertama paid, field is_bonus_produksi = False, berikan bonus produksi ke sponsor_id
	####################################################################################################
	def cron_bonus_produksi(self, cr, uid, context=None):

		mlm_plan 						= self.get_mlm_plan(cr, uid, context=context)
		presentase_bns 					= mlm_plan.bonus_produksi
		max_bonus_produksi_level		= mlm_plan.max_bonus_produksi_level
		bonus_produksi_percent_decrease	= mlm_plan.bonus_produksi_percent_decrease
		
		presentase_bns = mlm_plan.bonus_produksi
		member_ids = self.search(cr,uid,[('state','=','aktif'),('is_bonus_produksi','=',False)],context=context)
		#import pdb;pdb.set_trace()
		if presentase_bns == 0 or member_ids == [] :
			return True

		new_member_ids = self.browse(cr, uid, member_ids, context=context)
		for member in new_member_ids:
			#inv_id = inv_obj.search(cr, uid, [('partner_id','=',member.id),('state','=','paid')], context=context)
			# if inv_id :
			# 	inv_pertama = sorted(inv_id)[0]
			# 	#####################################################################
			# 	# bonus produksi langsung
			# 	#####################################################################
			# 	member_bonus 	= self.pool.get('mlm.member_bonus')
			# 	new_member 		= self.browse(cr, uid, member.id, context=context)
			# 	sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
			# 	bns_produksi 	= (new_member.paket_id.price * presentase_bns) /100
			# 	member_bonus.addBonusProduction(cr, uid, new_member.id, sponsor.id, 
			# 		bns_produksi, 'New Member Bonus Production Paket %s' % (new_member.paket_id.name), context=context)

			# 	#bri status bahwa sdh terima bonus produksi
			# 	self.write(cr,uid,member.id,{'is_bonus_produksi':True},context=context)     

			###########################################################################################
			#Cek invoice atas nama bersangkutan harus sudah berstatus paid untuk mendapatkan bonus ini
			###########################################################################################
			inv_obj			= self.pool.get('account.invoice')
			inv_id 			= inv_obj.search(cr, uid, [('partner_id','=',member.id),('state','=','paid')], context=context)
			
			############################################################################
			# cari id invoice pertama atau yg paling kecil (invoice pendaftaran member),
			# dan setting batasan upline di isi kurang dari atau sama dengan nol
			############################################################################
			if inv_id and max_bonus_produksi_level <= 0.00 :
				inv_id_pertama = sorted(inv_id)[0]
				inv_id_state = inv_obj.browse(cr, uid, inv_id_pertama, context=context).state
				if inv_id_state == 'paid' :

					#####################################################################
					# bonus produksi langsung
					#####################################################################
					member_bonus 	= self.pool.get('mlm.member_bonus')				
					sponsor 		= self.browse(cr, uid, member.sponsor_id.id, context=context)
					bns_produksi 	= (member.paket_id.price * presentase_bns) /100
					member_bonus.addBonusProduction(cr, uid, member.id, sponsor.id, 
						bns_produksi, 'New Member Bonus Production Paket %s' % (member.paket_id.name), context=context)

					##############################################
					#beri status bahwa sdh terima bonus produksi
					##############################################
					self.write(cr,uid,member.id,{'is_bonus_produksi':True},context=context)

			elif inv_id and max_bonus_produksi_level > 0.00 :
				inv_id_pertama = sorted(inv_id)[0]
				inv_id_state = inv_obj.browse(cr, uid, inv_id_pertama, context=context).state
				if inv_id_state == 'paid' : 
					######################################################################################################################################
					# cari upline sd ke max level
					######################################################################################################################################
					# tulis ulang sql ini karena jika memanggil fungsi aslinya komen "-- and (is_affiliate <> 't' or is_affiliate is null)" masih terbaca
					######################################################################################################################################
					sql = "select id, name, path_ltree,\
							nlevel(path_ltree) as level,\
							nlevel(path_ltree) - nlevel('%s') as level\
							from res_partner as p where path_ltree @> '%s'\
							and id <> %d \
							order by path_ltree desc\
							limit %d" % (member.path, member.path, member.id, max_bonus_produksi_level)
					_logger.warning( sql )
					cr.execute(sql)
					upline1 = cr.fetchall()

					#################################################################
					# loop setiap upline mulai dari yg paling atas:
					#################################################################				
					member_bonus 	= self.pool.get('mlm.member_bonus')
					for upline in upline1:
						upline_id    = upline[0]; upline_name  = upline[1]; upline_path  = upline[2]; upline_level = upline[3]
						
						#####################################################################
						# bonus produksi bertingkat ke atas (upline)
						#####################################################################
						bns_produksi 	= (member.paket_id.price * presentase_bns) /100
						member_bonus.addBonusProduction(cr, uid, member.id, upline_id, 
							bns_produksi, 'New Member Bonus Production Paket %s' % (member.paket_id.name), context=context)						


					##############################################
					#beri status bahwa sdh terima bonus produksi
					##############################################
					self.write(cr,uid,member.id,{'is_bonus_produksi':True},context=context)	


		return True


####################################################################
#partner_bonus:
#
#Terisi ketika ada konfirmasi pendaftaran member baru (on aktivate partner).
#
#Proses nya:
#1. cek bisnis plan yg aktiv
#2. dari dan isikan bonus sponsor ke sponsor_id
#3. cari dan isikan bonus level ke upline_id
#4. dari dan isikan bonus pasangan ke upline_id dan sponsor_id
#
####################################################################

BONUS_PRODUKSI	     = 7

class member_bonus(osv.osv):
	_inherit 		= "mlm.member_bonus"

	def addBonusProduction(self, cr, uid, new_member_id, sponsor_id, bns_produksi, description, context=None):

		bonus_produksi = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_PRODUKSI)], context=context)
		if not bonus_produksi:
			raise osv.except_osv(_('Error'),_("No Production Bonus defined, code = 8") ) 

		data = {
			'member_id' 		: sponsor_id ,   # yang dapat bonus
			'new_member_id' 	: new_member_id, # sumber member 
			'level' 			: False, # pada level berapa
			'amount'			: bns_produksi,        # jumlah
			'trans_date'		: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'bonus_id'			: bonus_produksi[0],
			'is_transfered'		: False,
			'description' 		: description
		}
		self.pool.get('mlm.member_bonus').create(cr, uid, data, context=context)		