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
    'name': 'GST - Tax Config',
    'version': '1.0',
    'description': """

  """,
    'author': ['Iswasu Technologies'],
    'category': 'Localization/Account Charts',
    'depends': [
        'account',
        'account_chart','l10n_in'
        
    ],
    'demo': [],
    'data': [
         'schedule6_charts.xml',
         #~ 'account_account_template.xml',
        'tax_code_template.xml',
        'standard_tax_template.xml',
        'schedule6_tax_template.xml',
        #~ 'wizard.xml',
       
    ],
    'auto_install': True,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
