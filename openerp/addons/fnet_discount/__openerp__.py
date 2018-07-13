# -*- coding: utf-8 -*-
{
 'name': 'Fnet Discount',
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
 'depends': ['base','sale','account','account_accountant','fnet_aea_crm'],
 'data': [
          'sale_security.xml',
          'security/ir.model.access.csv',
          'invoice_discount/invoice_discount_view.xml',
          'sale_discount/product_view.xml',
          'sale_discount/sale_discount_view.xml',
          'sale_discount/sale_order.xml',              
          'views/res_config_view.xml',
           ],
 
 'installable': True,
 'auto_install': False,
 'application': True,
 }
