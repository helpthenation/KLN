# -*- coding: utf-8 -*-
{
    'name': "Fnet Update Sale Team Details",

    'version': '1.0',
    'category': 'Update Details',
    'sequence': 2,
    'summary': """This module add a menu under More button in Account Invoice,named Update Details, Which will update Sale Representative and Sale Team Details For the Selected Invoices based on customer details""",
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','account'],

    # always loaded
    'data': [
        'wizard/update_details.xml',
        'security/ir.model.access.csv',
    ],


}
