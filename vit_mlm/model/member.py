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
		'sponsor_id' 		: fields.many2one('res.partner', 'Sponsor ID', required=True),
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
		return company.mlm_plan_id

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
			amount, 'New Member, Direct Sponsor', context=context)

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
	# 		pada level ke n [0..n], jumlah member aktif = 2^n
	# logic:
	#		cari semua upline sd max_bonus_level limit
	#		setiap id upline: hitung berapa jumlah downlinenya
	#		jika belum ada bonus pada level tsb dan jumlah downline == 2^level :
	#			maka si upline dapat bonus level
	#########################################################################
	def hitung_bonus_level(self, cr, uid, ids, context=None):
		mlm_plan 		= self.get_mlm_plan(cr, uid, context=context)
		amount_bonus_level 			 = mlm_plan.bonus_level
		amount_bonus_pasangan 		 = mlm_plan.bonus_pasangan 
		bonus_level_percent_decrease = mlm_plan.bonus_level_percent_decrease

		max_bonus_level_level = 1000000 if mlm_plan.max_bonus_level_level == 0 else mlm_plan.max_bonus_level_level
		if amount_bonus_level == 0:
			return True

		new_member 		= self.browse(cr, uid, ids[0], context=context)
		member_bonus 	= self.pool.get('mlm.member_bonus')

		#####################################################################
		# cari upline dan level nya masing-masing sd level max_bonus_level_level
		# dan bukan type Affiliate
		# 	Andi 1
		# 	Bani 2
		#   Doni 3
		#####################################################################
		#import pdb; pdb.set_trace()
		sql = "select id, name, path_ltree,\
				nlevel(path_ltree) as level,\
				nlevel(path_ltree) - nlevel('%s') as level\
				from res_partner as p where path_ltree @> '%s'\
				and id <> %d \
				and (is_affiliate <> 't' or is_affiliate is null)\
				order by path_ltree desc\
				limit %d" % (new_member.path, new_member.path, new_member.id, max_bonus_level_level)
		print sql 
		cr.execute(sql)
		rows = cr.fetchall()

		#import pdb; pdb.set_trace()

		#################################################################
		# loop masing-masing upline :
		#################################################################
		for r in rows:
			upline_id    = r[0]; upline_name  = r[1]; upline_path  = r[2]; upline_level = r[3]
			member_level = upline_level + 1

			#################################################################
			# cari total child per level 
			# hanya dihitung member yang sudang status Open (ada path nya)
			# jika jumlah child pada level n = 2^n : terjadi bonus level
			# level   children
			# 1       2  ---> bonus pasangan
			# 2       4 
			# 3       8
			# 4       5  ---> belum ada bonus level
			# 
			# jika jumlah child upline = 2: terjadi bonus pasangan
			#################################################################
			sql = "select nlevel(path_ltree) - nlevel('%s') as level, count(*)\
				from res_partner\
				where path_ltree ~ '%s.*{1,}'\
				group by level" % (upline_path,upline_path)
			cr.execute(sql)
			levels = cr.fetchall()
	
			for l in levels:
				rel_level = l[0]; children = l[1]
				_logger.error('Upline=%s, rel_level=%d, children=%d' % 
					(upline_name, rel_level, children))
				# jika belum exists
				exist = [('member_id','=',upline_id),('level','=',rel_level)]
				if not member_bonus.search(cr, uid, exist, context=context):
					# jika jumlah child == 2^level
					if children == 2**rel_level:
						# jika level 1 : namanya bonus pasangan
						if rel_level==1:
							member_bonus.addBonusPasangan(cr, uid, new_member.id, upline_id, rel_level,
								amount_bonus_pasangan, "Bonus Pasangan", context=context)

						member_bonus.addBonusLevel(cr, uid, new_member.id, upline_id, rel_level,
							amount_bonus_level, "Bonus Level at Level %d" % (rel_level), context=context)
		return True 


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
	# create : cek max downline, set path
	#########################################################################
	def create_user(self, cr, uid, member, context=None):
		alias_id = 4

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
			'MLM / Manager','MLM / User',
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

		#########################################################################
		# create user 
		#########################################################################		
		self.create_user(cr, uid, new_member, context=context)

		#########################################################################
		# process paket join, khusus binary plan saja
		#########################################################################		
		if new_member.paket_id:
			self.generate_sub_member(cr, uid, ids, context=context)

		return ids[0]


	#########################################################################
	# bentuk sub member akibat dari paket join (khusus binary plan)
	#########################################################################
	def generate_sub_member(self, cr, uid, ids, context=None):
		mlm_plan = self.get_mlm_plan(cr, uid, context=context)
		max_downline = mlm_plan.max_downline

		new_member = self.browse(cr, uid, ids[0], context=context)
		paket      = new_member.paket_id
		hak_usaha  = paket.hak_usaha
		child      = []

		parent_id 	= new_member.id 
		sponsor_id 	= new_member.sponsor_id.id

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
			child.append(new_sub_id)

			jc = jc + 1

			if jc >= max_downline:
				parent_id = child[parent_index]
				parent_index = parent_index + 1
				jc = 0

			#confirm langsung 


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
		self.hitung_bonus_sponsor(cr, uid, ids, context=context)
		self.hitung_bonus_level(cr, uid, ids, context=context)
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[3][0]},context=context)

	#########################################################################
	#set to "nonaktif" state
	#########################################################################
	def action_nonaktif(self,cr,uid,ids,context=None):
		self.hitung_bonus_sponsor(cr, uid, ids, context=context)
		self.hitung_bonus_level(cr, uid, ids, context=context)
		return self.write(cr,uid,ids,{'state':MEMBER_STATES[4][0]},context=context)
