from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
CASHFLOW_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]


class cashflow_coa(osv.osv):
	_name 		= 'anggaran.cashflow.coa'
	_columns = {
		'code'		: fields.char('Code'),
		'parent_id'	: fields.many2one('anggaran.cashflow.coa', 'Parent'),
		'name'		: fields.char('Name')
	}

class cashflow(osv.osv):
	_name 		= 'anggaran.cashflow'
	_columns = {
		'name'				: fields.char('No'),
		'tanggal'			: fields.date('Tanggal'),
		'fakultas_id'		: fields.many2one('anggaran.fakultas', 'Fakultas'),
		'jurusan_id'		: fields.many2one('anggaran.jurusan', 'Jurusan'),
		'unit_id'			: fields.many2one('anggaran.unit', 'Unit', required=True),
		'tahun_id'			: fields.many2one('account.fiscalyear', 'Tahun', required=True),
		'cashflow_line_ids'	: fields.one2many('anggaran.cashflow.line','cashflow_id','Lines', ondelete="cascade"),
		'state'             : fields.selection(CASHFLOW_STATES,'Status',readonly=True,required=True),
		'user_id'			: fields.many2one('res.users', 'Create By'),
		'show_actual'		: fields.boolean('Show Actual'),
		'show_deviasi'		: fields.boolean('Show Deviation'),
	}
	_defaults = {
		'state'       	: CASHFLOW_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',	
		'show_actual'	: True,
		'show_deviasi'	: True,
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.cashflow') or '/'
		new_id = super(cashflow, self).create(cr, uid, vals, context=context)
		return new_id

	def action_recalculate(self,cr,uid,ids,context=None):

		cr.execute('delete from anggaran_cashflow_line where cashflow_id=%s' % ids[0] )

		cf = self.browse(cr, uid, ids[0], context=context)
		total_income = 0.0
		total_biaya_unit = 0.0
		total_biaya_adm = 0.0
		total_pengeluaran = 0.0
		total_pendanaan = 0.0

		coa_obj = self.pool.get('anggaran.cashflow.coa')
		cashflow_line_ids = []

		coa_ids = coa_obj.search(cr, uid, [], context=context)

		for m in range(1,13):

			mfield = 0

			for coa in coa_obj.browse(cr, uid, coa_ids, context=context):
				
				if coa.code == '2.1':
					mfield = self.cari_bpp_mhs(cr, uid, cf)
					total_income += mfield 

				if coa.code == '2.2':
					mfield = self.cari_spp_mhs(cr, uid, cf)
					total_income += mfield

				if coa.code == '2.3':
					mfield = self.cari_tagihan_lain(cr, uid, cf)
					total_income += mfield

				if coa.code == '2.4':
					mfield = self.cari_income_lain(cr, uid, cf)
					total_income += mfield

				if coa.code == '2.100':
					mfield = total_income


				if coa.code == '3.1':
					mfield = self.cari_bahan_habis_pakai(cr, uid, cf)
					total_biaya_unit += mfield

				if coa.code == '3.2':
					mfield = self.cari_gaji(cr, uid, cf)
					total_biaya_unit += mfield

				if coa.code == '3.3':
					mfield = self.cari_sewa(cr, uid, cf)
					total_biaya_unit += mfield

				if coa.code == '3.4':
					mfield = self.cari_outsourcing(cr, uid, cf)
					total_biaya_unit += mfield

				if coa.code == '3.5':
					mfield = self.cari_overhead(cr, uid, cf)
					total_biaya_unit += mfield

				if coa.code == '3.100':
					mfield = total_biaya_unit 


				if coa.code == '3.6':
					mfield = self.cari_biaya_adm(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.7':
					mfield = self.cari_investasi(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.8':
					mfield = self.cari_biaya_prepaid(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.9':
					mfield = self.cari_pajak(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.10':
					mfield = self.cari_uudp(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.11':
					mfield = self.cari_saving(cr, uid, cf)
					total_pengeluaran += mfield

				if coa.code == '3.200':
					mfield = total_pengeluaran

				if coa.code == '3.300':
					mfield = total_income - total_biaya_unit - total_pengeluaran


				if coa.code == '4.1':
					mfield = self.cari_pinjaman(cr, uid, cf)
					total_pendanaan += mfield

				if coa.code == '4.2':
					mfield = self.cari_pembayaran_pinjaman(cr, uid, cf)
					total_pendanaan += mfield

				if coa.code == '4.3':
					mfield = self.cari_bunga_pinjaman(cr, uid, cf)
					total_pendanaan += mfield

				if coa.code == '4.100':
					mfield = total_pendanaan 

				if coa.code == '5':
					mfield =  total_income - total_biaya_unit - total_pengeluaran + total_pendanaan


				cashflow_line_ids.append( (0,0,{
					'cashflow_coa_id' : coa.id,
					'type':'p',
					('m%i' % m ) : mfield,
				}) )

				if len(coa.code) > 1:
					cashflow_line_ids.append( (0,0,{
						'type':'a',
						('m%i' % m ) : 0.0,
					}) )

					cashflow_line_ids.append( (0,0,{
						'type':'v',
						('m%i' % m ) : 0.0
					}) )

			self.write(cr, uid,ids, {'cashflow_line_ids':cashflow_line_ids}, context=context)
		return

	#cari dari jurusan_income total record total
	def cari_spp_mhs(self, cr, uid, cf):
		jurusan_id = cf.jurusan_id
		total = 0.0
		for inc in jurusan_id.income_ids:
			total += inc.total_spp
		return total 

	def cari_bpp_mhs(self, cr, uid, cf):
		jurusan_id = cf.jurusan_id
		total = 0.0
		for inc in jurusan_id.income_ids:
			total += inc.total_bpp
		return total 

	def cari_income_lain(self, cr, uid, cf):
		total = 0.0
		return total

	def cari_tagihan_lain(self, cr, uid, cf):
		total = 0.0
		return total 

	def cari_bahan_habis_pakai(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_gaji(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_sewa(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_outsourcing(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_overhead(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_biaya_adm(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_investasi(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_biaya_prepaid(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_pajak(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_uudp(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_saving(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_pinjaman(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_pembayaran_pinjaman(self, cr, uid, cf):
		total = 0.0
		return total 
	def cari_bunga_pinjaman(self, cr, uid, cf):
		total = 0.0
		return total 



class cashflow_line(osv.osv):
	_name 		= 'anggaran.cashflow.line'
	_columns = {
		'cashflow_id': fields.many2one('anggaran.cashflow', 'Cashflow'),
		'cashflow_coa_id': fields.many2one('anggaran.cashflow.coa', 'Rincian'),
		'code': fields.related('cashflow_coa_id', 'code' , type="char", relation="anggaran.cashflow_coa", string="Code", store=False),
		'type': fields.char('Type'),
		'm1' : fields.float('Sep'),
		'm2' : fields.float('Oct'),
		'm3' : fields.float('Nov'),
		'm4' : fields.float('Dec'),
		'm5' : fields.float('Jan'),
		'm6' : fields.float('Feb'),
		'm7' : fields.float('Mar'),
		'm8' : fields.float('Apr'),
		'm9' : fields.float('May'),
		'm10' : fields.float('Jun'),
		'm11' : fields.float('Jul'),
		'm12' : fields.float('Aug'),

		'm1a' : fields.float('Sep (a)'),
		'm2a' : fields.float('Oct (a)'),
		'm3a' : fields.float('Nov (a)'),
		'm4a' : fields.float('Dec (a)'),
		'm5a' : fields.float('Jan (a)'),
		'm6a' : fields.float('Feb (a)'),
		'm7a' : fields.float('Mar (a)'),
		'm8a' : fields.float('Apr (a)'),
		'm9a' : fields.float('May (a)'),
		'm10a' : fields.float('Jun (a)'),
		'm11a' : fields.float('Jul (a)'),
		'm12a' : fields.float('Aug (a)'),

		'm1s' : fields.float('Sep (s)'),
		'm2s' : fields.float('Oct (s)'),
		'm3s' : fields.float('Nov (s)'),
		'm4s' : fields.float('Dec (s)'),
		'm5s' : fields.float('Jan (s)'),
		'm6s' : fields.float('Feb (s)'),
		'm7s' : fields.float('Mar (s)'),
		'm8s' : fields.float('Apr (s)'),
		'm9s' : fields.float('May (s)'),
		'm10s' : fields.float('Jun (s)'),
		'm11s' : fields.float('Jul (s)'),
		'm12s' : fields.float('Aug (s)'),				

	}
