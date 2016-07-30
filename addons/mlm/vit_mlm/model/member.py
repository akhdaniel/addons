from openerp import tools
from openerp import SUPERUSER_ID
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
from datetime import datetime

_logger = logging.getLogger(__name__)

MEMBER_STATES = [('draft', _('Draft')), ('open', _('Verification')),
                 ('reject', _('Rejected')),
                 ('aktif', _('Active')), ('nonaktif', _('Non Active'))]

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


    def _auto_init(self, cr, context=None):
        sql="CREATE extension IF NOT EXISTS ltree"
        cr.execute(sql)

        sql = "CREATE OR REPLACE function f_add_col(_tbl regclass, _col  text, _type regtype)\
                  RETURNS bool AS \
                $BODY$ \
                BEGIN \
                   IF EXISTS (SELECT 1 FROM pg_attribute \
                              WHERE  attrelid = _tbl \
                              AND    attname = _col \
                              AND    NOT attisdropped) THEN \
                      RETURN FALSE; \
                   ELSE \
                      EXECUTE format('ALTER TABLE %s ADD COLUMN %I %s', _tbl, _col, _type); \
                      RETURN TRUE; \
                   END IF; \
                END \
                $BODY$ LANGUAGE plpgsql"
        cr.execute(sql)

        sql = "select f_add_col('res_partner', 'path_ltree', 'ltree')"
        cr.execute(sql)

        sql="CREATE OR REPLACE FUNCTION f_add_index(table_name text, index_name text, index_type text, column_name text)\
                RETURNS void AS $$\
            declare\
               l_count integer;\
            begin\
              select count(*) \
                 into l_count \
              from pg_indexes \
              where schemaname = 'public' \
                and tablename = lower(table_name)\
                and indexname = lower(index_name);\
              if l_count = 0 then \
                 execute 'create index ' || index_name || ' on ' || table_name || ' USING ' || index_type || '(' || column_name || ')'; \
              end if; \
            end;\
            $$ LANGUAGE plpgsql;"
        cr.execute(sql)
        sql = "select f_add_index('res_partner', 'path_gist_res_partner_idx', 'GIST', 'path_ltree')"
        cr.execute(sql)

        sql = "select f_add_index('res_partner', 'path_res_partner_idx', 'btree', 'path_ltree')"
        cr.execute(sql)


        return super(member, self)._auto_init(cr, context=context)

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

    # untuk mencari invoice pertama (inv join) apa sdh paid atau belum
    def _get_inv_join_paid(self, cr, uid, ids, field, arg, context=None):
        inv_obj		= self.pool.get("account.invoice")
        results 	= {}
        partners 	= self.browse(cr, uid, ids, context=context)
        for partner in partners:
            results[partner.id] = False
            inv_id 	= inv_obj.search(cr,uid,[('partner_id','=',partner.id)])
            #jika ada invoicenya
            if inv_id :
                # cari yang id nya paling kecil
                inv_join 	= sorted(inv_id)[0]
                inv_state 	= inv_obj.browse(cr,uid,inv_join).state
                if inv_state == 'paid' :
                    results[partner.id] = True
        return results

    _columns 	= {
        'path'				: fields.char("Path"),
        'code'				: fields.char("Member ID"),
        'parent_id' 		: fields.many2one('res.partner', 'Upline ID', required=False,readonly=True,states={'draft':[('readonly',False)]}),
        'sponsor_id' 		: fields.many2one('res.partner', 'Sponsor ID', required=False,readonly=True,states={'draft':[('readonly',False)]}),
        'member_bonus_ids' 	: fields.one2many('mlm.member_bonus','member_id','Member Bonuses', ondelete="cascade", readonly=True,),
        'state'				: fields.selection(MEMBER_STATES,'Status',readonly=True,required=True),

        ### paket join
        'paket_id'			: fields.many2one('mlm.paket', 'Join Package',
            domain="[('is_submember','=',False)]", readonly=True, states={'draft':[('readonly',False)]}),
        'paket_harga'		: fields.related('paket_id', 'price' ,
            type="float", relation="mlm.paket", string="Package Price",readonly=True),
        'paket_cashback'		: fields.float("Cashback Join",readonly=True,store=True),

        ## paket barang
        'paket_produk_ids'	: fields.one2many('mlm.member_paket_produk','member_id', 'Product Package',),# states={'aktif':[('readonly',True)]}),
        # 'paket_produk_id'	: fields.many2one('mlm.paket_produk', 'Product Package',
        # 	required=True),

        # untransfered
        'total_bonus' 				: fields.function(_total_bonus, string="Total Bonus"),
        'total_bonus_sponsor' 		: fields.function(_total_bonus_sponsor, string="Total Bonus Sponsor"),
        'total_bonus_pasangan' 		: fields.function(_total_bonus_pasangan, string="Total Bonus Pairing"),
        'total_bonus_level' 		: fields.function(_total_bonus_level, string="Total Bonus Level"),
        'total_bonus_belanja' 		: fields.function(_total_bonus_belanja, string="Total Bonus Order"),
        # trasfered
        'total_bonus_transfered' 				: fields.function(_total_bonus_transfered, string="Total Bonus"),
        'total_bonus_sponsor_transfered' 		: fields.function(_total_bonus_sponsor_transfered, string="Total Bonus Sponsor"),
        'total_bonus_pasangan_transfered' 		: fields.function(_total_bonus_pasangan_transfered, string="Total Bonus Pairing"),
        'total_bonus_level_transfered' 			: fields.function(_total_bonus_level_transfered, string="Total Bonus Level"),
        'total_bonus_belanja_transfered' 		: fields.function(_total_bonus_belanja_transfered, string="Total Bonus Order"),

        'bbm'				: fields.char("BBM Pin"),
        'signature'			: fields.binary('Signature'),
        'bank_no'			: fields.char("Bank Account Number"),
        'bank_account_name'	: fields.char("Bank Account Name"),
        'bank_name'			: fields.char("Bank Name"),
        'bank_branch'		: fields.char("Bank Branch"),
        'id_number'			: fields.char("ID Card No"),

        'tree_url'	  		: fields.function(_get_tree_url, type="char", string="Tree URL"),

        'sale_order_ids'		: fields.one2many('sale.order','partner_id','Sale Orders'),
        'sale_order_exists'		: fields.function(_sale_order_exists,
            string='Sales Order Ada',
            type='boolean',
            # help="Apakah Partner ini sudah punya Sales Order."),
        help="Is the Partner has Sales Order?"),
        'start_join'		: fields.char("Start Join",readonly=True),
        'cek_state'		    : fields.function(_cek_state, type="char", method=True,
            string="Show/hide buttons", store=False, help="Show/hide buttons."),

        'history_join_ids'	: fields.one2many('mlm.history.join','member_id',string='History Join',readonly=True),
        'jumlah_bayar'		: fields.float('Amount Due',readonly=True),
        'invoice_join_paid'	: fields.function(_get_inv_join_paid, type="boolean",readonly=True,string="Invoice Join Paid")

    }
    _defaults = {
        'code'				: lambda obj, cr, uid, context: '/',
        'state'				: MEMBER_STATES[0][0],
        'paket_produk_ids'	: _get_default_paket_produk,
        'cek_state'			: 'draft',
    }
    _sql_constraints = [
        ('id_number_uniq', 'unique(id_number)','ID Card already used !'),
        ('cek_unik_email', 'UNIQUE(email)', 'Email already exists !')
    ]


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
            raise osv.except_osv(_('Error'),
                _("No Bonus Level defined, code = 3") )
                #_("Belum ada definisi Bonus Level, code = 3") )
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
                #import pdb;pdb.set_trace()
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
            raise osv.except_osv(_('Error'),
                _("No Bonus Pairing defined, code = 2") )
                #_("Belum ada definisi Bonus Pairing, code = 2") )
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

            for lev in levels.keys():
                kiris = levels[lev][0]
                kanans = levels[lev][1]

                for kiri in kiris:
                # 	search = ['&','&',('level', '=',lev),
                # 			('bonus_id','=',bonus_pasangan),
                # 			('new_member_id','=',kiri)]
                    # exist = member_bonus.search(cr, uid, search, context=context)
                    sql = "select id from mlm_member_bonus \
                            where level = %d \
                            and bonus_id = %d \
                            and ( match_member_id = %d \
                            or new_member_id = %d)" % (lev, bonus_pasangan, kiri, kiri)
                    _logger.warning( sql )
                    cr.execute(sql)
                    exist = cr.fetchall()
                    if not exist :
                        for kanan in kanans:
                            # search = ['&','&',('match_member_id', '=',kanan),('level', '=',lev),
                            # 	('bonus_id','=',bonus_pasangan)]
                            # exist = member_bonus.search(cr, uid, search, context=context)
                            sql = "select id from mlm_member_bonus \
                                    where level = %d \
                                    and bonus_id = %d \
                                    and ( match_member_id = %d \
                                    or new_member_id = %d)" % (lev, bonus_pasangan, kanan, kanan)
                            _logger.warning( sql )
                            cr.execute(sql)
                            exist = cr.fetchall()
                            if not exist:
                                desc = '%sPairing' % (cashback)
                                member_bonus.addBonusPairing(cr, uid, kiri, kanan,
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
        members_categ = self.pool.get('res.partner.category').search(cr, uid, [('name','=','Members')], context=context)
        start_join 	= False
        harga_paket = 0
        cashback 	= 0

        if 'paket_id' in vals:
            paket = self.pool.get('mlm.paket').browse(cr,uid,int(vals['paket_id']))
            start_join 	= paket.name or ''
            harga_paket = paket.price
            cashback 	= paket.cashback

            vals.update({
                'customer'		: True,
                'supplier'		: True,
                'is_company'	: True,
                'start_join'	: start_join,
                'jumlah_bayar'	: harga_paket-cashback,
                'paket_cashback': cashback

            })
        if members_categ:
            vals.update({
                'category_id': [(4, members_categ[0])]
        })

        new_id = super(member, self).create(cr, uid, vals, context=context)

        return new_id

    #########################################################################
    # create user secara manual
    # bawaan odoo: waktu create user otomatis terbentuk res_partner
    #########################################################################
    def create_user(self, cr, uid, member, context=None):
        alias_id = 1

        #default action upon login
        action_id = self.pool.get('ir.actions.actions').search(cr, uid, [('name','=','MLM Homepage')], context=context)
        if not action_id:
            raise osv.except_osv(_('error'),_("no action id MLM Homepage, please install MLM Website or contact Administrator") )

        sql = "INSERT INTO ""res_users"" (""id"", ""partner_id"", \
            ""alias_id"", ""share"", ""active"", ""company_id"", \
            ""action_id"", ""display_employees_suggestions"", \
            ""default_section_id"", ""password"", \
            ""display_groups_suggestions"", ""signature"", \
            ""login"", ""create_uid"", ""write_uid"", \
            ""create_date"", ""write_date"") \
            VALUES (nextval('res_users_id_seq'), \
            %d, %d, false, true, %d, %d, true, NULL, '', \
            true, NULL, '%s', %d, %d, (now() at time zone 'UTC'), \
            (now() at time zone 'UTC')) RETURNING id" % (
                member.id,
                alias_id,
                member.company_id,
                action_id[0],
                # member.name.lower(),
                member.email.lower(),
                uid,uid)
        res = cr.execute(sql)

        user_id = cr.fetchall()



        group =  self.pool.get('res.groups')

        #employee
        # grp_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_user')
        # group_user_id = grp_ref and grp_ref[1] or False,

        #'Contact Creation'
        grp_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_partner_manager')
        group_partner_manager_id = grp_ref and grp_ref[1] or False,

        #'Portal'
        # grp_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'base', 'group_portal')
        # group_portal_id = grp_ref and grp_ref[1] or False,

        #'MLM / Member'
        grp_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'vit_mlm', 'group_mlm_user')
        group_mlm_user_id = grp_ref and grp_ref[1] or False,

        gids =group.search(cr, SUPERUSER_ID, [('id','in',[
            group_partner_manager_id,
            group_mlm_user_id
            ])], context=context)

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
        _logger.warning(upline.state)
        if upline and upline.state not in ['open','aktif','pre']:
            raise osv.except_osv(_('Warning'),
                "Cannot confirm member %s, upline %s is not Open/Active/Pre-Registered"%(new_member.name,upline.name) )

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

        #########################################################################
        # buat histori confirm
        #########################################################################
        history= {
                'member_id'		: ids[0],
                'paket_id'		: new_member.paket_id.id,
                'date'			: time.strftime("%Y-%m-%d %H:%M:%S")
        }
        history_id = self.pool.get('mlm.history.join').create(cr, uid, history, context=context)

        self.write(cr,uid,ids[0],{
            'code' : new_code,
            'path' : new_path,
            'state': MEMBER_STATES[1][0]},context=context)

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
            amount, '%d x Bonus Sponsor Package %s' % (hak_usaha, paket.name), context=context)

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
        # sale_order dan invoice object
        #################################################################
        sale_order_obj = self.pool.get("sale.order")

        #################################################################
        # compose sale_order lines
        #################################################################
        lines = []
        isi_paket = 0
        jml_paket = partner.paket_id.hak_usaha
        for paket in paket_produk_ids:
            paket_qty = paket.qty
            if paket_qty > 0 :
                isi_paket+=paket_qty
                for detail in paket.paket_produk_id.paket_produk_detail_ids:
                    lines.append((0,0,{
                        'product_id'		: detail.product_id.id,
                        'product_uom'		: detail.uom_id.id,
                        'name'				: detail.product_id.name,
                        'product_uom_qty' 	: detail.qty * paket_qty,
                        'price_unit' 		: detail.harga,
                    }))
        if not lines:
            raise osv.except_osv(_('Warning'),_("Product Items for Package %s is empty, please set !" % (partner.paket_id.name)))

        ####################################################
        # jika create SO untuk join pertama
        ####################################################
        if partner.cek_state != 'update':
            paket_so = partner.paket_id.id
            if isi_paket != jml_paket:
                raise osv.except_osv(_('Warning'),_("Product Package is not match with Join Package %s" % (partner.paket_id.name)))
            ##############################################################
            # cek apakah sudah buat SO sebelumnya untuk aktifkan memmber
            ##############################################################
            sale_order_exist 	= sale_order_obj.search(cr,uid,[('partner_id','=',ids[0]),('paket_id','=',partner.paket_id.id)])
            if sale_order_exist :
                raise osv.except_osv(_('Error!'), _('Sale Order member %s package %s exists !') % (partner.name,partner.paket_id.name))

        ####################################################
        # jika create SO untuk Upgrade
        ####################################################
        elif partner.cek_state == 'update':

            ####################################################
            # hitung jumlah package yang seharusnya diisi
            ####################################################
            new_code 		= str(int(partner.paket_id.code) + 1)
            paket_obj 		= self.pool.get('mlm.paket')
            new_paket_id  	= paket_obj.search(cr,uid,[('code','=',new_code)])[0]

            paket_browse	= paket_obj.browse(cr,uid,new_paket_id)
            hu_baru 		= paket_browse.hak_usaha
            paket_to_add 	= hu_baru - partner.paket_id.hak_usaha

            paket_so  		= paket_browse.id

            if isi_paket != paket_to_add :
                raise osv.except_osv(_('Warning!'),_("Jumlah package produk tidak sesuai dengan upgrade \
                    package %s ke package %s (harus %d package product) !" % (partner.paket_id.name,paket_browse.name,paket_to_add)))

            ##############################################################
            # cek apakah sudah buat SO sebelumnya untuk aktifkan memmber
            ##############################################################
            sale_order_exist 	= sale_order_obj.search(cr,uid,[('partner_id','=',ids[0]),('paket_id','=',new_paket_id)])
            if sale_order_exist :
                raise osv.except_osv(_('Error!'), _('Sale Order member %s package upgrade %s sudah ada !') % (partner.name,paket_browse.name))

        #################################################################
        # create sale_order
        #################################################################
        data= {
            'partner_id'			: partner.id,
            'partner_invoice_id' 	: partner.id,
            'partner_shipping_id' 	: partner.id,
            'date_order'			: time.strftime("%Y-%m-%d %H:%M:%S") ,
            'order_line' 			: lines,
            'order_policy'			: 'prepaid', # agar invoice di buat otomatis sebelum barang di transfer
            'origin'				: 'Product Package Member: %s' % (partner.name),
            'paket_id'				:  paket_so #insert package id di SO
        }

        sale_order_id = sale_order_obj.create(cr, uid, data, context=context)

        # cr.commit()
        # raise osv.except_osv( '' , '')
        return {'warning': {'title': _('OK!'),'message': _('Sale Order created !.')}}


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
            raise osv.except_osv(_('Error!'), _('Package %s tidak bisa diupgrade!') % (paket.name))

        ####################################################
        # paket yg akan diisikan ke member yg diupdate
        ####################################################
        new_code 		= str(int(paket.code) + 1)
        paket_obj 		= self.pool.get('mlm.paket')
        new_paket_id  	= paket_obj.search(cr,uid,[('code','=',new_code)])[0]

        max_downline 	= upline.company_id.mlm_plan_id.max_downline
        paket_browse	= paket_obj.browse(cr,uid,new_paket_id,)
        hu_baru 		= paket_browse.hak_usaha
        member_to_add 	= hu_baru - paket.hak_usaha

        ####################################################
        # cek invoice atas join paket ini apa sdh paid?
        ####################################################
        inv_obj = self.pool.get('account.invoice')
        invoice_id 	= inv_obj.search(cr,uid,[('partner_id','=',ids[0]),('paket_id','=',new_paket_id)])
        if not invoice_id :
            raise osv.except_osv(_('Tidak bisa upgrade!'), _('Hal ini terjadi karena SO belum di buat, \n jika SO sudah dibuat berarti invoicenya belum dibuat !'))

        else :
            invoice 	= inv_obj.browse(cr,uid,invoice_id[0])
            inv_state 	= invoice.state
            inv_number	= invoice.number
            if inv_number == False :
                inv_number = ''
            if inv_state != 'paid' :
                raise osv.except_osv(_('Error!'), _('Invoice %s untuk upgrade package %s member ini belum paid !') % (inv_number,paket_browse.name))

        ####################################################
        # cek package yang akan di upgrade
        # apakah jml package detailnya sesuai dengan sisa
        # hak usaha (hak usaha baru - hak usaha lama)
        ####################################################
        titik = 0
        for ttk in upline.paket_produk_ids :
            titik += ttk.qty

        if member_to_add != 0.0 :
            if titik != member_to_add:
                raise osv.except_osv(_('Error!'), _('Upgrade ke Package %s harus beli %d package lagi !')
                                                    % (paket_browse.name,member_to_add))

        if member_to_add == 0:
            #########################################################
            # buat histori upgrade
            #########################################################
            history= {
                    'member_id'		: ids[0],
                    'paket_id'		: new_paket_id,
                    'date'			: time.strftime("%Y-%m-%d %H:%M:%S")
            }
            self.pool.get('mlm.history.join').create(cr, uid, history, context=context)
            return self.write(cr,uid,ids[0],{'paket_id':new_paket_id})

        direct_src = self.search(cr,uid,[('parent_id','=',upline.id)])
        direct_childs = self.browse(cr,uid,direct_src,)
        if direct_childs:
            for child in direct_childs:
                ##############################################
                # putuskan parent id
                ##############################################
                child.write({'parent_id':False})


        new_data 		= {}
        new_childs 		= []
        i = len(self.search(cr,uid,[('name','ilike',upline.name)])) - 1
        paket_sub_member = self.pool.get('mlm.paket').search(cr,uid,[('is_submember','=',True)],limit=1)[0]
        # kiri :0 kanan: 1
        kaki = 0
        dc_path=[]

        #import pdb;pdb.set_trace()
        while len(new_childs) < member_to_add:
            ####################################################
            # Generate new_id
            ####################################################
            new_data = {
                'parent_id'		: upline.id,
                'sponsor_id'	: upline.sponsor_id.id,
                'name'			: "%s %d" % (upline.name,i),
                'is_company'	: True,
                'start_join'	: upline.paket_id.name,
                'paket_id'		: paket_sub_member,
                'state'			: MEMBER_STATES[0][0],
                }
            new_id = self.create(cr, uid, new_data, context=context)

            ####################################################
            # Commit dulu ke database agar bisa di aktivasi
            ####################################################
            cr.commit()

            ####################################################
            # aktifasi new_id yang telah dibuat sebelumnya
            ####################################################
            self.action_confirm(cr,uid,[new_id],context=None)

            ####################################################
            # browse path new_id yang sudah di update
            # di fungsi action_confirm untuk di append
            ####################################################
            new_path_new_id = self.browse(cr,uid,new_id).path

            dc_path.append(new_path_new_id)
            new_childs.append(new_id)

            kaki+=1
            i+=1

            ####################################################
            # jika punya direct childs
            # sambungkan kembali upline_id nya
            ####################################################
            if direct_childs :
                if kaki == 1 :
                    self.write(cr,uid,direct_childs[0].id,{'parent_id':new_id})

                elif len(direct_childs) >1 and kaki == 2 :
                    self.write(cr,uid,direct_childs[1].id,{'parent_id':new_id})
                cr.commit()
                #########################################################################
                # create sub new_id (sub dari id baru, misal dari 3 titik ke 7 titik)
                # jumlah titik yang akan ditambahkan > maksimal downline per titik
                #########################################################################
                if member_to_add > max_downline:
                    new_data.update({
                        'parent_id'		: new_id,
                        'name'			: "%s %d" % (upline.name,i)
                    })
                    new_sub_id=self.create(cr, uid, new_data, context=context)

                    ####################################################
                    # Commit dulu ke database agar bisa di aktivasi
                    ####################################################
                    cr.commit()

                    ####################################################
                    # aktifasi sub new_id yang telah dibuat sebelumnya
                    ####################################################
                    self.action_confirm(cr,uid,[new_sub_id],context=None)

                    ####################################################
                    # browse path new_id yang sudah di update
                    # di fungsi action_confirm untuk di append
                    ####################################################
                    new_path_sub_new_id = self.browse(cr,uid,new_sub_id).path

                    # dc_path.append(new_path_sub_new_id)
                    new_childs.append(new_sub_id)

                    i+=1


        ########################################################
        # Update path semua child dari member yang di upgrade
        ########################################################
        kanan=False
        cur_update_member_path=upline.path
        if new_childs and direct_childs:
            ####################################################
            # kaki kiri dan kanan diproses masing2
            ####################################################
            for dc in direct_childs:
                #import pdb;pdb.set_trace()
                ################################################
                # update childs all member kiri saja/kanan saja
                ################################################
                member_to_update = self._cari_data_bds_ltree_level(cr, uid, dc.path, 0, context=None) #res: id,ltree,path

                if kanan :
                    # kaki kanan
                    new_id_path = dc_path[1]
                else:
                    # kaki kiri
                    new_id_path = dc_path[0]
                    kanan = True
                #import pdb;pdb.set_trace()
                for mem in member_to_update:
                    ###############################################
                    this_old_path = mem[2]
                    new_path = new_id_path + this_old_path[len(cur_update_member_path):]

                    #########################################################################
                    # update path_ltree
                    #########################################################################
                    cr.execute("update res_partner set path_ltree = '%s', path = '%s' where id=%d" %
                        (new_path,new_path, mem[0]) )
                    cr.commit()

        ########################################################
        # naikan bonus level dan pasangan (increament +1)
        ########################################################
        for bonus in upline.member_bonus_ids:
            if bonus.level != 0 :
                self.pool.get('mlm.member_bonus').write(cr,uid,bonus.id,{'level':bonus.level+1})

        cr.commit()

        #########################################################
        # hitung semua bonus utk masing2 titik
        #########################################################
        if new_childs:
            for child in new_childs:
                self.action_aktif(cr,uid,[child],context=None)

        #########################################################
        # buat histori upgrade
        #########################################################
        history= {
                'member_id'		: ids[0],
                'paket_id'		: new_paket_id,
                'date'			: time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.pool.get('mlm.history.join').create(cr, uid, history, context=context)

        harga_paket_awal 	= upline.paket_id.price
        harga_paket_upgrade = paket_browse.price
        jml_harus_dibayar	= harga_paket_upgrade-harga_paket_awal

        self.write(cr,uid,ids[0],{'paket_id':new_paket_id,'jumlah_bayar':jml_harus_dibayar})

        return True

    def unlink(self, cr, uid, ids, context=None):
        orphan_contact_ids = self.search(cr, uid,
            [('parent_id', 'in', ids), ('id', 'not in', ids), ('use_parent_address', '=', True)], context=context)
        if orphan_contact_ids:
            # no longer have a parent address
            self.write(cr, uid, orphan_contact_ids, {'use_parent_address': False}, context=context)
        # hanya data yang berstatus draft saja yg bisa di hapus
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state != 'draft':
                raise osv.except_osv(_('Error!'), _('Only Draft Member can be deleted !'))
        return super(member, self).unlink(cr, uid, ids, context=context)


class mlm_history_join(osv.osv):
    _name ='mlm.history.join'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for history in self.read(cr, uid, ids, context=context):
            nam = history['paket_id'][1] + "[" + history['date'] + "]"# [0]=id, [1]=name
            res.append((history['id'], nam))
        return res

    _columns ={
        'member_id'		: fields.many2one('res.partner','Member_id'),
        'paket_id'		: fields.many2one('mlm.paket','Package'),
        'date'			: fields.date('Date'),
        }

mlm_history_join()