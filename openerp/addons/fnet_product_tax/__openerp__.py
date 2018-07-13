# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-TODAY Serpent Consulting Services Pvt. Ltd.
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
    'name': 'Product Tax Updation',
    'author': 'Iswasu Technologies Pvt. Ltd.,',
    'category': ' ',
    'summary': '',
    'website': "http://www.futurenet.com",
    'version': '8.0.1.0.1',
    'description': 'This Module help to update customer and supplier taxes in product for selected product category',
    'depends': ['account','product','sale','purchase'],
    'data': [
        'wizard/invoice_report_wizard.xml',
        'account_invoice_view.xml'
    ],
    'installable': True,
    'auto_install': False
}
