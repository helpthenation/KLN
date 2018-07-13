# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'AEA CRM',
    'version': '1.0',
    'category': 'Sale',
    'sequence': 2,
    'summary': '',
    'description': """
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base', 'sale', 'account', 'account_voucher', 'account_check_writing', 'fnet_aea_crm', 'delivery', 'purchase'],
    'data': [
        'sale_view.xml',
        'invoice_view.xml',
        #~ 'account_dd_map_view.xml',
        'account_voucher_view.xml',
        'security/internal_security.xml',
        'security/ir.model.access.csv',
        'views/voucher_check.xml',
        'invoice_sequence.xml',
        'stock_view.xml',
        'purchase_view.xml',
        'report/aged_partner_view.xml',
        'views/aged_partner_balance.xml',
            ],
    'demo': [
       
            ],
    'test': [
       
            ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
