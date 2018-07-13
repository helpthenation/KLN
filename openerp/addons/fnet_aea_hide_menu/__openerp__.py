# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'aea_hide_menu',
    'version' : '1.1',
    'summary': 'hide_menu',
    'sequence': 30,
    'data': ['security/internal_security.xml',
    'models/views.xml',
    'models/group_by_views.xml',
   
    ],
    'depends':['base', 'report','account','event'],

}
