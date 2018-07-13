
{
    'name' : 'Multiline Loan Management',
    'version' : '0.1',
    'author' : 'Futurenet',
    'category' : 'Human Resources',
    'description' : """

    """,

    'depends' : ['hr', 'account','hr_contract','fnet_mline_payroll'],
    'data': [
        'sequences/hr_loan_sequence.xml',
        #~ 'datas/hr_payroll_data.xml',
        'security/ir.model.access.csv',    
        'security/ir_rule.xml',         
        'views/hr_loan_view.xml',
        'views/hr_contract_view.xml',
        #'views/board_hr_loan_statistical_view.xml',
    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
