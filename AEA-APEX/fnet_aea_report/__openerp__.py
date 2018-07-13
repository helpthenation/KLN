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
    'name': 'AEA REPORT',
    'version': '1.0',
    'category': 'Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base', 'account', 'report', 'fnet_aea_crm','stock'],
    'data': [
        'views/report_header.xml',
        'aea_report.xml',
        'views/report_invoice.xml',
        'views/report_check_details.xml',
        'wizard/check_details_view.xml',
        'views/report_bounce_details.xml',
        'wizard/check_bounce_view.xml',
        'wizard/dd_details_view.xml',
        'views/report_dd_details.xml',
        'views/report_invoice_printing.xml',
        'views/dispatch_report_view.xml',
        'views/report_cheque.xml',
    ],
    'test': [
    ],
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: