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
import time


class enquiry_register_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(enquiry_register_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_enquiry_details':self._get_enquiry_details,
                'get_enquiry_details_line':self._get_enquiry_details_line,
        })

	def _get_date1(self,data,val):
		if val:
			a=datetime.strptime(val, '%Y-%m-%d %H:%M:%S').date()
			return a
			
	
    def _get_date(self, data):
        val = []
        res = {}
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        now = time.strftime("%Y-%m-%d")
        res['from_date']=from_date
        res['to_date']=to_date
        res['now']=now
        val.append(res)
        print val, "DDDDDDDd"
        return val
        
    def _get_enquiry_details(self, data):
        where_sql=[]
        partner_sql=[]
        sale_sql=[]
        state_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        partner='partner_ids' in data['form'] and [data['form']['partner_ids']] or []
        user='sales_person_ids' in data['form'] and [data['form']['sales_person_ids']] or []
        state='state' in data['form'] and [data['form']['state']] or []
        print state,'##################################'
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("cr.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("cr.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '.join(where_sql) + ' and'
        else:
            where_sql=''
        if from_date and to_date:
            from_date_sql.append("cr.date >= '%s'" % (str(from_date[0])))     
            to_date_sql.append("cr.date <= '%s'" % (str(to_date[0])))  
        if from_date_sql or  to_date_sql:
            from_date_sql = ' and '.join(from_date_sql) + ' and'
            to_date_sql = ' and '.join(to_date_sql)
        else:
            from_date_sql=''
            to_date_sql='' 
        if partner[0]:
            if len(partner)== 1:
                add = [0]
                data = partner[0]
                partner_sql.append("cr.partner_id in %s" % (str(tuple(data+add))))
            else:
                partner_sql.append("cr.partner_id in %s" % (str(tuple(partner[0]))))
        
        if partner_sql:
            partner_sql = ' and '.join(partner_sql) + ' and'
            str(partner_sql)
        else:
            partner_sql=''

        if user[0]:
            if len(user)== 1:
                add = [0]
                data = user[0]
                sale_sql.append("cr.user_id in %s" % (str(tuple(data+add))))
            else:
                sale_sql.append("cr.user_id in %s" % (str(tuple(user[0]))))
        
        if sale_sql:
            sale_sql = ' and '.join(sale_sql) + ' and'
            str(sale_sql)
        else:
            sale_sql=''            
            
        if state[0]:
            add = [0]
            data = state[0][0]
            state_sql.append("cr.stage_id = %s" % (str(data)))            
        if state_sql:
            state_sql = ' and '.join(state_sql)  +' and'
            str(state_sql)
        else:
            state_sql=''                        
        print where_sql, sale_sql, partner_sql, state_sql,'%%%%%%%%%%%%%%%%%%%%%%%%5555'   
        self.cr.execute(" select cr.id,cr.date, cr.seq_no, cr.name as subject, cr.client_order_ref,rp.name as partner,"\
                        " date(cr.submission_date) as submission_date,ccs.name as state, rpp.name as user from crm_lead cr "\
                        " join res_partner rp on (rp.id = cr.partner_id)"\
                        " join res_users ru on (ru.id = cr.user_id)"\
                        " join res_partner rpp on (rpp.id = ru.partner_id)"\
                        " join crm_case_stage ccs on (ccs.id = cr.stage_id)"\
                        " where "+ where_sql +  " "\
                        " "+ partner_sql +  " "\
                        " "+ sale_sql +  " "\
                        " "+ state_sql +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
                           
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
        
    def _get_enquiry_details_line(self,data,enquiry_id):
        where_sql=[]
        partner_sql=[]
        sale_sql=[]
        state_sql=[]
        from_date_sql=[]
        to_date_sql=[]
        enquiry_sql=[]
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        partner='partner_ids' in data['form'] and [data['form']['partner_ids']] or []
        user='sales_person_ids' in data['form'] and [data['form']['sales_person_ids']] or []
        state='state' in data['form'] and [data['form']['state']] or []
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("cr.company_id=%s" % (str(data['form']['company_ids'][0])))
            else:
                where_sql.append("cr.company_id in %s" % (str(tuple(data['form']['company_ids']))))
        if where_sql:
            where_sql = ' and '.join(where_sql) + ' and'
        else:
            where_sql=''
        if from_date and to_date:
            from_date_sql.append("cr.date >= '%s'" % (str(from_date[0])))     
            to_date_sql.append("cr.date <= '%s'" % (str(to_date[0])))  
        if from_date_sql or  to_date_sql:
            from_date_sql = ' and '.join(from_date_sql) + ' and'
            to_date_sql = ' and '.join(to_date_sql)
        else:
            from_date_sql=''
            to_date_sql='' 
        if enquiry_id:
            enquiry_sql.append("cr.id = '%s'" % (str(enquiry_id)))      
        if enquiry_sql:
            enquiry_sql = ' and '.join(enquiry_sql) + ' and'
        else:
            enquiry_sql=''            
        if partner[0]:
            if len(partner)== 1:
                add = [0]
                data = partner[0]
                partner_sql.append("cr.partner_id in %s" % (str(tuple(data+add))))
            else:
                partner_sql.append("cr.partner_id in %s" % (str(tuple(partner[0]))))
        
        if partner_sql:
            partner_sql = ' and '.join(partner_sql) + ' and'
            str(partner_sql)
        else:
            partner_sql=''

        if user[0]:
            if len(user)== 1:
                add = [0]
                data = user[0]
                sale_sql.append("cr.user_id in %s" % (str(tuple(data+add))))
            else:
                sale_sql.append("cr.user_id in %s" % (str(tuple(user[0]))))
        
        if sale_sql:
            sale_sql = ' and '.join(sale_sql) + ' and'
            str(sale_sql)
        else:
            sale_sql=''            
            
        if state[0]:
            add = [0]
            print state[0]
            data = state[0][0]
            state_sql.append("cr.stage_id = %s" % (str(data)))            
        if state_sql:
            state_sql = ' and '.join(state_sql)  +' and'
            str(state_sql)
        else:
            state_sql=''                        
        print where_sql, sale_sql, partner_sql, state_sql,'%%%%%%%%%%%%%%%%%%%%%%%%5555'   
        self.cr.execute(" select cr.id,cpl.reference as advanced, pt.name as product, cll.description,"\
                        " cll.part_no,cll.make_no,cll.quantity, pu.name  as uom from crm_lead cr "\
                        " join crm_lead_line cll on (cll.crm_lead_id=cr.id)"\
                        " join cutomer_product_line cpl on (cpl.id=cll.advanced)"\
                        " join product_product pp on (pp.id=cll.product_id) "\
                        " join product_template pt on (pt.id=pp.product_tmpl_id)"\
                        " join product_uom pu on (pu.id=cll.uom_id)"\
                        " where "+ where_sql +  " "\
                        " "+ partner_sql +  " "\
                        " "+ enquiry_sql +  " "\
                        " "+ sale_sql +  " "\
                        " "+ state_sql +  " "\
                        " "+ from_date_sql +  " "\
                        " "+ to_date_sql +  " ")
		
        line_list = [i for i in self.cr.dictfetchall()]
        print line_list
        return line_list        

class wrapped_enquiry_register_summary(osv.AbstractModel):
    _name = 'report.fnet_mline_sale_report.report_enquiry_register'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_sale_report.report_enquiry_register'
    _wrapped_report_class = enquiry_register_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
