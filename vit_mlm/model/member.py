from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

MEMBER_STATES =[('draft','Draft'),('open','Sedang Verifikasi'), ('reject','Ditolak'),
                 ('aktif','Aktif'),('nonaktif','Non Aktif')]
BONUS_SPONSOR_CODE   = 1
BONUS_PASANGAN_CODE  = 2
BONUS_LEVEL_CODE     = 3
BONUS_BELANJA	     = 4

'''
install

Install the contrib package: 
sudo apt-get install postgresql-contrib
sudo /etc/init.d/postgresql restart

masuk psql:
CREATE extension ltree;
ALTER table res_partner ADD column path_ltree ltree;
CREATE INDEX path_gist_res_partner_idx ON res_partner USING GIST(path_ltree);
CREATE INDEX path_res_partner_idx ON res_partner USING btree(path_ltree);
'''

class member(osv.osv):
	_name 		= "res.partner"
	_inherit 	= "res.partner"

	# untransfered
	def _total_bonus(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, False, 'False', context=context)
		return results

	def _total_bonus_sponsor(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '1', 'False', context=context)
		return results

	def _total_bonus_pasangan(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '2', 'False', context=context)
		return results

	def _total_bonus_level(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '3', 'False', context=context)
		return results

	def _total_bonus_belanja(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '4', 'False', context=context)
		return results	

	# trasfered
	def _total_bonus_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, False, 'True', context=context)
		return results

	def _total_bonus_sponsor_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '1', 'True', context=context)
		return results

	def _total_bonus_pasangan_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '2', 'True', context=context)
		return results

	def _total_bonus_level_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '3', 'True', context=context)
		return results

	def _total_bonus_belanja_transfered(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '4', 'True', context=context)
		return results	

	def _get_total_bonus(self, cr, uid, ids, code, transfer_status, context=None):
		bonus = False
		if code != False:
			bonus = self.pool.get('mlm.bonus').search(cr, uid, [('code','=', code )], context=context)
		def hitung_bonus(member,ids0,bonus):
			res={member.id : 0.0}
			for mb in self.pool.get('mlm.member_bonus').browse(cr,uid,ids0):
				if bonus:
					if mb.bonus_id.id == bonus[0]:
						res[member.id] = res[member.id] + mb.amount
				else:					
					res[member.id] = res[member.id] + mb.amount
			return res
		results = {}
		for m in self.browse(cr, uid, ids, context=context):
			untransfered_ids = [x.id for x in m.member_bonus_ids if (x.is_transfered == False)] 
			transfered_ids  = [y.id for y in m.member_bonus_ids if (y.is_transfered == True)] 
			if 	transfer_status == 'False':
				results = hitung_bonus(m,untransfered_ids,bonus)
			else :
				results = hitung_bonus(m,transfered_ids,bonus)
		return results	

	def _sale_order_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for partner in self.browse(cursor, user, ids, context=context):
			res[partner.id] = False
			if partner.sale_order_ids:
				res[partner.id] = True
		return res

	def _get_tree_url(self, cr, uid, ids, field, arg, context=None):
		results = {}
		for m in self.browse(cr, uid, ids, context=context):
			results[m.id] = '/mlm/member/tree/%d' % (m.id)
		return results	

	def _get_default_paket_produk(self, cr, uid, context=None):
		product_ids = []
		paket_ids = self.pool.get('mlm.paket_produk').search(cr,uid,[])
		for x in paket_ids:
			product_ids.append((0,0,{'paket_produk_id':x,'qty':0.0}))
		return product_ids

	def _cek_state(self, cr, uid, ids, name, arg, context=None):
		res = {}
		# state:draft,open,sale_wait,aktif
		for partner in self.browse(cr, uid, ids, context=context):
			if   partner.state == 'aktif' and partner.paket_id.is_upgradable:
				res[partner.id] = 'update'
			elif partner.state == 'open' and partner.sale_order_ids:
				res[partner.id] = '2baktif'
			elif partner.state == 'open':
				res[partner.id] = 'sale'
		return res

	_columns 	= {
		'path'				: fields.char("Path"),
		'code'				: fields.char("Member ID"),
		'parent_id' 		: fields.many2one('res.partner', 'Upline ID', required=False,states={'aktif':[('readonly',True)]}),
		'sponsor_id' 		: fields.many2one('res.partner', 'Sponsor ID', required=False,states={'aktif':[('readonly',True)]}),
		'member_bonus_ids' 	: fields.one2many('mlm.member_bonus','member_id','Member Bonuses', ondelete="cascade", readonly=True),
		'state'				: fields.selection(MEMBER_STATES,'Status',readonly=True,required=True),
		
		### paket join
		'paket_id'			: fields.many2one('mlm.paket', 'Join Paket', required=True, domain="[('is_submember','=',False)]",states={'aktif':[('readonly',True)]}),
		'paket_harga'		: fields.related('paket_id', 'price' , 
			type="float", relation="mlm.paket", string="Harga Paket"),
		'paket_cashback'		: fields.related('paket_id', 'cashback' , 
			type="float", relation="mlm.paket", string="Cashback Paket"),

		## paket barang
		'paket_produk_ids'	: fields.one2many('mlm.member_paket_produk','member_id', 'Paket Produk', states={'aktif':[('readonly',True)]}),
		# 'paket_produk_id'	: fields.many2one('mlm.paket_produk', 'Paket Produk', 
		# 	required=True),

		# untransfered
		'total_bonus' 				: fields.function(_total_bonus, string="Total Bonus"),
		'total_bonus_sponsor' 		: fields.function(_total_bonus_sponsor, string="Total Bonus Sponsor"),
		'total_bonus_pasangan' 		: fields.function(_total_bonus_pasangan, string="Total Bonus Pasangan"),
		'total_bonus_level' 		: fields.function(_total_bonus_level, string="Total Bonus Level"),
		'total_bonus_belanja' 		: fields.function(_total_bonus_belanja, string="Total Bonus Belanja"),
		# trasfered
		'total_bonus_transfered' 				: fields.function(_total_bonus_transfered, string="Total Bonus"),
		'total_bonus_sponsor_transfered' 		: fields.function(_total_bonus_sponsor_transfered, string="Total Bonus Sponsor"),
		'total_bonus_pasangan_transfered' 		: fields.function(_total_bonus_pasangan_transfered, string="Total Bonus Pasangan"),
		'total_bonus_level_transfered' 			: fields.function(_total_bonus_level_transfered, string="Total Bonus Level"),
		'total_bonus_belanja_transfered' 		: fields.function(_total_bonus_belanja_transfered, string="Total Bonus Belanja"),

		'is_stockist'		: fields.boolean("Is Stockist?"),
		'bbm'				: fields.char("BBM Pin"),
		'signature'			: fields.binary('Signature'),
		'bank_no'			: fields.char("Bank Account Number"),
		'bank_account_name'	: fields.char("Bank Account Name"),
		'bank_name'			: fields.char("Bank Name"),
		'bank_branch'		: fields.char("Bank Branch"),
		'id_number'			: fields.char("Nomor KTP/SIM"),

		'tree_url'	  		: fields.function(_get_tree_url, type="char", string="Tree URL"),

		'sale_order_ids'		: fields.one2many('sale.order','partner_id','Sale Orders'),
		'sale_order_exists'		: fields.function(_sale_order_exists, 
			string='Sales Order Ada',  
		    type='boolean', help="Apakah Partner ini sudah punya Sales Order."),	
		'start_join'		: fields.char("Start Join",readonly=True),
		'cek_state'		    : fields.function(_cek_state, type="char", method=True,
			string="Show/hide buttons", store=False, help="Show/hide buttons."),
	}
	_defaults = {
		'code'				: lambda obj, cr, uid, context: '/',		
		'state'				: MEMBER_STATES[0][0],
		'paket_produk_ids'	: _get_default_paket_produk,
		'cek_state'			: 'draft',
	}

	#########################################################################
	# cari MLM plan current company
	#########################################################################
	def get_mlm_plan(self, cr, uid, context=None):
		cid = self.pool.get('res.company')._company_default_get(cr, uid, context=context)
		company = self.pool.get('res.company').browse(cr, uid, cid, context=context)
		mlm_plan = company.mlm_plan_id
		if not mlm_plan:
			raise osv.except_osv(_('Warning'),_("Please set Company's MLM Plan") ) 
		return mlm_plan


	#####################################################################
	# cari upline dan level nya masing-masing 
	# sd level max_bonus_level_level
	# dan bukan type Affiliate, 
	# mulai dari top level paling atas
	# return array:
	#   0=id 	1=name 	2=path_ltree 	3=level-abs 	4=level-relative
	# 	0		Andi    001 			1 				-2
	# 	1 		Bani    001.002 		2 				-1
	#   2 		Doni    001.003 		2 				-1
	#####################################################################
	def cari_upline_dan_level(self, cr, uid, new_member, max_bonus_level_level, context=None):

		sql = "select id, name, path_ltree,\
				nlevel(path_ltree) as level,\
				nlevel(path_ltree) - nlevel('%s') as level\
				from res_partner as p where path_ltree @> '%s'\
				and id <> %d \
				order by path_ltree desc\
				limit %d" % (new_member.path, new_member.path, new_member.id, max_bonus_level_level)
		_logger.warning( sql )
		cr.execute(sql)
		rows = cr.fetchall()
		return rows

	#################################################################
	# cari total child per level 
	# hanya dihitung member yang sudah status Open (ada path nya)
	# return
	# level   children
	# 1       2  ---> 
	# 2       4 
	# 3       8
	# 4       5  ---> belum ada bonus level
	# 
	# jika jumlah child upline = 2: terjadi bonus pasangan
	#################################################################	
	def cari_child_per_level(self, cr, uid, upline_path, context=None):
		sql = "select nlevel(path_ltree) - nlevel('%s') as level, count(*)\
			from res_partner\
			where path_ltree ~ '%s.*{1,}'\
			group by level" % (upline_path,upline_path)
		cr.execute(sql)
		levels = cr.fetchall()	
		return levels

	#################################################################
	# cari detail nama2 child per level 
	# hanya dihitung member yang sudah status Open (ada path nya)
	# return
	# level   children
	# 1       [Banu, Dodo]
	# 2       [Banu0, Banu1]
	# 3       8
	# 4       5  ---> belum ada bonus level
	# 
	# jika jumlah child upline = 2: terjadi bonus pasangan
	#################################################################	
	def cari_detail_child_per_level(self, cr, uid, upline_path, context=None):
		sql = "select nlevel(path_ltree) - nlevel('%s') + 1 as level, id, name \
			from res_partner\
			where path_ltree ~ '%s.*{1,}'\
			order by level, id" % (upline_path,upline_path)
		cr.execute(sql)
		rows = cr.fetchall()
		# import pdb; pdb.set_trace()

		data={}
		members = []
		lev_lama = 0

		for lev in rows:
			if lev[0] != lev_lama:
				members = []
			members.append(lev[1]) 
			data.update({ lev[0] : members })
			lev_lama = lev[0] 

		_logger.warning( data )

		return data 

	def cari_direct_childs(self, cr, uid, upline_path, context=None):
		sql = "select id, name, path \
			from res_partner where\
			path_ltree ~ '%s.*{1,1}'" % (upline_path)
		cr.execute(sql)
		direct_childs = cr.fetchall() # 076; 083
		return direct_childs		

	#################################################################
	# cari total child per level di kiri dan kanan
	# hanya dihitung member yang sudah status Open (ada path nya)
	# return misal
	# 0:level   1:kiri 		2:kanan
	# 1      	1 			1
	# 2       	2 			2 
	# 3       	4 			4 
	# 4       	5	  		3 
	# 
	# jika jumlah child upline = 2: terjadi bonus pasangan
	#################################################################	
	def cari_child_per_level_kiri_kanan(self, cr, uid, upline_path, context=None):

		# cari direct child di kiri dan kanan
		# return array tdd:
		#	0: anak kiri 
		#	1: anak kanan
		direct_childs = self.cari_direct_childs(cr, uid, upline_path, context=context)

		# pada level 1: levels = {1:[ [1],[1] ]}
		levels = {
			1 : [
				1 if len(direct_childs)>0 else 0,
				1 if len(direct_childs)>1 else 0,
			]
		}

		# import pdb; pdb.set_trace()
		# cari child anak kiri dan anak kanan  per level
		# misalnya:
		kaki = 0

		for child in direct_childs: # 0:kiri - 1:kanan 
			data = {}
			child_per_level = self.cari_child_per_level(cr, uid, child[2], context=context)
			for r in child_per_level:
				lev = r[0] + 1 
				if lev in levels :
					data = {lev: levels[lev]}
				else:
					data = {lev: [0,0]}
				data[lev][kaki] = r[1]
				levels.update( data )
			kaki = kaki + 1
		return levels	


	#################################################################
	# cari detail nama-nama child per level di kiri dan kanan
	# hanya dihitung member yang sudah status Open (ada path nya)
	# return misal
	# 0:level   1:kiri 		2:kanan
	# 1      	[[Banu] 			[Dodo]]
	# 2       	[[Banu0, Banu1]		[Joko0,Joko1]]  
	# 3 dst....
	# 
	#################################################################	
	def cari_detail_child_per_level_kiri_kanan(self, cr, uid, upline_path, context=None):

		# cari direct child di kiri dan kanan
		# return array tdd:
		#	0: anak kiri 
		#	1: anak kanan
		direct_childs = self.cari_direct_childs(cr, uid, upline_path, context=context)

		kaki = 0
		levels = {}

		for child in direct_childs: # 0:kiri - 1:kanan 
			if kaki==0:
				levels.update( {1 : [[child[0]], [] ] })
			else:
				levels[1][1] = [ child[0] ]

			# nama2 child per setiap level: 
			# { 
			#    1: [list children level 1] 
			#    2: [list children level 2] 
			#    3: [list children level 3] 
			# }
			child_per_level = self.cari_detail_child_per_level(cr, uid, child[2], context=context)
			# import ipdb; ipdb.set_trace()

			for lev in child_per_level.keys():
				if lev in levels :
					data = {lev: levels[lev] } # [ [11,22], []]
				else:
					data = {lev: [[],[]] }
				data[lev][kaki] = child_per_level[lev]
				levels.update( data )

			kaki = kaki + 1
		return levels	

	#########################################################################
	# cari bonus sponsor, kalau ada >0 , masukkan ke tabel partner_bonus
	# dengan type 'sponsor'
	#########################################################################
	def hitung_bonus_sponsor(self, cr, uid, ids, context=None):
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)
		amount = mlm_plan.bonus_sponsor
		bonus_sponsor_percent_decrease = mlm_plan.bonus_sponsor_percent_decrease
		max_bonus_sponsor_level = 1000000 if mlm_plan.max_bonus_sponsor_level == 0 else mlm_plan.max_bonus_sponsor_level

		if amount == 0 :
			return True

		#####################################################################
		# sponsor langsung
		#####################################################################
		member_bonus 	= self.pool.get('mlm.member_bonus')
		new_member 		= self.browse(cr, uid, ids[0], context=context)
		sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
		member_bonus.addSponsor(cr, uid, new_member.id, sponsor.id, 
			amount, 'New Member Sponsor', context=context)

		#####################################################################
		# sponsor upline di atas sponsor langsung, x level ke atas sponsor
		# cari pake ltree path:
		# res_partner yang path nya <@ sponsor.path 
		#####################################################################

		if bonus_sponsor_percent_decrease != 0:
			upline = self.browse(cr, uid, new_member.parent_id.id, context=context)
			sql = "select id, name, path,\
				nlevel(path_ltree) - nlevel('%s') as level\
				from res_partner where path_ltree @> '%s'\
				order by path_ltree desc\
				limit %d" % (upline.path, upline.path , max_bonus_sponsor_level) 
			cr.execute(sql)
			pids = cr.fetchall()
			_logger.warning( sql )
			_logger.warning( pids )
			for p in pids:
				amount = amount * bonus_sponsor_percent_decrease
				member_bonus.addSponsor(cr, uid, new_member.id, p[0], 
					amount, "New Member, Up Level %d Sponsor" % (-p[3] + 1), context=context)

		return True


	#########################################################################
	# ini dijalankan waktu action_aktif suatu member baru.
	# untuk menghitung berapa bonus level bagi upline-upline nya
	# 
	# hitung dan cari bonus level, kalau ada, masukkan ke tabel partner_bonus
	# dengan type 'level'
	# 
	# syarat terjadinya bonus level: 
	# model full level:
	# 		pada level ke n [0..n], jumlah member aktif = 2^n
	# model minimal 1 kiri - kanan:
	# 		pada level ke n [0..n] jika jumlah grup kiri min 1 dan grup kanan min 1
	# logic:
	#		cari semua upline sd max_bonus_level limit
	#		setiap id upline: hitung berapa jumlah downlinenya
	#		jika belum ada bonus pada level tsb 
	#		modul full: jumlah downline == 2^level :
	#		model 1-1 kiri kanan : 
	#			maka si upline dapat bonus level
	#########################################################################
	def hitung_bonus_level(self, cr, uid, ids, zero_amount=False, context=None):
		mlm_plan 			= self.get_mlm_plan(cr, uid, context=context)
		full_level 			= mlm_plan.full_level
		amount_bonus_level 	= mlm_plan.bonus_level
		bonus_level_percent_decrease = mlm_plan.bonus_level_percent_decrease
		max_bonus_level_level = 1000000 if mlm_plan.max_bonus_level_level == 0 else mlm_plan.max_bonus_level_level

		cashback = ''

		bonus  = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_LEVEL_CODE)], context=context)
		if not bonus:
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus Level, code = 3") ) 
		bonus_level = bonus[0]

		####################################################################
		# apakah bonus level ada / aktif ?
		####################################################################
		if amount_bonus_level == 0:
			return True

		####################################################################
		# jika karena cashback memang sengaja bonus level=0
		####################################################################
		if zero_amount:
			amount_bonus_level = 0
			cashback = 'Cashback '

		new_member 		= self.browse(cr, uid, ids[0], context=context)
		member_bonus 	= self.pool.get('mlm.member_bonus')

		#################################################################
		# cari upline sd ke max level
		#################################################################
		uplines = self.cari_upline_dan_level(cr, uid, new_member, max_bonus_level_level, context=context)
		
		if full_level:
			#################################################################
			# loop masing-masing upline : dan cari berapa jumlah children 
			# per masing-masing level
			#################################################################
			for r in uplines:
				upline_id    = r[0]; upline_name  = r[1]; upline_path  = r[2]; upline_level = r[3]
				member_level = upline_level + 1
				levels = self.cari_child_per_level(cr, uid, upline_path, context=context)
				for l in levels:
					rel_level = l[0]; children = l[1]

					_logger.warning('Upline=%s, rel_level=%d, children=%d' % (upline_name, rel_level, children))
					
					# jika belum exists
					exist = ['&','&',('member_id','=',upline_id),('level','=',rel_level),
 						('bonus_id','=',bonus_level)]
					if not member_bonus.search(cr, uid, exist, context=context):
						# full level: harus jumlah child == 2^level
						if children == 2**rel_level:
							member_bonus.addBonusLevel(cr, uid, new_member.id, upline_id, rel_level,
								amount_bonus_level, "%sLevel %d" % (cashback, rel_level), context=context)
		
		else:
			#################################################################
			# loop setiap upline mulai dari yg paling atas:
			# dan cari jumlah children per masing-masing level di kiri dan kanan
			#################################################################
			for upline in uplines:
				import pdb;pdb.set_trace()
				upline_id    = upline[0]; upline_name  = upline[1]; upline_path  = upline[2]; upline_level = upline[3]
				levels = self.cari_child_per_level_kiri_kanan(cr, uid, upline_path, context=context)
				
				for lev in levels.keys():
					rel_level = lev; children_kiri = levels[lev][0]; children_kanan = levels[lev][1]
					# jika belum ada dan 
					# jika kiri =1 and kanan = 1: add bonus level
					if children_kiri >= 1 and children_kanan>=1:
						exist = ['&','&',('member_id','=',upline_id),('level','=',rel_level),
	 						('bonus_id','=',bonus_level)]
						if not member_bonus.search(cr, uid, exist, context=context):
							member_bonus.addBonusLevel(cr, uid, new_member.id, upline_id, rel_level,
								amount_bonus_level, "%sLevel %d" % (cashback, rel_level), context=context)

		return True 


	#########################################################################
	# ini dijalankan waktu action_aktif suatu member baru.
	# untuk menghitung berapa bonus pasangan bagi upline-upline nya
	# 
	# hitung dan cari bonus pasangan, kalau ada, masukkan ke tabel partner_bonus
	# dengan type 'pasangan'
	# 
	# syarat terjadinya bonus pasangan: 
	# 		pada level ke n [0..n], jumlah member aktif = 2
	# logic:
	#		cari semua upline sd max_bonus_pasangan limit
	#		setiap id upline: hitung berapa jumlah downlinenya
	#		jika belum ada bonus pada level tsb dan jumlah downline == 2^level :
	#			maka si upline dapat bonus level
	#########################################################################
	def hitung_bonus_pasangan(self, cr, uid, ids,  zero_amount=False, context=None):
		mlm_plan 		= self.get_mlm_plan(cr, uid, context=context)
		amount 			= mlm_plan.bonus_pasangan 
		bonus_pasangan_percent_decrease = mlm_plan.bonus_pasangan_percent_decrease
		max_bonus_pasangan_level = 1000000 if mlm_plan.max_bonus_pasangan_level == 0 else mlm_plan.max_bonus_pasangan_level
		if amount == 0:
			return True

		bonus = self.pool.get('mlm.bonus').search(cr, uid, 
			[('code','=',BONUS_PASANGAN_CODE)], context=context)
		if not bonus:
			raise osv.except_osv(_('Error'),_("Belum ada definisi Bonus Pasangan, code = 2") ) 
		bonus_pasangan=bonus[0]

		####################################################################
		# jika karena cashback memang sengaja bonus level=0
		####################################################################
		if zero_amount:
			amount = 0
			cashback = 'Cashback '
		else:
			cashback=''

		new_member 		= self.browse(cr, uid, ids[0], context=context)
		member_bonus 	= self.pool.get('mlm.member_bonus')

		#################################################################
		# cari upline sd ke max level
		#################################################################
		uplines = self.cari_upline_dan_level(cr, uid, new_member, max_bonus_pasangan_level, context=context)
		for upline in uplines:
			upline_id    = upline[0]; upline_name  = upline[1]; upline_path  = upline[2]; upline_level = upline[3]
			
			#################################################################
			# si upline punya child siapa saja di kiri dan di kanan
			# bentuk levels: { level : [ [list kiri], [list kanan] ]}
			#################################################################
			levels = self.cari_detail_child_per_level_kiri_kanan(cr, uid, upline_path, context=context)
			
			#################################################################
			# apakah child di kiri sudah punya pasangan child di kanan
			# pada level suatu level ?
			# jika belum , tambahkan bonus pasangan untuk si upline
			#################################################################
			# import pdb; pdb.set_trace()n

			for lev in levels.keys():
				kiris = levels[lev][0]
				kanans = levels[lev][1]
 				
 				for kiri in kiris:
 					search = ['&','&',('new_member_id','=', kiri),('level', '=',lev),
 						('bonus_id','=',bonus_pasangan)]
 					exist = member_bonus.search(cr, uid, search, context=context)
 					if not exist:
	 					for kanan in kanans:
		 					search = ['&','&',('match_member_id', '=',kanan),('level', '=',lev),
		 						('bonus_id','=',bonus_pasangan)]
		 					exist = member_bonus.search(cr, uid, search, context=context)
		 					if not exist:
		 						desc = '%sPasangan' % (cashback)
		 						member_bonus.addBonusPasangan(cr, uid, kiri, kanan, 
		 							upline_id, lev, amount, desc, context=context)
		 						cr.commit()
		 						break

		return True 


	#########################################################################
	# max downline sesuai mlm_plan
	#########################################################################
	def cek_max_downline(self, cr, uid, parent_id, context=None):
		#########################################################################
		# cek mlm_plan
		#########################################################################
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)

		#########################################################################
		# cek max level upline , kalau masih boleh tambah downline,
		# isikan nilai path 
		#########################################################################
		upline = self.browse(cr, uid, int(parent_id), context=context)
		max_downline = mlm_plan.max_downline
		downline = 0
		if max_downline != 0:
			for child in upline.child_ids:
				if child.state not in ['draft','nonaktif']:
					downline = downline + 1

			if downline >= max_downline:
				raise osv.except_osv(_('Warning'),_("%s: maximum downline for the current MLM plan is %d" % 
					(upline.name, max_downline))) 

		return True 


	#########################################################################
	# create : cek max downline, set path
	#########################################################################
	def create(self, cr, uid, vals, context=None):
		####################################################################
		# parent create()
		#####################################################################
		if 'parent_id' in vals:
			self.cek_max_downline(cr, uid, vals['parent_id'], context=context)
		paket_ids=[]
		produk_ids = self.pool.get('mlm.paket_produk').search(cr,uid,[])
		if 'paket_produk_qtyA' in vals:
			paket_ids.append((0,0,{'paket_produk_id':produk_ids[0],'qty':int(vals['paket_produk_qtyA'])}))
		if 'paket_produk_qtyB' in vals:
			paket_ids.append((0,0,{'paket_produk_id':produk_ids[1],'qty':int(vals['paket_produk_qtyB'])}))
		if 'paket_produk_qtyC' in vals:
			paket_ids.append((0,0,{'paket_produk_id':produk_ids[2],'qty':int(vals['paket_produk_qtyC'])}))
		vals.update({'paket_produk_ids':paket_ids})
		members_categ = self.pool.get('res.partner.category').search(cr, uid, [('name','=','Members')], context=context)
		paket = self.pool.get('mlm.paket').browse(cr,uid,int(vals['paket_id']))
		start_join = paket.name or ''
		vals.update({
			'customer':True,
			'supplier':True,
			'is_company':True,
			'start_join':start_join
		})
		if members_categ:
			vals.update({
				'category_id': [(4, members_categ[0])]
		})
		# import pdb;pdb.set_trace()
		new_id = super(member, self).create(cr, uid, vals, context=context)

		return new_id
	
	#########################################################################
	# create user secara manual
	# bawaan odoo: waktu create user otomatis terbentuk res_partner
	#########################################################################
	def create_user(self, cr, uid, member, context=None):
		alias_id = 1 

		sql = "INSERT INTO ""res_users"" (""id"", ""partner_id"", \
			""alias_id"", ""share"", ""active"", ""company_id"", \
			""action_id"", ""display_employees_suggestions"", \
			""default_section_id"", ""password"", \
			""display_groups_suggestions"", ""signature"", \
			""login"", ""create_uid"", ""write_uid"", \
			""create_date"", ""write_date"") \
			VALUES (nextval('res_users_id_seq'), \
			%d, %d, false, true, %d, NULL, true, NULL, '', \
			true, NULL, '%s', %d, %d, (now() at time zone 'UTC'), \
			(now() at time zone 'UTC')) RETURNING id" % (member.id, alias_id,member.company_id,
			 member.name.lower(),uid,uid)
		res = cr.execute(sql)

		user_id = cr.fetchall()

		group =  self.pool.get('res.groups')
		gids =group.search(cr, uid, [('name','in',['Employee','Contact Creation',
			'MLM / Member',
			'Portal'])], context=context)

		for gid in gids:
			sql = "insert into res_groups_users_rel (uid,gid) values (%d, %d)" % (user_id[0][0], gid)
			res = cr.execute(sql)

		# default company
		sql = "insert into res_company_users_rel (user_id,cid) values (%d, 1)"% (user_id[0][0])
		res = cr.execute(sql)

		return res 

	def name_get(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		if isinstance(ids, (int, long)):
			ids = [ids]
		res = []
		for record in self.browse(cr, uid, ids, context=context):
			name = record.name
			if record.parent_id:
				name = "%s" % (name)
			if context.get('show_address_only'):
				name = self._display_address(cr, uid, record, without_company=True, context=context)
			if context.get('show_address'):
				name = name + "\n" + self._display_address(cr, uid, record, without_company=True, context=context)
			name = name.replace('\n\n','\n')
			name = name.replace('\n\n','\n')
			if context.get('show_email') and record.email:
				name = "%s <%s>" % (name, record.email)
			res.append((record.id, name))
		return res

	#########################################################################
	#resset to "draft" state
	#########################################################################
	def action_draft(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[0][0]},context=context)
	
	#########################################################################
	#set to "open" state, diverifikasi
	#########################################################################
	def action_confirm(self,cr,uid,ids,context=None):

		#########################################################################
		# cek max downline sesuai mlm_plan
		#########################################################################
		new_member = self.browse(cr, uid, ids[0], context=context)
		upline = new_member.parent_id

		#########################################################################
		# cek upline sudah state aktif?
		#########################################################################
		if upline and upline.state not in ['open','aktif']:
			raise osv.except_osv(_('Warning'),
				"Cannot confirm member %s, upline %s is not Open"%(new_member.name,upline.name) ) 

		#########################################################################
		# cek max downline si upline
		#########################################################################
		self.cek_max_downline(cr, uid, upline.id, context=context)

		#########################################################################
		# generate code and path
		#########################################################################
		if context is None:
			context = {}
		new_code = self.pool.get('ir.sequence').get(cr, uid, 'mlm.member') or '/'

		if upline.path:
			new_path = "%s.%s" % (upline.path, new_code)
		else:
			new_path = "%s" % (new_code)

		self.write(cr,uid,ids[0],{
			'code' : new_code,
			'path' : new_path,
			'state': MEMBER_STATES[1][0]}, context=context)
		
		#########################################################################
		# update path_ltree 
		#########################################################################		
		cr.execute("update res_partner set path_ltree = '%s' where id=%d" % 
			(new_path, ids[0]) )
		cr.commit()

		#########################################################################
		# generate sub members and confirm
		#########################################################################		
		if new_member.paket_id.hak_usaha > 1:
			self.generate_sub_member(cr, uid, ids, context=context)

		return ids[0]

	#########################################################################
	# bentuk sub member akibat dari paket join (khusus binary plan)
	#########################################################################
	def generate_sub_member(self, cr, uid, ids, context=None):
		mlm_plan     = self.get_mlm_plan(cr, uid, context=context)
		max_downline = mlm_plan.max_downline

		new_member   = self.browse(cr, uid, ids[0], context=context)
		paket        = new_member.paket_id
		hak_usaha    = paket.hak_usaha
		childs       = []

		parent_id 	 = new_member.id 
		sponsor_id 	 = new_member.sponsor_id.id

		jc = 0
		parent_index = 0
		paket_sub_member = self.pool.get('mlm.paket').search(cr,uid,[('code','=',99)],limit=1)[0]

		for i in range(0, hak_usaha-1):
			data = {
				'code'			: '/',
				'parent_id'		: parent_id,
				'sponsor_id'	: sponsor_id,
				'name'			: "%s %d" % (new_member.name, i),
				'is_company'	: True,
				'start_join'	: new_member.paket_id.name,
				'paket_id'		: paket_sub_member
			}
			new_sub_id = self.create(cr, uid, data, context=context)
			childs.append(new_sub_id)

			# jd = jumlah children
			jc = jc + 1

			if jc >= max_downline:
				parent_id = childs[parent_index]
				parent_index = parent_index + 1
				jc = 0

			# confirm langsung 
			self.action_confirm(cr,uid,[new_sub_id],context=context)

		return True 

	#########################################################################
	# pada masing2 sub member, jalankan action_aktif
	# supaya menghitung bonus level tapi dengan amount=0
	#########################################################################
	def activate_sub_member(self, cr, uid, ids, context=None):
		mlm_plan     = self.get_mlm_plan(cr, uid, context=context)

		#####################################################################
		# titik yang membeli paket
		#####################################################################
		new_member 	 = self.browse(cr, uid, ids[0], context=context)
		paket        = new_member.paket_id
		hak_usaha    = paket.hak_usaha

		#######################################################################
		# si sponsor (new_member) paket dapat bonus sponsor langsung sebanyak 
		# = hak_usaha * bonus_sponsor
		#######################################################################
		bonus_sponsor 	= mlm_plan.bonus_sponsor
		member_bonus 	= self.pool.get('mlm.member_bonus')
		sponsor 		= self.browse(cr, uid, new_member.sponsor_id.id, context=context)
		amount 			= hak_usaha * bonus_sponsor
		member_bonus.addSponsor(cr, uid, new_member.id, sponsor.id, 
			amount, '%d x Bonus Sponsor Paket %s' % (hak_usaha, paket.name), context=context)

		#######################################################################
		# hitung bonus level utk masing2 titik 
		# hitung bonus pasangan utk masing2 titik 
		# nilainya 0 saja karena sudah dijadikan cashback pada waktu join
		#######################################################################
		sql = "select id, name,path from res_partner where \
			path_ltree <@ '%s' and id<>%d \
			order by path_ltree " % (new_member.path, new_member.id)
		cr.execute(sql)
		pids = cr.fetchall()
		for p in pids:
			self.hitung_bonus_level(cr, uid, [ p[0] ], zero_amount=True, context=context)
			self.hitung_bonus_pasangan(cr, uid, [ p[0] ], zero_amount=True,context=context)
			self.write(cr, uid, [p[0]], {'state':'aktif'}, context=context)


		return True

	#########################################################################
	#set to "reject" state
	#########################################################################
	def action_reject(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[2][0]},context=context)
		
	#########################################################################
	#set to "draft" state
	#########################################################################
	def action_cancel(self,cr,uid,ids,context=None):
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[0][0]},context=context)
	
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
		self.hitung_bonus_level(cr, uid, ids, context=context)
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[4][0]},context=context)


	#########################################################################
	# create sales order berisi produk-produk yang sesuai dengan paket_produk
	# yang dipilih pada saat join
	#########################################################################
	def action_create_sale_order(self,cr,uid,ids,context=None):
		#################################################################
		# partner
		#################################################################
		partner = self.browse(cr, uid, ids[0], context)
		paket_produk_ids = partner.paket_produk_ids

		#################################################################
		# compose sale_order lines 
		#################################################################
		lines = []
		isi_paket = 0
		jml_paket = partner.paket_id.hak_usaha
		for paket in paket_produk_ids:
			paket_qty = paket.qty or 0.0
			if paket_qty == 0.0:
				continue
			isi_paket+=paket_qty
			for detail in paket.paket_produk_id.paket_produk_detail_ids:
				lines.append((0,0,{
					'product_id'		: detail.product_id.id,
					'product_uom'		: detail.uom_id.id,
					'name'				: detail.product_id.name,
					'product_uom_qty' 	: detail.qty * paket_qty,
					'price_unit' 		: detail.product_id.lst_price,
				}))
		if not lines:
			return False 

		if isi_paket != jml_paket:
			raise osv.except_osv(_('Warning'),_("Jumlah paket produk tidak sesuai dengan join paket %s" % (partner.paket_id.name))) 
		
		#################################################################
		# sale_order object
		#################################################################
		sale_order_obj = self.pool.get("sale.order")

		#################################################################
		# create sale_order 
		#################################################################
		data= {
			'partner_id'			: partner.id,
			'partner_invoice_id' 	: partner.id,
			'partner_shipping_id' 	: partner.id,
			'date_order'			: time.strftime("%Y-%m-%d %H:%M:%S") ,
			'order_line' 			: lines,
			'origin'				: 'Paket Produk Member: %s' % (partner.name)
		}
		sale_order_id = sale_order_obj.create(cr, uid, data, context=context)
		
		return sale_order_id

	def _generate_new_path(self, cr, uid, path, context=None):	
		new_code = self.pool.get('ir.sequence').get(cr, uid, 'mlm.member') or '/'
		if path:
			new_path = "%s.%s" % (path, new_code)
		else:
			new_path = "%s" % (new_code)
		return {'new_path':new_path,'new_code':new_code}

	def _cari_data_bds_ltree_level(self, cr, uid, path_ltree, start_lv, context=None):
		sql = """SELECT id, path_ltree, path, \
				nlevel(path_ltree) as alevel, \
				nlevel(path_ltree) - nlevel('%s') as rlevel \
				FROM res_partner as p \
				where path_ltree ~ '%s.*{%d,}' \
				order by path_ltree""" % (path_ltree,path_ltree,start_lv)
		cr.execute(sql)
		rows = cr.fetchall() 
		return rows
	
	def update_path_ltree(self, cr, uid, path, res_id, context=None):
		cr.execute("update res_partner set path_ltree = '%s' where id=%d" % 
			(path, res_id) )
		cr.commit()

	#########################################################################
	# upgrade 1 level
	#########################################################################
	def action_upgrade(self, cr, uid, ids, context=None):
		upline = self.browse(cr, uid, ids[0], context)
		paket  = upline.paket_id

		if not paket.is_upgradable:
			raise osv.except_osv(_('Error!'), _('Paket %s tidak bisa diupgrade!') % (paket.name))
		
		# paket yg akan diisikan ke member yg diupdate
		new_code 		= str(int(paket.code) + 1)
		paket_obj 		= self.pool.get('mlm.paket')
		new_paket_id  	= paket_obj.search(cr,uid,[('code','=',new_code)])[0]

		max_downline 	= upline.company_id.mlm_plan_id.max_downline
		hu_baru 		= paket_obj.browse(cr,uid,new_paket_id,).hak_usaha
		member_to_add 	= hu_baru - paket.hak_usaha

		if member_to_add == 0:
			return self.write(cr,uid,ids[0],{'paket_id':new_paket_id})
		
		direct_src = self.search(cr,uid,[('parent_id','=',upline.id)])
		direct_childs = self.browse(cr,uid,direct_src,)
		if direct_childs:
			for child in direct_childs: child.write({'parent_id':False})

		new_data 		= {}
		new_childs 		= []
		i = len(self.search(cr,uid,[('name','ilike',upline.name)])) - 1
		paket_sub_member = self.pool.get('mlm.paket').search(cr,uid,[('is_submember','=',True)],limit=1)[0]
		# kiri :0 kanan: 1
		kaki = 0
		dc_path=[]

		while len(new_childs) < member_to_add:
			kode = self._generate_new_path(cr,uid,upline.path,context=None)
			new_data = {
				'code'			: kode['new_code'],
				'path'			: kode['new_path'],
				'parent_id'		: upline.id,
				'sponsor_id'	: upline.sponsor_id.id,
				'name'			: "%s %d" % (upline.name,i),
				'is_company'	: True,
				'start_join'	: upline.paket_id.name,
				'paket_id'		: paket_sub_member,
				'state'			: MEMBER_STATES[1][0],
				}
			new_id = self.create(cr, uid, new_data, context=context)
			new_childs.append(new_id)
			dc_path.append(kode['new_path'])
			i+=1
			if direct_childs and kaki == 0 :
				self.write(cr,uid,direct_childs[0].id,{'parent_id':new_id})
			elif direct_childs and kaki == 1 :
				self.write(cr,uid,direct_childs[1].id,{'parent_id':new_id})
			if member_to_add > max_downline:
				kode = self._generate_new_path(cr,uid,kode['new_path'],context=None)
				new_data.update({
					'code'			: kode['new_code'],
					'path'			: kode['new_path'],
					'parent_id'		: new_id,
					'name'			: "%s %d" % (upline.name,i)
				})
				new_sub_id=self.create(cr, uid, new_data, context=context)
				new_childs.append(new_sub_id)
				dc_path.append(kode['new_path'])
				i+=1
			kaki+=1		
		kiri=False
		cur_update_member_path=upline.path
		if new_childs and direct_childs:
			# kaki kiri dan kanan diproses masing2
			for dc in direct_childs:
				# all member kiri saja/kanan saja
				member_to_update = self._cari_data_bds_ltree_level(cr, uid, dc.path, 0, context=None) #res: id,ltree,path
				if kiri :
					new_id_path = dc_path[len(dc_path)-1:][0]
				else: 
					new_id_path = dc_path[:1][0]
					kiri = True
				for mem in member_to_update:
					# new_path = upline.path+(upline.path(awal-len(self.path)))
					this_old_path = mem[2]
					new_path = new_id_path + this_old_path[len(cur_update_member_path):]
					self.write(cr,uid,mem[0],{'path':new_path})
					self.update_path_ltree(cr, uid, new_path,mem[0],context=None)
		 			# increment lv bonus lv
		 			# for bonus in self.browse(cr, uid, mem[0], context).member_bonus_ids:
	 				# 	bonus.write({'level':bonus.level+1})
		for bonus in upline.member_bonus_ids:
			if bonus.level != 0 :
				self.pool.get('mlm.member_bonus').write(cr,uid,bonus.id,{'level':bonus.level+1})

		bp = self.pool.get('mlm.bonus').search(cr,uid,[('code','=',2)],limit=1)[0]
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)
		amount = mlm_plan.bonus_pasangan

		if len(new_childs)==2:
			self.pool.get('mlm.member_bonus').create(cr,uid,{
				'member_id': upline.id,
				'new_member_id': new_childs[1],
				'match_member_id': new_childs[0],
				'amount': amount,
				'trans_date': time.strftime("%Y-%m-%d %H:%M:%S"),
				'bonus_id': bp,
				'is_transfered': False,
				'description': "Pasangan",
				'level':1})
		elif len(new_childs)==4:
			for k in range(0, 2):
				self.pool.get('mlm.member_bonus').create(cr,uid,{
					'member_id': upline.id,
					'new_member_id': new_childs[k],
					'match_member_id': new_childs[k+2],
					'amount': amount,
					'trans_date': time.strftime("%Y-%m-%d %H:%M:%S"),
					'bonus_id': bp,
					'is_transfered': False,
					'description': "Pasangan",
					'level':k+1})
		# uplines = self.cari_upline_dan_level(cr, uid, new_member, max_bonus_level_level, context=context)
		
		# jika new child = 2, add bonus lv 0, bonus pasangan 0 untuk upline
		# jika new child = 4
		#######################################################################
		# hitung bonus level utk masing2 titik 
		# hitung bonus pasangan utk masing2 titik 
		# nilainya 0 saja karena sudah dijadikan cashback pada waktu join
		#######################################################################
		if new_childs:
			for child in new_childs:
				# self.hitung_bonus_level(cr, uid, [child], zero_amount=True, context=context)
				# self.hitung_bonus_pasangan(cr, uid, [ child ], zero_amount=True,context=context)
				self.write(cr, uid, [child], {'state':'aktif'}, context=context)

		self.write(cr,uid,ids[0],{'paket_id':new_paket_id})
		return True 