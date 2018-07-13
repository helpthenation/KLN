# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

import time
from lxml import etree

from openerp.osv import fields, osv
from openerp.osv.orm import setup_modifiers
from openerp.tools.translate import _

class consolidated_balance_report(osv.osv_memory):
    _name = "consolidated.balance.report"
    _description = "Account Common Report"

    
    _columns = {
        'date_from': fields.date("Start Date"),
        'date_to': fields.date("End Date"),
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', help='Keep empty for all open fiscal year'),

        }


    def _print_report(self, cr, uid, ids, data, context=None):
        context = context or {}       
        print data
        return self.pool['report'].get_action(cr, uid, ids, 'fnet_aea_consolidate_sheet.report_consolidated_balance', data=data, context=context)

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        print "555555555555",uid,ids,self.read(cr, uid, ids, ['date_from',  'date_to','fiscalyear_id'], context=context)[0],self.read(cr, uid, ids, ['date_from',  'date_to','fiscalyear_id'], context=context)
        #~ print self.ids
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to','fiscalyear_id'], context=context)[0]

        #~ data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
