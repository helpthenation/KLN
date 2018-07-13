# -*- coding: utf-8 -*-
{
 'name': 'Rounding Invoice Amount',
 'version': '1.0',
 'category': 'Invoice',
 'sequence': 6,
 'icon': "/fnet_crm/static/img/icon.png",
 'description': """
Rounded Invoice 
==========================================
Accounting->Configuration->settings Here is the rounding method field
  => if you select Rounding Total Amount option in rounding method field
  ->then add the rounding account in Tax rounding account field    

""",
 'author': "Futurenet",
 'website': 'http://www.futurenet.in/',
 'depends': ['account','account_accountant'],
 'data': [
          'views/account_invoice_view.xml',
          #~ 'views/res_config_view.xml',
           ],
 
 'installable': True,
 'auto_install': False,
 'application': True,
 }
