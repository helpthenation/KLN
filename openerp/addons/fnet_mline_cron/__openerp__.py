# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mline Leave Reset Cron',
    'version': '1.0',
    'category': 'HRMS',
    'sequence': 5,
    'summary': 'Leads, Opportunities, Activities',
    'description': """
Reset The Validity Of The Leave
""",
    'website': 'https://www.odoo.com/page/crm',
    'depends': [
        'base','hr','hr_contract',
    ],
    'data': [
        'view.xml',

    ],
    'demo': [
        
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
