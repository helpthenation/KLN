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
    'category': 'CRM',
    'sequence': 2,
    'summary': '',
    'description': """
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'depends': ['base', 'crm', 'sales_team', 'product', 'stock_account', 'stock', 'account', 'fnet_aea_crm'],
    'data': [
        #~ 'apex_sale_master_view.xml',
        'wizard/target_product_view.xml',
        #~ 'wizard/sale_target_submit.xml',
        'apex_rd_view.xml',
        'apex_pjc_master_view.xml',
        'security/internal_security.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'scheme_sequence.xml'
        
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
