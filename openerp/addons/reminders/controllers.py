# -*- coding: utf-8 -*-
from openerp import http

# class Reminders(http.Controller):
#     @http.route('/reminders/reminders/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/reminders/reminders/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('reminders.listing', {
#             'root': '/reminders/reminders',
#             'objects': http.request.env['reminders.reminders'].search([]),
#         })

#     @http.route('/reminders/reminders/objects/<model("reminders.reminders"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('reminders.object', {
#             'object': obj
#         })