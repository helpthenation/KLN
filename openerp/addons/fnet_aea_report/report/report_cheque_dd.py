#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.report import report_sxw
import math
from openerp.tools.amount_to_text_en import amount_to_text

class che_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(che_report, self).__init__(cr, uid, name, context=context)
        ids = context.get('active_ids')
        inv_obj = self.pool['cheque.details']
        inv_br_obj = inv_obj.browse(cr, uid, ids, context=context)
        self.localcontext.update({
             'get_amd2text': self._get_amd2text,
             'get_com': self._get_com,
        })
        self.context = context

   

    def _amount_to_text(self, amount, currency):
        cur = self.pool['res.currency'].browse(self.cr, self.uid, currency, context=self.context)
        if cur.name.upper() == 'EUR':
            currency_name = 'Euro'
        elif cur.name.upper() == 'USD':
            currency_name = 'Dollars'
        elif cur.name.upper() == 'INR':
            currency_name = 'Rupees'
        elif cur.name.upper() == 'BRL':
            currency_name = 'reais'
        else:
            currency_name = cur.name
        #TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
        #amount_in_word = amount_to_text(amount, context=context)
        return amount_to_text(amount, currency=currency_name)
    
    def _get_amd2text(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        tot = inv_br_obj.amount_total
        res = self._amount_to_text(tot, inv_br_obj.currency_id.id)
        return res
        
    def _get_com(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        na = inv_br_obj.company_id.name
        if na[0:3] == 'AEA':
            na = 'Associated Electrical Agencies'
        else:
            na = 'Apex Agencies'
        return na
        
   
        
class wrapped_che_report(osv.AbstractModel):
    _name = 'report.fnet_aea_report.report_cheque'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_report.report_cheque'
    _wrapped_report_class = che_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
