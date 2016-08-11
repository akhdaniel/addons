from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
from datetime import datetime,date
from dateutil.relativedelta import relativedelta
import logging
from openerp.tools.translate import _
import bni 
from openerp import netsvc
_logger = logging.getLogger(__name__)

####################################################################################
# on validate create biller taghian
# on cancel delete biller tagihan
####################################################################################
class account_invoice(osv.osv):
	_name 		= "account.invoice"
	_inherit 	= "account.invoice"

	spc_hostname = False
	spc_username = False
	spc_password = False
	spc_dbname   = False

	####################################################################################
	# get parameters for spc connections
	####################################################################################
	def get_params(self, cr, uid, context=None):
		self.spc_hostname = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.hostname')
		self.spc_username = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.username')
		self.spc_password = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.password')
		self.spc_dbname   = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.dbname')

	####################################################################################
	# on validate invoice, create biller_tagihan di MySQL SPC
	# update biller_tagihan_id ke invoice
	####################################################################################
	def invoice_validate(self, cr, uid, ids, context=None):
		_logger.info("validating invoice")
		res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=None)

		self.get_params(cr, uid, context=context)

		spc = bni.spc()
		spc.connect(host=self.spc_hostname, user=self.spc_username, passwd=self.spc_password, db=self.spc_dbname)
		for inv in self.browse(cr, uid, ids, context=context):
			
			mahasiswa = inv.partner_id 

			if mahasiswa.status_mahasiswa in ('calon','Mahasiswa'):

				if mahasiswa.status_mahasiswa == 'calon':
					nomor_pembayaran = mahasiswa.reg
				else:
					nomor_pembayaran = mahasiswa.npm

				today = date.today() 
				three_mon = today + relativedelta(months=3)
				#import pdb;pdb.set_trace()
				# insert header
				data = {
		            'id_record_tagihan'         : inv.number ,
		            'nomor_pembayaran'          : nomor_pembayaran ,
		            'nama'                      : mahasiswa.name ,
		            'kode_fakultas'             : mahasiswa.fakultas_id.kode ,
		            'nama_fakultas'             : mahasiswa.fakultas_id.name ,
		            'kode_prodi'                : mahasiswa.prodi_id.kode ,
		            'nama_prodi'                : mahasiswa.prodi_id.name ,
		            'kode_periode'              : mahasiswa.tahun_ajaran_id.code , ## TODO: tambah semester
		            'nama_periode'              : mahasiswa.tahun_ajaran_id.name , ## TODO: tambah semester
		            'is_tagihan_aktif'          : 1 ,
		            'waktu_berlaku'             : today.strftime('%Y-%m-%d'),
		            'waktu_berakhir'            : three_mon.strftime('%Y-%m-%d') ,
		            'strata'                    : mahasiswa.prodi_id.jenjang.name ,
		            'angkatan'                  : mahasiswa.tahun_ajaran_id.name ,
		            'urutan_antrian'            : 0,   ### TODO : jika ada 4 invoices, ini harus ngurut 0,1,2,3
		            'total_nilai_tagihan'       : inv.amount_total ,
		            'minimal_nilai_pembayaran'  : inv.amount_total ,
		            'maksimal_nilai_pembayaran' : inv.amount_total  ,
		            'nomor_induk'               : mahasiswa.npm,
		            'pembayaran_atau_voucher'   : '',
		            'voucher_nama'              : '' ,
		            'voucher_nama_fakultas'     : '',
		            'voucher_nama_prodi'        : '' ,
		            'voucher_nama_periode'      : '' 
				}
				spc.insert_biller_tagihan( data )

				# insert detail
				for line in inv.invoice_line:
					data = {
						'id_record_detil_tagihan'	: line.id, 
						'id_record_tagihan'			: inv.number,
						'urutan_detil_tagihan'		: line.id, 		
						'kode_jenis_biaya'			: line.product_id.default_code, 
						'label_jenis_biaya'			: line.product_id.name, 
						'label_jenis_biaya_panjang'	: line.name,
						'nilai_tagihan'				: line.price_subtotal
					}
					spc.insert_biller_tagihan_detil(data)

				# write reference sebagai flag bahwa invoice ini success spc
				self.write(cr,uid,inv.id,{'name':'Insert SPC Success'})

		spc.close()
		return res

	#######################################################################################
	# on cancel, hapus biller_tagihan ybs
	#######################################################################################
	def action_cancel(self, cr, uid, ids, context=None):
		_logger.info("canceling invoice")

		self.get_params(cr, uid, context=context)
		spc = bni.spc()
		spc.connect(host=self.spc_hostname, user=self.spc_username, passwd=self.spc_password, db=self.spc_dbname)
		for inv in self.browse(cr, uid, ids, context=context):

			#delete header
			data = {
				'id_record_tagihan': inv.number
			}
			spc.delete_biller_tagihan(data)

			#delete detail
			for line in inv.invoice_line:
				data = {
					'id_record_detil_tagihan'	: line.id, 
					'id_record_tagihan'			: inv.number,
				}
				spc.delete_biller_tagihan_detil(data)

			# hapus reference sebagai flag bahwa invoice ini success spc
			self.write(cr,uid,inv.id,{'name':False})

		spc.close()
		res = super(account_invoice, self).action_cancel(cr, uid, ids, context=None)
		return res


