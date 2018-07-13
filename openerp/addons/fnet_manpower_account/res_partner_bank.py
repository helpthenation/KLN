# -*- coding: utf-8 -*-
# Copyright 2009-2017 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models,fields,api,_


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    bank_bic=fields.Char('Bank Identifier Code',size=64)
    swift_code=fields.Char('Bank Swift Code')
