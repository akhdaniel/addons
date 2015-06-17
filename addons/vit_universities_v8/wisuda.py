from openerp.osv import fields, osv
import time
from dateutil.relativedelta import relativedelta
import openerp
from datetime import datetime
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, image_resize_image_big


class wisuda_mahasiswa(osv.Model):
	_name = 'wisuda.mahasiswa'

	def onchange_angkatan(self, cr, uid, ids, tahun_ajaran_id, tgl_wisuda, kuota,context=None):

		results = {}
		if not tahun_ajaran_id:
			return results

		par_obj = self.pool.get('res.partner')
		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',tahun_ajaran_id),
			('wisuda','=',tgl_wisuda),
			('tgl_lulus','=',False),
			('judul','=',False),
			], context=context)

		#import pdb;pdb.set_trace()
		res = []
		x=0
		for peserta in par_ids:
			x += 1			
			if x > kuota :
				break
			res.append(peserta)
		#insert many2many records
		wisuda_line_ids = [(6,0,res)]
		results = {
			'value' : {
				'partner_ids' : wisuda_line_ids,
			}
		}
		return results

	_columns = {
		'name': fields.char('Kode',required=True,size=32),
		'tahun_ajaran_id':fields.many2one('academic.year',string='Tahun Akademik',required=True),
		'tgl_wisuda':fields.date('Tanggal Wisuda',required=True),
		'lokasi_wisuda':fields.char('Tempat Wisuda',size=128,required=True),
		'kuota':fields.integer('Kuota',required=True),
		'partner_ids':fields.many2many(
			'res.partner',   	# 'other.object.name' dengan siapa dia many2many
			'wisuda_mahasiswa_rel',          # 'relation object'
			'wisuda_id',               # 'actual.object.id' in relation table
			'partner_id',           # 'other.object.id' in relation table
			'Wisudawan/i',              # 'Field Name'
			domain="[('status_mahasiswa','=','Mahasiswa'), \
			('tahun_ajaran_id','=',tahun_ajaran_id),\
			('wisuda','=',tgl_wisuda),]",
			readonly=False),	
		'state':fields.selection([('draft','Draft'),('done','Alumni')],'Status'),
	}
	_defaults = {  
		'state':'draft',
				}

	def button_reload(self,cr,uid,ids,context=None):

		my_form = self.browse(cr,uid,ids[0])
		angkatan = my_form.tahun_ajaran_id.id
		tgl_wisuda = my_form.tgl_wisuda

		par_obj = self.pool.get('res.partner')

		par_ids = par_obj.search(cr, uid, [
			('status_mahasiswa','=','Mahasiswa'),
			('tahun_ajaran_id','=',angkatan),
			('wisuda','=',tgl_wisuda),
			('tgl_lulus','!=',False),
			('judul','!=',False),
			], context=context)
		res = []
		x=0
		for peserta in par_ids:
			x += 1			
			if x > my_form.kuota :
				break
			res.append(peserta)
		#insert many2many records
		wisuda_line_ids = [(6,0,res)]
		
		self.write(cr,uid,ids[0],{'partner_ids':wisuda_line_ids,},context=context)
		return True

	def confirm(self,cr,uid,ids,context=None):
		my_form = self.browse(cr,uid,ids[0])
		for alumni in my_form.partner_ids:
			gelar = alumni.prodi_id.gelar_id.id
			#import pdb;pdb.set_trace()
			self.pool.get('res.partner').write(cr,uid,alumni.id,{'status_mahasiswa':'alumni','lokasi_wisuda':my_form.lokasi_wisuda,'title':gelar},context=context)
		self.write(cr,uid,ids,{'state':'done'},context=context)
		return True	

	def unlink(self, cr, uid, ids, context=None):
		if context is None:
			context = {}
		"""Allows to delete in draft state"""
		for rec in self.browse(cr, uid, ids, context=context):
			if rec.state != 'draft':
				raise osv.except_osv(_('Error!'), _('Data yang dapat dihapus hanya yang berstatus draft'))
		return super(wisuda_mahasiswa, self).unlink(cr, uid, ids, context=context)