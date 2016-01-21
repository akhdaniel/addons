# -*- coding: utf-8 -*-
from openerp import http, SUPERUSER_ID
from openerp.http import request
import base64
import simplejson
import logging
_logger = logging.getLogger(__name__)
import time
from datetime import datetime

class Spmb(http.Controller):

	######################################################################################
	# halaman registration
	# muncul form registrasi, action ke registraion_process
	######################################################################################
	@http.route('/spmb/registration', auth='public', website=True)
	def registration(self, **kw):
		message_error = kw.get('message_error','')
		message_success = kw.get('message_success','')

		Prodi  = http.request.env['master.prodi']
		prodi_ids = Prodi.search([])

		Tahun  = http.request.env['academic.year']
		tahun_ids = Tahun.search([])

		Semester  = http.request.env['master.semester']
		semester_ids = Semester.search([])

		pekerjaans = [('psn','Pengawai Negeri Sipil'),('tni','TNI'),('petani','Petani'),('peg_swasta', 'Pegawai Swasta'),('wiraswasta','Wiraswasta'),('none','Tidak Bekerja'),('lain','Lain-lain')]
		jenis_kelamins = [('laki_laki','Laki-Laki'),('perempuan','Perempuan')]
		agamas = [('islam','Islam'),('kristen','Kristen'),('hindu','Hindu'),('budha','Budha'),('kepercayaan','Kepercayaan')]

		return http.request.render('vit_universities_web.registration',
			{
			'target_title'	: 'Registration', 
			'prodi_ids'		: prodi_ids,
			'tahun_ids'		: tahun_ids,
			'semester_ids'	: semester_ids,
			'pekerjaans'	: pekerjaans,
			'jenis_kelamins'	: jenis_kelamins,
			'agamas'		: agamas,
			'message_error'	: message_error,
			'message_success': message_success
		} )	



	######################################################################################
	# proses registration patient: 
	# print, email, save: insert transaksi spmb
	######################################################################################
	@http.route('/spmb/registration_process', auth='public', website=True)
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
		email_template = email_template_obj.search([('name','=','spmb_email')])

		if not member_plan:
			message = "Member Plan not found! Please try again."
			return request.redirect('/spmb/registration?message_error=%s'% (message), code=301)

		Claim  = http.request.env['netpro.spmb']
		spmb_data = {}

		if kw.get('confirm') == '':
			##############################################################################
			# insert into netpro_spmb
			##############################################################################

			spmb_details = [(0,0,{'benefit_id' : x.benefit_id.id}) for x in member_plan.member_plan_detail_ids]

			data = {
				'spmb_date'		: time.strftime("%Y-%m-%d"),
				'member_id'			: int(member_id),
				'policy_id'			: int(policy_id.id),
				'member_plan_id'	: member_plan.id ,
				'spmb_detail_ids'  : spmb_details,
				'state'  			: "open",
			}
			spmb_data = Claim.create(data)
			message = "Claim Registration Success!"
		
		if kw.get('email') == '':
			if member_data.email:
				spmb_data = Claim.browse(int(kw.get('spmb_id')))
				
				subject_email = ''
				body_email = ''

				if email_template:
					subject_email = self.replaceString(email_template.subject, spmb_data, member_plan)
					body_email = self.replaceString(email_template.body, spmb_data, member_plan)
					
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

		#return request.redirect('/spmb/registration?message_success=%s'% (message), code=301)
		return http.request.render('vit_universities_web.loa', {
			'member'		: member_data, 
			'member_plan'	: member_plan,
			'spmb'			: spmb_data,
			'message'		: message
		})


	# # # # # # # # # # # # # # # # # # # # # 
	# 		REPLACE EMAIL GLOSSARY 			#
	# # # # # # # # # # # # # # # # # # # # # 
	def replaceString(self,content,spmb,plan):
		ret = ''
		benefits = ''
		for pl in plan.member_plan_detail_ids:
			benefits += pl.benefit_id.name + '			: '+ '{0:,.2f}'.format(int(pl.remaining)) + '\n'

		if content.find('[spmb_no]'):
			ret += content.replace('[spmb_no]', spmb.spmb_no)
		if content.find('[benefit]'):
			ret += content.replace('[benefit]', str(benefits))
		if content.find('[member_name]'):
			ret += content.replace('[member_name]', spmb.member_id.name)
		return content


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
	# action ke spmb list
	######################################################################################
	@http.route('/spmb/spmb_list', auth='user', website=True)
	def spmb_list(self, **kw):
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
				return request.redirect('/spmb/search?message_error=%s'% (message), code=301)

			##############################################################################
			# cari data spmb member tsb yang masih open
			##############################################################################
			Claim  = http.request.env['netpro.spmb']
			spmb_ids = Claim.search([('member_id','=',member.id) ])
			if not spmb_ids:
				message = "Claim Registration not found!"
				return request.redirect('/spmb/search?message_error=%s'% (message), code=301)

			# import pdb; pdb.set_trace()
			# spmbs = Claim.browse(spmb_ids)

			return http.request.render('vit_universities_web.spmb_list',
				{'message_error'	: message_error,
				'message_success'	: message_success,
				'spmbs' 			: spmb_ids,
				'member'			: member 
			} )	

