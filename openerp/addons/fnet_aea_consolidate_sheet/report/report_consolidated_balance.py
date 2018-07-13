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

from openerp import api,models,fields,_
from datetime import datetime
import time
from dateutil import relativedelta




class report_consolidated_bs_balance(models.AbstractModel):
    _name = 'report.fnet_aea_consolidate_sheet.report_consolidated_balance'


    def _get_query_data(self, data, ids=None):
        print data,ids 
        print "4444444444",self.env.uid,self.env.user,self.env.user.company_id
        print "66666",self.ids
        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        print "21111111111",ids
        #~ ctx['fiscalyear'] = data['fiscalyear_id']
        #~ child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)        
        return data

    @api.model
    def render_html(self, ids,data=None):
        print "111111111111111111111111", self.env.context.get('active_model'),data,ids
        report_model = self.env['report']._get_report_from_name('fnet_aea_consolidate_sheet.report_consolidated_balance')
        docargs = {
            'doc_model':report_model.model,
            'data':data['form'],
            'get_query_data':self._get_query_data
        }
        
        render_model = 'fnet_aea_consolidate_sheet.report_consolidated_balance'
        return self.env['report'].render(render_model, docargs)

        

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
