#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'MULTILINE REPORT',
    'version': '1.0',
    'category': 'Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
                Sale Quote Report,
                Sale Order Report,
                Purchase Quote Report
                Purchase Order Report
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base','base_setup', 'sale','website','report','fnet_mline_crm_inherit','purchase',],
    "images":['img/cash_invoice.jpg',],
    'data': [
        'multiline_report.xml',
        'views/header.xml',
        'views/header_bulluff.xml',
        'views/footer.xml',
        'views/report_sale_quote.xml',
        'views/report_purchase_quote.xml',
        'views/report_purchase_order.xml',
        'views/report_tech_quote.xml',
        'views/report_covering.xml',
        'views/report_invoice.xml',
        #~ 'views/report_delivery_note.xml',
        'views/report_grn.xml',
        'views/delivery_note_format.xml',
        'views/report_proforma_invoice.xml',
        'views/proforma_invoice_format.xml',
        'views/report_po_buluff.xml',
        'views/report_po_quote_buluff.xml',
        'views/report_costing.xml',
        'views/report_so_quote_buluff.xml',
        'views/baluff_invoice.xml',
        'views/report_bank_voucher.xml',
        'views/report_bank_voucher_reciept.xml',
        'views/report_reciept_voucher.xml',
        'views/credit_memo.xml',
        'views/report_check.xml',
        'views/report_det.xml',
        'views/header_invoice.xml',
        'views/header_invoice_cash.xml',
        'views/invoice_footer.xml',
        'views/invoice_footer_cash.xml',
        'views/delivery_footer.xml',
        'views/delivery_header.xml',
        'views/grn_header.xml',
        'views/grn_footer.xml',
        'views/layout.xml',
        'partner_view.xml',
        'sale_view.xml',
        'purchase_view.xml',
        'stock_view.xml',
        'res_partner_bank_view.xml',
       
    ],
    'test': [
    ],
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
