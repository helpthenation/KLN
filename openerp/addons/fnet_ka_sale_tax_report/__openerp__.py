# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Fnet KA Sale Tax Excel Report',
    'version': '1',
    'category': 'Sale Tax Report',
    'author': "Futurenet Technologies",
    'website': 'www.futurenet.com',
    'license': 'AGPL-3',
    'depends': [
                 'base','sale','account','excel_export'     
    ],
    'data': ['ka_sale_report_view.xml',  
    'security/ir.model.access.csv',
    ],
    'qweb': [
        
    ],
    'installable': True,
    'auto_install': False,
}
