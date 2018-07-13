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
    'name': 'Mline Vat Invoice',
    'version': '1.0',
    'category': 'Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
             Mline
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base', 'account', 'report','product','fnet_mline_vat_field','fnet_manpower_account',],
    'data': [
        'report.xml',
        'views/report_invoices.xml',
        'views/report_meps_invoices.xml',
    ],
    'test': [
    ],
    'demo': [ ],
    'installable': True,
    'auto_install': False,
    'application': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
