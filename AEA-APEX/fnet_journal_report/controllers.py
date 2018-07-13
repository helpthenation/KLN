# -*- coding: utf-8 -*-
from openerp import http

# class FnetJournalReport(http.Controller):
#     @http.route('/fnet_journal_report/fnet_journal_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fnet_journal_report/fnet_journal_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fnet_journal_report.listing', {
#             'root': '/fnet_journal_report/fnet_journal_report',
#             'objects': http.request.env['fnet_journal_report.fnet_journal_report'].search([]),
#         })

#     @http.route('/fnet_journal_report/fnet_journal_report/objects/<model("fnet_journal_report.fnet_journal_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fnet_journal_report.object', {
#             'object': obj
#         })