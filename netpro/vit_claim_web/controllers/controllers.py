# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson
import logging
_logger = logging.getLogger(__name__)
import time
from datetime import datetime

class Member(http.Controller):

	#@http.route('autocomplete', )

	######################################################################################
	# halaman registration
	# muncul search patient, action ke eligibility
	######################################################################################
	@http.route('/claim/registration', auth='user', website=True)
	def registration(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')
		return http.request.render('vit_claim_web.search',
			{'target'		: '/claim/eligibility', 
			'target_title'	: 'Registration', 
			'message_error'	: message_error,
			'message_success': message_success
		} )	

	######################################################################################
	# pengecekan eligibility pasien 
	######################################################################################
	@http.route('/claim/eligibility', auth='user', website=True)
	def eligibility(self, **kw):
		member = False
		message = "";

		if request.httprequest.method == 'POST':
			Member = http.request.env['netpro.member']
			member = Member.search([('card_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				# return http.request.render('vit_claim_web.registration', {'message':message} )	
				return request.redirect('/claim/registration?message_error=%s'% (message), code=301)

			passed = True
			now = datetime.now()
			member_period = time.strptime(member.insurance_period_end,"%Y-%m-%d")
			end_period = datetime(member_period[0], member_period[1], member_period[2])
			if now > end_period:
				passed = False

			if not passed or member.state == 'nonactive' or member.upd_code == 'R':
				message = "Member is Inactive! Transaction cannot be processed.<br />"
				message += "Insurance Date End : "+member.insurance_period_end+"<br />"
				message += "Member State : "+member.state+"<br />"
				if member.upd_code:
					message += "Member Code : "+member.upd_code
				return request.redirect('/claim/registration?message_error=%s'% (message), code=301)

			##############################################################################
			# cari data claim member tsb yang masih open
			##############################################################################
			Claim  = http.request.env['netpro.claim']
			claim = Claim.search([('member_id','=',member.id), ('state','=', 'open')])
			if claim:
				message = "Found existing Open Claim No %s, please discharge first. " % (claim[0].claim_no) 
				return request.redirect('/claim/registration?message_error=%s'% (message), code=301)

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
				return request.redirect('/claim/registration?message_error=%s'% (message), code=301)

		# cari benefit member sesuai member_plan (RI, RJ, dll)

		currency = http.request.env['netpro.claim']

		return http.request.render('vit_claim_web.loa', {
			'member'		: member, 
			'member_plan'	: member_plan,
			'message'		: message
		})

	# # # # # # # # # # # # # # # # # # # # # 
	# 		REPLACE EMAIL GLOSSARY 			#
	# # # # # # # # # # # # # # # # # # # # # 
	def replaceString(self,content,claim,plan):
		ret = ''
		benefits = ''
		for pl in plan.member_plan_detail_ids:
			benefits += pl.benefit_id.name + '			: '+ '{0:,.2f}'.format(int(pl.remaining)) + '\n'

		if content.find('[claim_no]'):
			ret += content.replace('[claim_no]', claim.claim_no)
		if content.find('[benefit]'):
			ret += content.replace('[benefit]', str(benefits))
		if content.find('[member_name]'):
			ret += content.replace('[member_name]', claim.member_id.name)
		return content

	######################################################################################
	# proses registration patient: 
	# print, email, save: insert transaksi claim
	######################################################################################
	@http.route('/claim/registration_process', auth='user', website=True)
	def registration_process(self, **kw):
		# import pdb;pdb.set_trace()
		message = kw.get('message','')
		member_id = kw.get('member_id', '')
		member_data = http.request.env['netpro.member'].browse(int(member_id))
		policy_id = http.request.env['netpro.policy'].browse(int(member_data.policy_id.id))
		member_plan_id = kw.get('member_plan_id', False)
		MemberPlan = http.request.env['netpro.member_plan']
		member_plan = MemberPlan.browse(int(member_plan_id))

		email_template_obj = http.request.env['netpro.email_template']
		email_template = email_template_obj.search([('name','=','claim_email')])

		if not member_plan:
			message = "Member Plan not found! Please try again."
			return request.redirect('/claim/registration?message_error=%s'% (message), code=301)

		Claim  = http.request.env['netpro.claim']
		claim_data = {}

		if kw.get('confirm') == '':
			##############################################################################
			# insert into netpro_claim
			##############################################################################

			claim_details = [(0,0,{'benefit_id' : x.benefit_id.id}) for x in member_plan.member_plan_detail_ids]

			data = {
				'claim_date'		: time.strftime("%Y-%m-%d"),
				'member_id'			: int(member_id),
				'policy_id'			: int(policy_id.id),
				'member_plan_id'	: member_plan.id ,
				'claim_detail_ids'  : claim_details,
				'state'  			: "open",
			}
			claim_data = Claim.create(data)
			message = "Claim Registration Success!"
		
		if kw.get('email') == '':
			if member_data.email:
				claim_data = Claim.browse(int(kw.get('claim_id')))
				
				subject_email = ''
				body_email = ''

				if email_template:
					subject_email = self.replaceString(email_template.subject, claim_data, member_plan)
					body_email = self.replaceString(email_template.body, claim_data, member_plan)
					
				values = {
					'subject' : subject_email,
					'email_to' : member_data.email,
					'body_html' : body_email,
					'res_id' : False,
				}
				mail_mail_obj = http.request.env['mail.mail']
				msg_id = mail_mail_obj.create(values)
				#mail_mail_obj.send(msg_id.id)
				message = "Message Sent"
	        else :
	        	message = "Member's email cannot be found, please filling email on member form to sending email."

		#return request.redirect('/claim/registration?message_success=%s'% (message), code=301)
		return http.request.render('vit_claim_web.loa', {
			'member'		: member_data, 
			'member_plan'	: member_plan,
			'claim'			: claim_data,
			'message'		: message
		})

	######################################################################################
	# halaman utama discrhage, munculkan search patient
	# action ke discharge_confirmation
	######################################################################################
	@http.route('/claim/discharge', auth='user', website=True)
	def discharge(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')
		return http.request.render('vit_claim_web.search', 
			{'target':'/claim/discharge_confirmation' , 
			'target_title':'Discharge', 
			'message_error':message_error,
			'message_success':message_success
			} )	

	######################################################################################
	# discharge confirm, pengesahan
	# cari data registrasi awal (claim)
	# jika ada:
	# masukkan angka2 yang di-claim
	######################################################################################
	@http.route('/claim/discharge_confirmation', auth='user', website=True)
	def discharge_confirmation(self, **kw):
		member = False
		message = "";

		if request.httprequest.method == 'POST':
			##############################################################################
			# cari dulu data member
			##############################################################################
			Member = http.request.env['netpro.member']
			member = Member.search([('card_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				return request.redirect('/claim/discharge?message_error=%s'% (message), code=301)

			##############################################################################
			# cari data claim member tsb yang masih open
			##############################################################################
			Claim  = http.request.env['netpro.claim']
			claim = Claim.search([('member_id','=',member.id), ('state','=', 'open')])
			if not claim:
				message = "Claim Registration not found!"
				return request.redirect('/claim/discharge?message_error=%s'% (message), code=301)

			if len(claim) > 1:
				message = "Found more than 1 claim registration!"
				return request.redirect('/claim/discharge?message_error=%s'% (message), code=301)

			claim = claim[0]

			##############################################################################
			# diagnosis data / harus autocomplete
			##############################################################################
			Diagnosis  = http.request.env['netpro.diagnosis']
			diagnosis = Diagnosis.search([])

			return http.request.render('vit_claim_web.discharge_confirmation', 
				{'member'	: member, 
				'claim'		: claim, 
				'member_plan' : claim.member_plan_id,
				'diagnosis'	: diagnosis,
				'message'	: message})

	######################################################################################
	# convert kw string to array
	######################################################################################
	def string2array(self, name, kw):
		res = {}
		for k in kw.keys():
			if k.find('.') != -1:
				x = k.split('.')
				if x[0] == name:
					res[ int(x[1]) ] = kw.get(k)

		return res

	def collectDiagnosis(self, name, kw):
		res = {}

		for k in kw.keys():
			if k.startswith(name):
				data = http.request.env['netpro.diagnosis'].browse(int(kw.get(k)))
				res[int(kw.get(k))] = float(data.standard_fee)

		return res

	######################################################################################
	# proses discharge: update transaksi claim detail
	######################################################################################
	@http.route('/claim/discharge_process', auth='user', website=True)
	def discharge_process(self, **kw):
		message = "";

		if request.httprequest.method == 'POST':
			##############################################################################
			# cari dulu data member
			##############################################################################
			Member = http.request.env['netpro.member']
			# MemberPlan = http.request.env['netpro.member_plan']
			Claim  = http.request.env['netpro.claim']

			member = Member.search([('id','=',kw.get('member_id','') )])
			#member_plan = MemberPlan.search([('id','=',kw.get('member_plan_id','') )])

			# if not member:
			# 	message = "Member not found! Please try again."
			# 	return request.redirect('/claim/discharge?message=%s'% (message), code=301)

			# ##############################################################################
			# # cari data claim member tsb yang masih open
			# ##############################################################################
			claim = Claim.search([('id','=', kw.get('claim_id',''))])

			claim_details = self.string2array('claim_details', kw)

			diagnosis_list = self.collectDiagnosis('diagnosis_', kw)

			##############################################################################
			# update detail claim
			##############################################################################
			claim_detail_ids = [
				(1, x , { 'billed': float(claim_details[x]), 'excess': float( kw.get('excess.'+str(x), 0) ), 'accepted': float(kw.get('accept.'+str(x), 0)) }) for x in claim_details.keys()
			]

			# prepare data diagnosis
			diagnosis_datas = [
				(0, 0, {'diagnosis_id': xx, 'standard_fee': diagnosis_list[xx]}) for xx in diagnosis_list.keys()
			]

			# loop to get summary accepted, excess
			total_accepted = 0
			total_billed = 0
			total_excess = 0
			for x in claim_details.keys():
				total_accepted += float( kw.get('accept.'+str(x), 0) )
				total_billed += float( kw.get('claim_details.'+str(x), 0) )
				total_excess += float( kw.get('excess.'+str(x), 0) )

			claim.write({
				'summary_accepted' 	 : total_accepted,
				'summary_billed' 	 : total_billed,
				'sumary_total_excess': total_excess,
				'claim_detail_ids' 	 : claim_detail_ids,
				'diagnosis_ids'		 : diagnosis_datas,
			})

			claim.action_close() # cara memanggil action di object

			Diagnosis  = http.request.env['netpro.diagnosis']
			diagnosis = Diagnosis.search([])

			message = "Discharge Success!"
			#return request.redirect('/claim/discharge?message_success=%s'% (message), code=301)
			return http.request.render('vit_claim_web.discharge_confirmation', 
				{'member'	: member, 
				'claim'		: claim, 
				'member_plan' : claim.member_plan_id,
				'diagnosis'	: diagnosis,
				'message'	: message})


	######################################################################################
	# halaman search claim
	# muncul search patient, action ke claim list
	######################################################################################
	@http.route('/claim/search', auth='user', website=True)
	def search(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')
		return http.request.render('vit_claim_web.search',
			{'target'		: '/claim/claim_list', 
			'target_title'	: 'Search Claim', 
			'message_error'	: message_error,
			'message_success': message_success
		} )	

	######################################################################################
	# action ke claim list
	######################################################################################
	@http.route('/claim/claim_list', auth='user', website=True)
	def claim_list(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')

		if request.httprequest.method == 'POST':
			##############################################################################
			# cari dulu data member
			##############################################################################
			Member = http.request.env['netpro.member']
			member = Member.search([('card_no','=',kw.get('card_no','') )])
			if not member:
				message = "Member not found! Please try again."
				return request.redirect('/claim/search?message_error=%s'% (message), code=301)

			##############################################################################
			# cari data claim member tsb yang masih open
			##############################################################################
			Claim  = http.request.env['netpro.claim']
			claim_ids = Claim.search([('member_id','=',member.id) ])
			if not claim_ids:
				message = "Claim Registration not found!"
				return request.redirect('/claim/search?message_error=%s'% (message), code=301)

			# import pdb; pdb.set_trace()
			# claims = Claim.browse(claim_ids)

			return http.request.render('vit_claim_web.claim_list',
				{'message_error'	: message_error,
				'message_success'	: message_success,
				'claims' 			: claim_ids,
				'member'			: member 
			} )	

	@http.route('/claim/check_excess', type='json', auth="public", website=True)
	def check_excess(self,**kw):
		benefit = kw.get('benefit')
		mplan = kw.get('mplanid')
		nilai = kw.get('nilai')
		isexcess = False
		excess = 0
		accept = float(nilai)
		mplan_data = http.request.env['netpro.member_plan_detail'].search([('member_plan_id','=',int(mplan)), ('benefit_id','=',int(benefit))])
		if float(nilai) > float(mplan_data.remaining):
			isexcess = True
			excess = float(nilai) - float(mplan_data.remaining)
			accept = mplan_data.remaining
		res = {}
		res['success'] = isexcess
		res['excess'] = excess
		res['accepted'] = accept
		return simplejson.dumps(res)