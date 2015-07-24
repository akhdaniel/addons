# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson
import logging
_logger = logging.getLogger(__name__)
import time

class Member(http.Controller):
	######################################################################################
	# halaman registration
	# muncul search patient, action ke eligibility
	######################################################################################
	@http.route('/claim/registration', auth='user', website=True)
	def registration(self, **kw):
		message = kw.get('message','')
		return http.request.render('vit_claim_web.search',
			{'target':'/claim/eligibility', 'target_title':'Registration', 'message':message} )	

	######################################################################################
	# pengecekan eligibility pasien 
	######################################################################################
	@http.route('/claim/eligibility', auth='user', website=True)
	def eligibility(self, **kw):
		member = False
		message = "";

		if request.httprequest.method == 'POST':
			Member = http.request.env['netpro.member']
			member = Member.search([('member_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				# return http.request.render('vit_claim_web.registration', {'message':message} )	
				return request.redirect('/claim/registration?message=%s'% (message), code=301)

		return http.request.render('vit_claim_web.eligibility', 
			{'member': member, 'message':message})


	######################################################################################
	# penampilan letter of authority
	# benefit yg didapat patient dari suatu coverage yg dipilih
	# == registration confirmation
	# action POST ke registration_process
	######################################################################################
	@http.route('/claim/loa/<model("netpro.member"):member>/<model("netpro.member_plan"):member_plan>', auth='user', website=True)
	def loa(self, member, member_plan, **kw):
		message = "";

		if request.httprequest.method == 'GET':
			if not member:
				message = "Member not found! Please try again."
				# return http.request.render('vit_claim_web.registration', {'message':message} )	
				return request.redirect('/claim/registration?message=%s'% (message), code=301)

		# cari benefit member sesuai member_plan (RI, RJ, dll)


		return http.request.render('vit_claim_web.loa', {
			'member'		: member, 
			'member_plan'	: member_plan,
			'message'		: message
		})

	######################################################################################
	# proses registration patient: 
	# print, email, save: insert transaksi claim
	######################################################################################
	@http.route('/claim/registration_process', auth='user', website=True)
	def registration_process(self, **kw):
		message = kw.get('message','')
		member_id = kw.get('member_id', '')
		member_plan_id = kw.get('member_plan_id', False)
		MemberPlan = http.request.env['netpro.member_plan']
		member_plan = MemberPlan.browse( int(member_plan_id))

		if not member_plan:
			raise osv.except_osv(_('Error'),_("Member Plan not found!") ) 

		#insert into netpro_claim
		Claim = http.request.env['netpro.claim']
		data = {
			'claim_date'	: time.strftime("%Y-%m-%d"),
			'member_id'		: int(member_id),
			'product_plan_base_id'	: member_plan.plan_schedule_id.product_plan_base_id.id 
		}
		Claim.create(data)

		return http.request.render('vit_claim_web.registration_process', {} )	


	######################################################################################
	# halaman utama discrhage, munculkan search patient
	# action ke discharge_confirmation
	######################################################################################
	@http.route('/claim/discharge', auth='user', website=True)
	def discharge(self, **kw):
		message = kw.get('message','')
		return http.request.render('vit_claim_web.search', 
			{'target':'/claim/discharge_confirmation' , 'target_title':'Discharge', 'message':message} )	

	######################################################################################
	# discharge confirm, pengesahan
	# masukkan angka2 yang di-claim
	######################################################################################
	@http.route('/claim/discharge_confirmation', auth='user', website=True)
	def discharge_confirmation(self, **kw):
		member = False
		message = "";

		if request.httprequest.method == 'POST':
			Member = http.request.env['netpro.member']
			member = Member.search([('member_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				return request.redirect('/claim/discharge?message=%s'% (message), code=301)

		return http.request.render('vit_claim_web.discharge_confirmation', 
			{'member': member, 'message':message})


	######################################################################################
	# proses discharge: insert transaksi claim
	######################################################################################
	@http.route('/claim/discharge_process', auth='user', website=True)
	def discharge_process(self, **kw):
		message = "";
		return http.request.render('vit_claim_web.discharge_process', 
			{ 'message':message })

	# @http.route('/mlm/member/list', auth='user', website=True)
	# def list(self, **kw):		
	# 	Partners = http.request.env['res.partner']
	# 	Mymembers = self._cari_users_members(request.cr, request.uid, request.uid, request.context)
	# 	return http.request.render('website.member_list', {
	# 		'members': Partners.search([('id','in',Mymembers)])
	# 	}) 

	# @http.route('/mlm/member/view/<model("res.partner"):member>',  auth='user', website=True)
	# def view(self, member):
	# 	# Member = http.request.env['res.partner']
	# 	# Paket  = http.request.env['mlm.paket']
	# 	# State = http.request.env['res.country.state']
	# 	# Country = http.request.env['res.country']
	# 	# Products  = http.request.env['mlm.paket_produk']
	# 	return http.request.render('website.member_view', {
	# 		'member': member,
	# 		'products': member.paket_produk_ids,
	# 		# 'members': Member.search([]),
	# 		# 'pakets': Paket.search([]),
	# 		# 'states': State.search([]),
	# 		# 'countrys': Country.search([]),
	# 	})

	# @http.route('/mlm/member/json/<int:parent_id>',  auth='user', website=True)
	# def json(self, parent_id):
	# 	Members = http.request.env['res.partner']
	# 	members = Members.search([('parent_id','=',parent_id)])
	# 	return members

	# @http.route('/mlm/stockist',  auth='public', website=True)
	# def stockist(self, **kw):
	# 	Members = http.request.env['res.partner']
	# 	members = Members.search([('is_stockist','=',True)])
	# 	return http.request.render('website.member_list', {
	# 		'members': members
	# 	})

	# @http.route('/mlm/member/create',  auth='user', website=True)
	# def create(self, **kwargs):
	# 	cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
		
	# 	Users  = pool['res.users']
	# 	user   = Users.browse(cr, uid, uid, context=context)
	# 	parent = user.partner_id

	# 	Member  = http.request.env['res.partner']
	# 	Paket  = http.request.env['mlm.paket']
	# 	State = http.request.env['res.country.state']
	# 	Country = http.request.env['res.country']
	# 	Products  = http.request.env['mlm.paket_produk']
	# 	Mymembers = self._cari_users_members(cr, uid, uid, context)
	# 	values = {}
	# 	for field in ['name', 'sponsor_id', 'parent_id', 'paket_id', 'street', 
	# 		'street2', 'zip', 'city', 'state_id', 'country_id', 'bbm', 'email', 
	# 		'phone','fax','mobile','paket_produk_id','signature','paket_produk_ids']:
	# 		if kwargs.get(field):
	# 			values[field] = kwargs.pop(field)
	# 	values.update(kwargs=kwargs.items())
	# 	values.update({
	# 		'parent' : parent,
	# 		'member' : None,
	# 		'pakets' : Paket.search([]),
	# 		'members': Member.search([('id','in',Mymembers)]),
	# 		'states': State.search([]),
	# 		'countrys': Country.search([]),
	# 		'products': Products.search([]),

	# 	})
	# 	return http.request.render('website.member_create', values)

	# def create_partner(self, request, values, kwargs):
	# 	""" Allow to be overrided """
	# 	return request.registry['res.partner'].create(request.cr, SUPERUSER_ID, values, request.context)

	# def add_partner_response(self, values, kwargs):
	# 	return request.website.render(kwargs.get("view_callback", "website.add_member_thanks"), values)

	# @http.route('/mlm/member/add',  auth='user', method=['POST'], website=True)
	# def add_member(self, **kwargs):
	# 	cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

	# 	def dict_to_str(title, dictvar):
	# 		ret = "\n\n%s" % title
	# 		for field in dictvar:
	# 			ret += "\n%s" % field
	# 		return ret

	# 	_TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
	# 	_BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description
	# 	_REQUIRED = ['name']  # Could be improved including required from model

	# 	post_file = []  # List of file to add to ir_attachment once we have the ID
	# 	post_description = []  # Info to add after the message
	# 	values = {}
	# 	paket_produk_ids = []
	# 	for field_name, field_value in kwargs.items():
	# 		if hasattr(field_value, 'filename'):
	# 			post_file.append(field_value)
	# 			if field_name=='signature':
	# 				values['signature'] = base64.encodestring(field_value.read())
	# 		elif field_name in request.registry['res.partner']._fields and field_name not in _BLACKLIST:
	# 			values[field_name] = field_value
	# 		elif field_name[:16] == 'paket_produk_ids' and field_value:
	# 			paket_produk_ids.append((0,0,{'paket_produk_id':int(field_name[17:-1]),'qty':int(field_value)}))
	# 		elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
	# 			post_description.append("%s: %s" % (field_name, field_value))
	# 			values[field_name] = field_value
	# 	if paket_produk_ids:
	# 		values['paket_produk_ids'] = paket_produk_ids
	# 	error = set(field for field in _REQUIRED if not values.get(field))

	# 	if error:
	# 		values = dict(values, error=error, kwargs=kwargs.items())
	# 		return request.website.render(kwargs.get("view_from", "website.member_create"), values)

	# 	if post_description:
	# 		values['description'] += dict_to_str(_("Custom Fields: "), post_description)
	# 	lead_id = self.create_partner(request, dict(values, user_id=False), 
	# 		kwargs)
	# 	values.update(lead_id=lead_id)
	# 	if lead_id:
	# 		for field_value in post_file:
	# 			attachment_value = {
	# 				'name': 'Signature of '+values['name']+':'+field_value.filename,
	# 				'res_name': field_value.filename,
	# 				'res_model': 'res.partner',
	# 				'res_id': lead_id,
	# 				'datas': values['signature'],
	# 				'datas_fname': field_value.filename,
	# 			}
	# 			request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value, context=request.context)

	# 	return request.redirect('/mlm/member/view/%d'% (lead_id), code=301)

	# @http.route('/mlm/member/edit/<model("res.partner"):member>',  auth='user', website=True)
	# def edit(self, member, **kwargs):
	# 	Member = http.request.env['res.partner']
	# 	Paket  = http.request.env['mlm.paket']
	# 	State = http.request.env['res.country.state']
	# 	Country = http.request.env['res.country']
	# 	return http.request.render('website.member_edit', {
	# 		'member': member,
	# 		'parent': member.parent_id,
	# 		'members': Member.search([]),
	# 		'pakets': Paket.search([]),
	# 		'states': State.search([]),
	# 		'countrys': Country.search([]),
	# 		'kwargs':kwargs.items(),
	# 	})

	# @http.route('/mlm/member/update',  auth='user', method='post', website=True)		
	# def update_member(self, **kwargs):
	# 	id = int(kwargs['id'])
	# 	request.registry['res.partner'].write(request.cr, SUPERUSER_ID, [id], kwargs, request.context)
	# 	return request.redirect('/mlm/member/view/%d'% (id), code=301)

	# @http.route('/mlm/member/stockist',  auth='user', website=True)
	# def stockist(self, **kw):
	# 	cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
	# 	domain = [('is_stockist', '=', True)]
	# 	Partner = pool.get('res.partner')
	# 	Partner_ids = Partner.search(cr, uid, domain, context=context)
	# 	Partners = Partner.browse(cr, uid, Partner_ids, context=context)

	# 	return http.request.render('website.member_list', {
	# 		'members': Partners,
	# 	})

	# @http.route('/mlm/member/tree/<model("res.partner"):member>',  auth='user', website=True)
	# def tree(self,member):
	# 	return http.request.render('website.d3_member_tree', {
	# 		'member': member,
	# 	})

	# def _cari_users_members(self,cr,uid,user_id,context=None):
	# 	Users  = request.registry['res.users']
	# 	user   = Users.browse(cr, uid, user_id, context=context)
	# 	path   = user.partner_id and user.partner_id.path
	# 	partner_uid = user.partner_id and user.partner_id.id
	# 	sql="select id from res_partner where path_ltree <@ '%s' \
	# 		or (path_ltree is null and sponsor_id = %d) \
	# 		order by path_ltree" % (path,partner_uid)
	# 	cr.execute(sql)
	# 	member_ids = cr.fetchall()
	# 	return [x[0] for x in member_ids]

	# @http.route('/mlm/member/create/json/<int:country_id>',type='json')
	# def json(self,country_id):
	# 	cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
	# 	cr.execute("select id, name from res_country_state where country_id = %d" % country_id)
	# 	rows = cr.fetchall()
	# 	data = simplejson.dumps(dict(rows))
	# 	return data