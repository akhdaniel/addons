# -*- coding: utf-8 -*-

######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

from openerp.osv import fields, osv
import tools
import time

class vit_account_aging_wizard(osv.osv_memory):
	_name = 'vit.account.aging.wizard'

	_columns ={
		'cut_off': fields.date('Cut Off Date', required=True),
		}

	_defaults = {
		'cut_off': fields.date.context_today,
		}        

class vit_partner_aging_customer(osv.Model):
	_name = 'vit.partner.aging.customer'
	_auto = False
	_order = 'partner_id'


	_columns = {
		'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
		'date': fields.date('Due Date', readonly=True),
		'total': fields.float('Total', readonly=True),
		'days_due_01to30': fields.float('01/30', readonly=True),
		'days_due_31to60': fields.float(u'31/60', readonly=True),
		'days_due_61to90': fields.float(u'61/90', readonly=True),
		'days_due_91to120': fields.float(u'91/120', readonly=True),
		'days_due_121togr': fields.float(u'+121', readonly=True),
		'current': fields.float(u'Current', readonly=True),
		'max_days_overdue': fields.float(u'Days Overdue', readonly=True),
		'ref': fields.char('Reference', size=25, readonly=True),

	 }

	def init(self, cr):
		"""
		@author       vitraining.com
		@description  Update table on load with latest aging information
		"""

		tools.drop_view_if_exists(cr, 'vit_partner_aging_customer')
		cr.execute("""
			CREATE OR REPLACE VIEW vit_partner_aging_customer AS (

				SELECT partner_id AS id, SUM(total) AS total, partner_id, SUM(days_due_01to30) AS days_due_01to30, 
				SUM(days_due_31to60) AS days_due_31to60, SUM(days_due_61to90) AS days_due_61to90,
				SUM(days_due_91to120) AS days_due_91to120, SUM(days_due_121togr) AS days_due_121togr,
				SUM(max_days_overdue) AS max_days_overdue, SUM(current) AS current from	

					(SELECT DaysDue.id as id,SUM(debit-credit) AS total,DaysDue.partner_id,DaysDue.ref,days_due,move_id,

						CASE WHEN (days_due BETWEEN 1 and 30) THEN debit-credit 
						ELSE 0 END  AS "days_due_01to30",

						CASE WHEN (days_due BETWEEN 31 and 60) THEN debit-credit  
						ELSE 0 END  AS "days_due_31to60",

						CASE WHEN (days_due BETWEEN 61 and 90) THEN debit-credit  
						ELSE 0 END  AS "days_due_61to90",

						CASE WHEN (days_due BETWEEN 91 and 120) THEN debit-credit  
						ELSE 0 END  AS "days_due_91to120",	
						
						CASE WHEN days_due >= 121 THEN debit-credit
						ELSE 0 END  AS "days_due_121togr",

						CASE WHEN days_due < 0 or days_due is null THEN debit-credit
						ELSE 0 END  AS "max_days_overdue",

						CASE WHEN days_due <= 0 THEN debit-credit
						ELSE 0 END  AS "current"

						FROM 
							(
							SELECT lt.id as id,lt.partner_id as partner_id,lt.debit AS debit,lt.credit AS credit,
							lt.ref as ref,lt.account_id as account_id,move_id as move_id,
						    CASE WHEN lt.partner_id is not null THEN  COALESCE(EXTRACT(DAY FROM (now() - lt.date)),0)::INT END AS days_due
							FROM account_move_line lt
							GROUP BY lt.partner_id,lt.id,days_due,lt.id,lt.ref
							) AS DaysDue

						INNER JOIN account_account aa
						ON aa.id = account_id
						INNER JOIN account_move am
						ON am.id = move_id

					WHERE aa.active
					AND (aa.type IN ('receivable'))
					AND DaysDue.partner_id is not null
					AND am.state = 'posted'

					GROUP BY DaysDue.id,days_due,DaysDue.ref,account_id,DaysDue.debit,DaysDue.credit,daysdue.partner_id,DaysDue.move_id) AS foo
					
					GROUP BY partner_id
		
		)""")	

vit_partner_aging_customer()