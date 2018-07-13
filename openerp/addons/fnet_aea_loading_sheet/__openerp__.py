# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'aea_loading_sheet',
    'version' : '1.1',
    'summary': 'loading_sheet',
    'sequence': 30,
    'data': [
    'wizard/loading_sheet_wizard_view.xml',
    'reports/tpt_report.xml',
   
    ],
    'depends':['base', 'report','account','event'],

}
