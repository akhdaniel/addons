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
		'bonus_produksi': fields.float("Bonus Produksi (%)",help='Bonus persentase dari harga join paket'),

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
		'total_bonus_produksi' 					: fields.function(_total_bonus_produksi, string="Total Bonus Produksi"),

		# trasfered
		'total_bonus_produksi_transfered' 		: fields.function(_total_bonus_produksi_transfered, string="Total Bonus Produksi"),

		# field yang menetukan apakah pernah memberi' bonus produksi ke sponsor_id (dari invoice pertama)
		'is_bonus_produksi'						: fields.boolean('Terima Bonus Produksi?', readonly=True)
		}

	def hitung_bonus_produksi(self, cr, uid, ids, context=None):
		
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)
		presentase_bns = mlm_plan.bonus_produksi
		#import pdb;pdb.set_trace()
		if presentase_bns == 0 :
			return True

		#Cek invoice atas nama bersangkutan harus sudah berstatus paid untuk mendapatkan bonus ini
		inv_obj		= self.pool.get('account.invoice')
		inv_id		= inv_obj.search(cr,uid,[('partner_id','=',ids[0])],context=context)
		if inv_id :
			#cari id invoice pertama atau yg paling kecil (invoice pendaftaran member)
			inv_id_pertama = sorted(inv_id)[0]
			inv_id_state = inv_obj.browse(cr, uid, inv_id_pertama, context=context).state
			if inv_id_state == 'paid' :
				#####################################################################
				# bonus produksi langsung
				#####################################################################
				member_bonus 	= self.pool.get('mlm.member_bonus')
				new_member 		= self.browse(cr, uid, ids[0], context=context)
				sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
				bns_produksi 	= (new_member.paket_id.price * presentase_bns) /100
				member_bonus.addBonusProduksi(cr, uid, new_member.id, sponsor.id, 
					bns_produksi, 'New Member Bonus Produksi Paket %s' % (new_member.paket_id.name), context=context)

				#bri status bahwa sdh terima bonus produksi
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


	##############################################################################
	# Cron Job Bonus Produksi yang mengecek invoice pertama pada member baru
	# jika invoice pertama paid, field is_bonus_produksi = False, berikan bonus produksi ke sponsor_id
	def cron_bonus_produksi(self, cr, uid, context=None):
		inv_obj = self.pool.get('account.invoice')
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)
		
		presentase_bns = mlm_plan.bonus_produksi
		#import pdb;pdb.set_trace()
		if presentase_bns == 0 :
			return True

		member_ids = self.search(cr,uid,[('state','=','aktif'),('is_bonus_produksi','=',False)],context=context)
		for member in self.browse(cr, uid, member_ids, context=context):
			inv_id = inv_obj.search(cr, uid, [('partner_id','=',member.id),('state','=','paid')], context=context)
			if inv_id :
				inv_pertama = sorted(inv_id)[0]
				#####################################################################
				# bonus produksi langsung
				#####################################################################
				member_bonus 	= self.pool.get('mlm.member_bonus')
				new_member 		= self.browse(cr, uid, member.id, context=context)
				sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
				bns_produksi 	= (new_member.paket_id.price * presentase_bns) /100
				member_bonus.addBonusProduksi(cr, uid, new_member.id, sponsor.id, 
					bns_produksi, 'New Member Bonus Produksi Paket %s' % (new_member.paket_id.name), context=context)

				#bri status bahwa sdh terima bonus produksi
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

	def addBonusProduksi(self, cr, uid, new_member_id, sponsor_id, bns_produksi, description, context=None):

		bonus_produksi = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_PRODUKSI)], context=context)
		if not bonus_produksi:
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus Produksi, code = 8") ) 

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