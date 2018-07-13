# -*- coding: utf-8 -*-
{
    'name': "fnet_aea_rdclaim",

    'version': '1.0',
    'category': 'RD Claim Report Management',
    'sequence': 2,
    'summary': 'Report Creation',
    'description': """
             Associated Electrical Agencies
                   """,
    'author': 'Futurenet',
    'website': 'http://www.futurenet.in/',

    # any module necessary for this one to work correctly
    'depends': ['base','report_xls','report_xlsx','report_webkit','fnet_aea_sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/financial_webkit_header.xml',
        'data/custom_webkit_header.xml',
        'report/report_rdsale_entries.xml',
        'report/report.xml',
        'wizard/rdclaim_wizard.xml',
        'wizard/rdclaim_sales_achievement.xml',
        'wizard/rd_sale_entry.xml',
    ],


}
