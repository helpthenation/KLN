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
    'name': 'Mline SALE REPORT',
    'version': '1.0',
    'category': 'Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
             Multiline 
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base','report', 'sale','purchase'],
    'data': [
        'views/header.xml',
        'aea_sale_report.xml',
        'wizard/sale_register_view.xml',
        'views/report_sale_register.xml',
        'wizard/sale_return_view.xml',
        'views/report_sale_return.xml',
        'wizard/purchase_register_view.xml',
        'views/report_purchase_register.xml',
        'wizard/stock_ledger_view.xml',
        'views/report_stock_ledger.xml',
        'wizard/purchase_register_view_consolidate.xml',
        'views/report_purchase_register_consolidate.xml',
        'wizard/sale_register_view_consolidate.xml',
        'views/report_sale_register_consolidate.xml',
        'wizard/party_wise_sale_summary.xml',
        'views/report_party_wise_sale_summary.xml',
        'wizard/sale_summary.xml',
        'views/report_sale_summary.xml',
        'wizard/sale_summary_month_wise.xml',
        'views/report_sale_summary_month_wise.xml',
        #~ 'wizard/salary_register.xml',
        #~ 'views/report_salary_register.xml',
        'wizard/sale_register_view_prod.xml',
        'views/report_sale_register_prod.xml',
        'wizard/sale_return_prod_view.xml',
        'views/report_sale_return_prod.xml',
        'wizard/enquiry_register_view.xml',
        #~ 'views/report_job_costing.xml',
        #~ 'wizard/job_costing_view.xml',
        'views/report_enquiry_register.xml', 
        'wizard/sale_register_pending_view.xml',
        'views/report_sale_register_pending.xml', 
        'wizard/po_return_view.xml',
        'views/report_po_return.xml',   
        'wizard/pending_purchase_register_view.xml',
        'views/report_purchase_register_pending.xml',        
            
    ],
    'test': [
    ],
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
