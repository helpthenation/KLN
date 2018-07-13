# -*- coding: utf-8 -*-
{
    'name': "Fnet Sale Representative Update",

    'version': '1.0',
    'category': 'Update Details',
    'sequence': 2,
    'summary': """This module add a menu under More button in Sale Entry,Which will update Sale Representative  For the Selected Record based on customer details""",
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','account','fnet_aea_sale',],

    # always loaded
    'data': [
        'wizard/update_details.xml',
        'security/ir.model.access.csv',
    ],


}
