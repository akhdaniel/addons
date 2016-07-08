# -*- coding: utf-8 -*-

###############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2009-TODAY Tech-Receptives(<http://www.techreceptives.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields


class arus_kas(models.Model):
	_name = 'arus.kas'
	_rec_name = 'account_id'

	account_id 			= fields.Many2one('account.account','Chart of Account')
	period_start_id  	= fields.Many2one('account.period','Period Start')
	period_end_id    	= fields.Many2one('account.period','Period End',)
	user_id    			= fields.Many2one('res.users','Period End',)
	arus_kas_detail_ids	= fields.One2many('arus.kas.detail','arus_kas_id','Arus Kas Detail')
	t_initial_balance	= fields.Float('Total Starting Balance')
	t_balance			= fields.Float('Total Ending Balance')


arus_kas()


class arus_kas_detail(models.Model): 
	_name = 'arus.kas.detail' 

	arus_kas_id 	= fields.Many2one('arus.kas','Arus Kas ID')
	date 			= fields.Date('Date')
	description  	= fields.Char('Description')
	narration    	= fields.Char('Notes')
	initial_balance	= fields.Float('Init Balance')
	debit 			= fields.Float('Debit')
	credit			= fields.Float('Credit')
	balance			= fields.Float('Balance')

arus_kas_detail()