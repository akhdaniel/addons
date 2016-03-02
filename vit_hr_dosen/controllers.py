# -*- coding: utf-8 -*-
from openerp import http

# class VitHrDosen(http.Controller):
#     @http.route('/vit_hr_dosen/vit_hr_dosen/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/vit_hr_dosen/vit_hr_dosen/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('vit_hr_dosen.listing', {
#             'root': '/vit_hr_dosen/vit_hr_dosen',
#             'objects': http.request.env['vit_hr_dosen.vit_hr_dosen'].search([]),
#         })

#     @http.route('/vit_hr_dosen/vit_hr_dosen/objects/<model("vit_hr_dosen.vit_hr_dosen"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('vit_hr_dosen.object', {
#             'object': obj
#         })