####################################################################################
# periodic read dari ca_pembayaran
# if exists create payment voucher for the invoice
####################################################################################
class account_voucher(osv.osv):
	_name 		= "account.voucher"
	_inherit 	= "account.voucher"

	spc_hostname = False
	spc_username = False
	spc_password = False
	spc_dbname   = False

	####################################################################################
	# get parameters for spc connections
	####################################################################################
	def get_params(self, cr, uid, context=None):
		self.spc_hostname = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.hostname')
		self.spc_username = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.username')
		self.spc_password = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.password')
		self.spc_dbname   = self.pool.get('ir.config_parameter').get_param(cr, uid, 'spc.dbname')


	####################################################################################
	# proses import dari menu More..
	####################################################################################
	def process_import(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		active_ids 		= context['active_ids']
		_logger.info('processing from menu. active_ids=%s' % (active_ids)) 
		self.actual_process_import(cr, uid, context)

	####################################################################################
	# proses import dari Cron Job, pilih yang masih is_processed = False
	# limit records
	# panggil dari cron job (lihat di xml)
	####################################################################################
	def cron_process_import(self, cr, uid, context=None):
 		################################################################################
		# id yg akan diproses
		################################################################################
		self.actual_process_import(cr, uid, context)

	####################################################################################
	# mulai process import, bisa dari menu atau dari cron job
	####################################################################################
	def actual_process_import(self, cr, uid, context=None):

		################################################################################
		# prepare common variable
		################################################################################
		users_obj = self.pool.get('res.users')
		u1 = users_obj.browse(cr, uid, uid, context=context)
		company_id 		= u1.company_id.id
		date_voucher 	= date.today().strftime('%Y-%m-%d')

		journal_bni = self.find_journal_by_code(cr, uid, 'BNI')
		if not journal_bni:
			raise osv.except_osv(_('Error'),_("no journal with code BNI, please create one") ) 

		##################################################################################
		# connection parameters
		##################################################################################
		self.get_params(cr, uid, context=context)
		spc = bni.spc()
		spc.connect(host=self.spc_hostname, user=self.spc_username, passwd=self.spc_password, db=self.spc_dbname)

		##################################################################################
		# loop setiap record import ca_pembayaran
		##################################################################################
		i = 0

		for temp in spc.read_ca_pembayaran():
			
			_logger.warning('   temp ' )
			_logger.warning(temp)


			invoice_id = self.find_invoice_by_number(cr, uid, temp['id_record_tagihan'] ) #no invoice
			if not invoice_id:
				raise osv.except_osv(_('Error'),_("no invoice with number %s") % (temp['id_record_tagihan'] ) ) 

			###########################################################################
			# tambah logic jika invoice tsb di paid manual skip saja
			###########################################################################
			if invoice_id.state != 'open' :	
				continue

			partner_id = invoice_id.partner_id.id 
			amount     = invoice_id.amount_total

			vid=self.create_payment(cr, uid, invoice_id, partner_id, amount, journal_bni, company_id, context=context)
			self.payment_confirm(cr, uid, vid, context=context)

			spc.set_ca_pembayaran_processed( temp['id_record_pembayaran'] )

			cr.commit()

			i = i + 1

		delta = 0
		spc.close()

		_logger.warning('Done processing. %s payment import(s) in %s ' % (i, str(delta)) )		
		return True 


	####################################################################################
	#create payment 
	#invoice_id: yang mau dibayar
	#journal_id: payment method
	####################################################################################
	def create_payment(self, cr, uid, inv, partner_id, amount, journal, company_id, context=None):
		voucher_lines = []

		#cari invoice
		# inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
		
		#cari move_line yang move_id nya = invoice.move_id
		move_line_id = self.pool.get('account.move.line').search( cr, uid, [('move_id.id','=', inv.move_id.id)] );
		move_lines = self.pool.get('account.move.line').browse(cr, uid, move_line_id)
		move_line = move_lines[0] # yang AR saja

		voucher_lines.append((0,0,{
			'move_line_id': 		move_line.id,
			'account_id':			move_line.account_id.id,
			'amount_original':		move_line.debit,
			'amount_unreconciled':	move_line.debit,
			'reconcile':			True,
			'amount':				move_line.debit,
			'type':					'cr',
			'name':					move_line.name,
			'company_id':  			company_id
		}))
		

		voucher_id = self.pool.get('account.voucher').create(cr,uid,{
			'partner_id' 	: partner_id,
			'amount' 		: amount,
			'account_id'	: journal.default_debit_account_id.id,
			'journal_id'	: journal.id,
			'reference' 	: 'payment #',
			'name' 			: 'payment #',
			'company_id' 	: company_id,
			'type'			: 'receipt',
			'line_ids'		: voucher_lines
		    })
		_logger.info("   created payment id:%d" % (voucher_id) )
		return voucher_id

	####################################################################################
	#set done
	####################################################################################
	def payment_confirm(self, cr, uid, vid, context=None):
		wf_service = netsvc.LocalService('workflow')
		wf_service.trg_validate(uid, 'account.voucher', vid, 'proforma_voucher', cr)
		_logger.info("   confirmed payment id:%d" % (vid) ) 
		return True


	####################################################################################
	# find invoice by number
	####################################################################################
	def find_invoice_by_number(self, cr, uid, number, context=None):
		invoice_obj = self.pool.get('account.invoice')
		invoice_id = invoice_obj.search(cr, uid, [('number','=', number)], context=context)
		invoice = invoice_obj.browse(cr, uid, invoice_id, context=context)
		return invoice


	####################################################################################
	# find journal by code
	####################################################################################
	def find_journal_by_code(self, cr, uid, code, context=None):
		journal_obj = self.pool.get('account.journal')
		journal_id = journal_obj.search(cr, uid, [('code','=', code)], context=context)
		journal = journal_obj.browse(cr, uid, journal_id, context=context)
		return journal