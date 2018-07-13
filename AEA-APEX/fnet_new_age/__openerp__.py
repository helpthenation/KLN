# -*- coding: utf-8 -*-
{
    'name': "Fnet New Aged Partner",

    'category': 'Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','report'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'report/layouts.xml',
        'wizard/fnet_aged_partner.xml',
        'report/report.xml',
        'report/report_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
