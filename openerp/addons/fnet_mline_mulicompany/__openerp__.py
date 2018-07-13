# -*- coding: utf-8 -*-
{
    'name': "Enquiry Based On Company",

    'summary': """
                      This Module will limit the Enquiry for current login company
                      """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Futurenet",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','fnet_mline_crm_inherit',
        'crm',
        ],

    # always loaded
    'data': [
        #~ 'security/ir.model.access.csv',
        'multicompany_rules.xml',
        'view.xml',    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
