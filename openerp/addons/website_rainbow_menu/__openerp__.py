# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015-TODAY Odoo S.A. <http://www.odoo.com>
#    @author Paramjit Singh A. Sahota <sahotaparamjitsingh@gmail.com>
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
    'name': 'Rainbow Menu',
    'version': '8.0.1.0.0',
    'author': 'Paramjit Singh A. Sahota',
    'website': 'www.sahotaparamjitsingh.blogspot.com',
    'category': 'Website',
    'depends': ['website'],
    'description': """
Website Rainbow Menu
============================
After installing this module the menus in website
will have different colors underline.

The selected menu will have different color underline
and on hovering the menus will also show you different colors underlines
which will gives your website more different look.
    """,
    'data': [
        'views/website_rainbow_menu.xml',
    ],
    'demo': [],
    'installable': True,
}
