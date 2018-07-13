# -*- coding: utf-8 -*-
{
    'name': "Fnet Mline Reminder",
    'summary': """Enquiry Remainder""",
    'description': """Cron JOB To Send Mail For Enquiry Remainder""",
    'author': "Futurenet",
    'website': "http://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','crm','fnet_mline_crm_inherit','report','mail'],    
    'data': ['security/ir.model.access.csv',
             'report_enquiry_view.xml',
             'report_enquiry_tomarrow.xml',
             'enquiry_remainder_cron.xml',
             'enquiry_remainder_view.xml'],
}
