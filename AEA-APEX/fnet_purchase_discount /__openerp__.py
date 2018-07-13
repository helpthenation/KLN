# -*- coding: utf-8 -*-
{
 'name': 'Fnet Purchase Discount',
 'version': '1.0',
 'category': 'Purchase',
 'sequence': 6,
 'icon': "/fnet_crm/static/img/icon.png",
 'description': """
Purchase Discount 
==========================================

""",
 'author': "Futurenet",
 'website': 'http://www.futurenet.in/',
 'depends': ['base','purchase','account','account_accountant'],
 'data': [
          'models/product_view.xml',
          'models/purchase_order.xml',
          'models/invoice_view.xml',
          'models/res_config_view.xml',
           ],
 
 'installable': True,
 'auto_install': False,
 'application': True,
 }
