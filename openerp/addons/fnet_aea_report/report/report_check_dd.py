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
from datetime import datetime, timedelta


class dd_report_bounce(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(dd_report_bounce, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_check_details': self._get_check_details,
                #~ 'get_check_vou_total': self._get_check_vou_total,
                #~ 'get_check_chk_total': self._get_check_chk_total,
        })

    def _get_check_details(self, data):
        where_sql = []
        com = 'company_id' in data['form'] and [data['form']['company_id']] or []
        partner = 'partner_ids' in data['form'] and [data['form']['partner_ids']] or []
        district = 'district_ids' in data['form'] and [data['form']['district_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if data['form']['partner_ids']:
            if len(data['form']['partner_ids'])== 1:
                add = [0]
                data = data['form']['partner_ids']
                where_sql.append("cd.partner_id in %s" % (str(tuple(data+add))))
            else:
                where_sql.append("cd.partner_id in %s" % (str(tuple(data['form']['partner_ids']))))
        
        if district[0]:
            if len(district[0])== 1:
                add = [0]
                data = district[0]
                where_sql.append("rp.district_id in %s" % (str(tuple(data+add))))
            else:
                where_sql.append("rp.district_id in %s" % (str(tuple(district[0]))))
        if where_sql:
            where_sql = ' and '+' and '.join(where_sql)
            str(where_sql)
        else:
            where_sql=''
        self.cr.execute(" select rp.display_name as stokiest, rcd.name as town, pdc.name as chk_no, cd.date as chk_date, pdca.name as dd, pdca.issue_date as dd_date, to_char(pdca.issue_date, 'DD') as day, COALESCE(pdca.amount,0) as amount, pdca.bank_name as bank_name,pdca.branch_name as branch_name,  COALESCE(pdca.amount,0) - COALESCE(cd.amount,0) as pending, pdca.issue_date::date - cd.date::date as chk_boun_day, cd.bounce_amount as bounce_amt, rpu.display_name as srp, rpuinl.display_name as inl, cd.description as des "\
                        " from cheque_details cd "\
                        " join post_date_cheque pdc on (pdc.id = cd.cheque_id) "\
                        " join post_date_cheque pdca on (pdca.id = cd.against_id) "\
                        " join res_partner rp on (rp.id = cd.partner_id) "\
                        " join res_users ru on (ru.id = rp.user_id) "\
                        " join res_partner rpu on (rpu.id = ru.partner_id) "\
                        " join res_users ruinl on (ruinl.id = rp.inl_executive_id) "\
                        " join res_partner rpuinl on (rpuinl.id = ruinl.partner_id) "\
                        " join res_country_district rcd on (rcd.id = rp.district_id) "\
                        " join account_voucher av on (av.id = cd.voucher_id) "\
                        " where rp.customer is True "\
                        " and cd.against_id is not null "\
                        " and cd.state = 'done' "\
                        " "+ where_sql +  " "\
                        " and cd.company_id = '%s' "\
                        " and cd.date >= '%s' "\
                        " and cd.date <= '%s' " % (com[0][0],str(from_date[0]),str(to_date[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        return line_list
        
    #~ def _get_check_vou_total(self,data):
        #~ val = self._get_check_details(data)
        #~ vou_amount = 0.0
        #~ for value in val:
            #~ vou_amount += value['vou_amount']
        #~ return vou_amount
        
    #~ def _get_check_chk_total(self,data):
        #~ val = self._get_check_details(data)
        #~ chk_amount = 0.0
        #~ for value in val:
            #~ chk_amount += value['chk_amount']
        #~ return chk_amount

class wrapped_dd_bounce_details(osv.AbstractModel):
    _name = 'report.fnet_aea_report.report_dd_bounce'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_report.report_dd_bounce'
    _wrapped_report_class = dd_report_bounce

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
