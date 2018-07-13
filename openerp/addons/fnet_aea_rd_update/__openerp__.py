
{
    'name' : 'RD Product Update',
    'version' : '0.1',
    'author' : 'Futurenet',
    'category' : 'Sales',
    'description' : """

    """,

    'depends' : ['fnet_aea_sale','sale'],
    'data': [
        'security/ir_rule.xml',  
        'security/ir.model.access.csv',    
        'views.xml',   

    ],

    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
