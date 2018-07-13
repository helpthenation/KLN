# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "MLINE LEAVE",
    "summary": "Compute worked days from attendance",
    "version": "8.0.1.0.1",
    "category": "Human Resources",
    "website": "https://opensynergy-indonesia.com",
    "author": "OpenSynergy Indonesia",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr",
        "hr_holidays",
        "hr_contract",
    ],
    "data": [
        "views/hr_payslip_view.xml",
    ],
}
