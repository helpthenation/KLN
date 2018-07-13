# -*- coding: utf-8 -*-
{
    'name': "Fnet Product PriceList Update",

    'version': '1.0',
    'category': 'Update Details',
    'sequence': 2,
    'summary': """Fnet Product PriceList Update""",
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/multicompany_rules.xml',
        'view.xml',        
    ],


}
