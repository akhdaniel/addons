from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

MEMBER_STATES =[('draft','Draft'),('open','Sedang Verifikasi'), ('reject','Ditolak'),
                 ('aktif','Aktif'),('nonaktif','Non Aktif')]

'''
insstall

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

	def _total_bonus(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, False, context=context)
		return results

	def _total_bonus_sponsor(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, 1, context=context)
		return results

	def _total_bonus_pasangan(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, 2, context=context)
		return results

	def _total_bonus_level(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '3', context=context)
		return results

	def _total_bonus_belanja(self, cr, uid, ids, field, arg, context=None):
		results = self._get_total_bonus(cr, uid, ids, '4', context=context)
		return results	

	def _get_total_bonus(self, cr, uid, ids, code, context=None):
		bonus = False
		if code != False:
			bonus = self.pool.get('mlm.bonus').search(cr, uid, [('code','=', code )], context=context)

		results = {}
		for m in self.browse(cr, uid, ids, context=context):
			results[m.id] = 0.0
			for mb in m.member_bonus_ids:
				if bonus:
					if mb.bonus_id.id == bonus[0]:
						results[m.id] = results[m.id] + mb.amount
				else:					
					results[m.id] = results[m.id] + mb.amount

		return results	

	_columns 	= {
		'path'				: fields.char("Path"),
		'code'				: fields.char("Member ID"),
		'parent_id' 		: fields.many2one('res.partner', 'Upline ID', required=False),
		'sponsor_id' 		: fields.many2one('res.partner', 'Sponsor ID', required=False),
		'member_bonus_ids' 	: fields.one2many('mlm.member_bonus','member_id','Member Bonuses', ondelete="cascade"),
		'state'				: fields.selection(MEMBER_STATES,'Status',readonly=True,required=True),
		'paket_id'			: fields.many2one('mlm.paket', 'Join Paket', required=True),
		'is_affiliate'  	: fields.boolean('Affiliate Member ?', help="Hanya mendapat bonus sponsor saja"),

		'total_bonus' 				: fields.function(_total_bonus, string="Total Bonus"),
		'total_bonus_sponsor' 		: fields.function(_total_bonus_sponsor, string="Total Bonus Sponsor"),
		'total_bonus_pasangan' 		: fields.function(_total_bonus_pasangan, string="Total Bonus Pasangan"),
		'total_bonus_level' 		: fields.function(_total_bonus_level, string="Total Bonus Level"),
		'total_bonus_belanja' 		: fields.function(_total_bonus_belanja, string="Total Bonus Belanja"),

		'is_stockist'		: fields.boolean("Is Stockist?"),
		'bbm'				: fields.char("BBM Pin"),
		'signature'			: fields.binary('Signature'),
		'bank_no'			: fields.char("Bank Account Number"),
		'bank_account_name'	: fields.char("Bank Account Name"),
		'bank_name'			: fields.char("Bank Name"),
		'bank_branch'		: fields.char("Bank Branch"),
		'id_number'			: fields.char("Nomor KTP/SIM"),

	}
	_defaults = {
		'code'				: lambda obj, cr, uid, context: '/',		
		'state'				: MEMBER_STATES[0][0],
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
				and (is_affiliate <> 't' or is_affiliate is null)\
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

		# level 1: levels = {1:(1,1)}
		levels = {
			1 : [
				1 if len(direct_childs)>0 else 0,
				1 if len(direct_childs)>1 else 0,
			]
		}

		# import pdb; pdb.set_trace()
		# cari jumlah child anak kiri dan anak kanan  per level
		# misalnya:
		# Andi
		# 		level 1: 1  1
		#		level 2: 2  2
		#		level 3: 4  4
		# Badu
		# 		level 1: 1  0
		#		level 2: 2  1
		#		level 3: 4  3
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
					exist = [('member_id','=',upline_id),('level','=',rel_level)]
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
				upline_id    = upline[0]; upline_name  = upline[1]; upline_path  = upline[2]; upline_level = upline[3]
				levels = self.cari_child_per_level_kiri_kanan(cr, uid, upline_path, context=context)
				# import pdb; pdb.set_trace()
				for lev in levels.keys():
					rel_level = lev; children_kiri = levels[lev][0]; children_kanan = levels[lev][1]
					# jika belum ada dan 
					# jika kiri =1 and kanan = 1: add bonus level
					if children_kiri >= 1 and children_kanan>=1:
						exist = [('member_id','=',upline_id),('level','=',rel_level)]
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
	def hitung_bonus_pasangan(self, cr, uid, ids, context=None):
		mlm_plan 		= self.get_mlm_plan(cr, uid, context=context)
		amount_bonus_pasangan 		 = mlm_plan.bonus_pasangan 
		bonus_pasangan_percent_decrease = mlm_plan.bonus_pasangan_percent_decrease

		max_bonus_pasangan_level = 1000000 if mlm_plan.max_bonus_pasangan_level == 0 else mlm_plan.max_bonus_pasangan_pasangan
		if amount_bonus_pasangan == 0:
			return True

		new_member 		= self.browse(cr, uid, ids[0], context=context)
		member_bonus 	= self.pool.get('mlm.member_bonus')

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
		upline = self.browse(cr, uid, parent_id, context=context)
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

		for i in range(0, hak_usaha-1):
			data = {
				'code'			: '/',
				'parent_id'		: parent_id,
				'sponsor_id'	: sponsor_id,
				'name'			: "%s %d" % (new_member.name, i),
				'is_company'	: True 
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
		# titip yang beli paket
		#####################################################################
		new_member 	 = self.browse(cr, uid, ids[0], context=context)
		paket        = new_member.paket_id
		hak_usaha    = paket.hak_usaha

		#######################################################################
		# si top level (new_member) paket dapat bonus sponsor langsung sebanyak 
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
		# nilainya 0 saja karena sudah dijadikan cashback pada waktu join
		#######################################################################
		# import pdb; pdb.set_trace()
		sql = "select id, name,path from res_partner where \
			path_ltree <@ '%s' and id<>%d \
			order by path_ltree " % (new_member.path, new_member.id)
		cr.execute(sql)
		pids = cr.fetchall()
		for p in pids:
			self.hitung_bonus_level(cr, uid, [ p[0] ], zero_amount=True, context=context)
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
