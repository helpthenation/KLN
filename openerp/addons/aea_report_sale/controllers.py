# -*- coding: utf-8 -*-
from openerp import http

# class AeaReportSale(http.Controller):
#     @http.route('/aea_report_sale/aea_report_sale/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/aea_report_sale/aea_report_sale/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('aea_report_sale.listing', {
#             'root': '/aea_report_sale/aea_report_sale',
#             'objects': http.request.env['aea_report_sale.aea_report_sale'].search([]),
#         })

#     @http.route('/aea_report_sale/aea_report_sale/objects/<model("aea_report_sale.aea_report_sale"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('aea_report_sale.object', {
#             'object': obj
#         })