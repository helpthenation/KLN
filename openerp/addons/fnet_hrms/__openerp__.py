#-*- coding:utf-8 -*-


{
    'name': 'Additional Details HRMS',
    'version': '1.1',
    'category': 'Human Resources',
    'description': """
		1.This is used for add some detail about employee.
		2.This module fully depends on hr module 
    """,
    'author':'Futurenet',
    'website':'http://oneclick.software',
    'depends': [
        'hr','hr_payroll'
            ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_details_view.xml',
        #~ 'hr_details_sequence.xml',
        #~ 'res_partner.xml',
        'view.xml',
        #~ 'hr_employee_views.xml',
        #~ 'security/ir.model.access.csv',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
