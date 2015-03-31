from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mlm_plan(osv.osv):
	_name 		= "mlm.mlm_plan"
	_columns 	= {
		'name'				: fields.char('Name',required=True),
		'code'				: fields.char('Code',required=True),
		'max_downline'		: fields.integer('Max Downline',
			help='Berapa jumlah max downline suatu titik, isi dengan 0 untuk unlimited'),

		###############################################################
		# bonus sponsor
		###############################################################
		'bonus_sponsor'		: fields.float('Bonus Sponsor Amount', 
			help="Berapa nilai bonus sponsor, isi dengan 0 utk tidak ada bonus sponsor"),
		'max_bonus_sponsor_level'	: fields.integer('Max Bonus Sponsor Depth (Up)',
			help='Berapa jumlah level (keatas) dimana Upline masih dapat Bonus Sponsor, isi dengan 0 untuk unlimited'),
		'bonus_sponsor_percent_decrease': fields.float("Bonus Sponsor Percent Decrease",
			help='Berapa persen penurunan Bonus Sponsor untuk setiap level ke atasnya. Isi dengan 0.0-1.0, nilai 1 artinya tidak ada penurunan'),
		
		###############################################################
		# bonus level
		###############################################################
		'bonus_level'		: fields.float('Bonus Level Amount', 
			help="Berapa nilai bonus level, isi dengan 0 untuk tidak ada bonus level"),
		'max_bonus_level_level'	: fields.integer('Max Bonus Level Depth',
			help='Berapa jumlah kedalaman level yang masih dapat bonus level, isi dengan 0 untuk unlimited'),
		'bonus_level_percent_decrease': fields.float("Bonus Level Percent Decrease",
			help='Berapa persen penurunan Bonus Level untuk setiap level ke atasnya. Isi dengan 0.0-1.0, nilai 1 artinya tidak ada penurunan'),
		'full_level'		: fields.boolean('Force Full Level?',
			help='Bonus level terjadi ketika jumlah level sudah Full atau minimal 1 di kiri dan 1 di kanan'),

		###############################################################
		# bonus pasangan
		###############################################################
		'bonus_pasangan'	: fields.float('Bonus Pasangan Amount', 
			help="Berapa nilai bonus pasangan, isi dengan 0 untuk tidak ada bonus pasangan"),
		'max_bonus_pasangan_level'	: fields.integer('Max Bonus Pasangan Depth',
			help='Berapa jumlah kedalaman level yang masih dapat bonus pasangan, isi dengan 0 untuk unlimited'),
		'bonus_pasangan_percent_decrease': fields.float("Bonus Pasangan Percent Decrease",
			help='Berapa persen penurunan Bonus Pasangan untuk setiap level ke atasnya. Isi dengan 0.0-1.0, nilai 1 artinya tidak ada penurunan'),


	}