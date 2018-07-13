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

from openerp import api, models
from openerp.osv import osv
from openerp import api,_
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import datetime
from datetime import timedelta

class ParticularReport(models.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_purchasequote' 
            
    def get_date(self,val):
        if val.lead_id:
            if val.lead_id.submission_date:
                rec=datetime.strptime(val.lead_id.submission_date, "%Y-%m-%d %H:%M:%S").date()
                value=rec.strftime('%Y-%m-%d')
                new_date=(datetime.strptime(value, '%Y-%m-%d') - timedelta(days = 2)).date()
                return new_date.strftime('%d/%m/%Y')
            else:
                return False
            return False
            
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_purchasequote')
        po_obj=self.env['purchase.order'].browse(self.ids)
        #~ sale_order=self.env['sale.order'].search([('name','=',stock_pick.origin)])
        for order in po_obj.browse(self.ids):
            if order.state == 'draft':
                raise osv.except_osv(_("Warning!"), _("Kindly Confrim The RFQ Before Printing The Report...!! "))
            docargs = {
                'doc_ids': po_obj,
                #~ 'sale':sale_order,
                'doc_model': report.model,
                'docs': self,
            }
            
            return report_obj.render('fnet_mline_reportz.report_purchasequote', docargs)            


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
