# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#                Gabriela Quilarque <gabriela@vauxoo.com>
############################################################################

{
    "name": "Forecasting by Smoothing Techniques",
    "version": "8.0.1.0.0",
    "license": "LGPL-3",
    "author": "Vauxoo",
    "website": "http://www.vauxoo.com/",
    "category": "",
    "depends": [
        "board",  # Just because we need some graphic stuff from here
        "web_widget_x2many_graph",  # To show one2many values as graphs
        "mail",
    ],
    "data": [
        "security/forecasting_smoothing_techniques_security.xml",
        "security/ir.model.access.csv",
        "views/forecasting_smoothing_techniques_view.xml",
    ],
    "demo": [
        "demo/forecast_demo.xml",
    ],
    "external_dependencies": {
        "python": ["pandas", "numexpr"],
    },
    "test": [],
    "qweb": [],
    "installable": True,
    "application": True,
}
