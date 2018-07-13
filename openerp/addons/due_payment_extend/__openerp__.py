# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2014-2016 Openies Services(<http://openies.com>).
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
    "name" : "Due Payment Report",
    "version" : "1.0",
    "author" : "Openies Services",
    'website' : 'http://Openies.com',
    "category" : "Account",
    "summary": 'Removes No Followup Lines from Due Payment Report',
    "description": """
Openies Account Overdue Extend
========================================
    A Overdue report Extension
    Module will restrict the lines in the report which has marked no follow up
    
""",
    "license" : "AGPL-3",
    "depends" : ['account_followup'],
    "data" : ['views/report_overdue_payment.xml'],
    "demo" : [],
    'auto_install': False,
    "installable": True,
    'images': ['static/description/openies_due_payment_extend.png'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
