from osv import osv,fields
from openerp.tools.translate import _
import datetime 

class account_move_wizard(osv.TransientModel): 
	_name = 'account.move.wizard' 

	_columns = {
		'type':fields.selection([('post','Post'), ('cancel','Cancel')], 'Type', required=True),
		'entry_post_ids':fields.many2many('account.move', string='Journals Entries', domain="[('state','=','draft')]"),
		'entry_cancel_ids':fields.many2many('account.move', string='Journals Entries', domain="[('state','=','posted')]"),
	}



	def post_cancel_journal_entries(self, cr, uid, ids, context=None):
		i = len(ids)
		for jr in self.browse(cr,uid, ids, context):
			entries_obj = self.pool.get('account.move')
			
			if jr.type == 'post' :
				for journal in jr.entry_post_ids:
					sql = "update account_move set state = 'posted' where id = %s" % (journal.id)
					cr.execute(sql)					
			elif jr.type == 'cancel' :
				for journal in jr.entry_cancel_ids:				
					sql = "update account_move set state = 'draft' where id = %s" % (journal.id)
					cr.execute(sql)
		view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'account', 'view_move_tree')
		view_id = view_ref and view_ref[1] or False,	
		return {
			'warning': {'title': _('OK!'),'message': _('Done processing. %s Journal Entry(s) %sed' % (i,jr.type) )}, 
			'name' : _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree',			
			'res_model': 'account.move',
			'res_id': ids[0],
			'type': 'ir.actions.act_window',
			'view_id': view_id,
			'target': 'current',
			"context":"{}",
			'nodestroy': False,
		}	