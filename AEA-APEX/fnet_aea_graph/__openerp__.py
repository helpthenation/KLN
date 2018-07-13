# -*- coding: utf-8 -*-
{
    'name': "Fnet Sale Entry Pivot View",

    'version': '1.0',
    'sequence': 2,
    'summary': 'Associated Electrical Agencies',
    'description': """
             This Module Add Sale Entry Analysis Menu Under Reporting-->Sale,which is used analysis sale entry details in pivoted view
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',

    # any module necessary for this one to work correctly
    'depends': ['base','crm','sale','fnet_aea_sale'],

    # always loaded
    'data': [
      'sale_entry_report.xml',
      'security/internal_security.xml',
      'security/ir.model.access.csv',
    ],


}
