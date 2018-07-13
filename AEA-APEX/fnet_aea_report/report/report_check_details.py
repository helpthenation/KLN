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
from  amt_to_txt  import Number2Words
import locale

class check_report_details(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(check_report_details, self).__init__(cr, uid, name, context)
        ids = context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(cr, uid, ids, context=context)
        self.localcontext.update({
                'get_check_details': self._get_check_details,
                'get_com1': self._get_com1,
                'Number2_Words':self.Number2Words,
                #~ 'set_to_comma1':self.set_to_comma,
        })
        self.context = context

    def _get_check_details(self, data):
        com = 'company_id' in data['form'] and [data['form']['company_id']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        chk_type = 'chk_type' in data['form'] and [data['form']['chk_type']] or []
        state = 'state' in data['form'] and [data['form']['state']] or []
        if chk_type[0] == 'all':   
            self.cr.execute("""select 
                                          to_char(cd.date,'DD-MM-YYYY') as date,
                                          cd.type as type,
                                          pdc.name as chk_no,
                                          rp.display_name,
                                          cd.amount
                                    from cheque_details cd
                                    join post_date_cheque pdc on (pdc.id = cd.cheque_id)
                                    join res_partner rp on (rp.id = cd.partner_id) 
                                    where rp.customer is True and cd.type = 'cheque' and cd.state = '%s' and cd.date = '%s' and cd.company_id = '%s' and pdc.chk_type <> 'all'
                                    order by 1 """ % (state[0],from_date[0], com[0][0]))
            line_list = [i for i in self.cr.dictfetchall()]
            return line_list
        else:
            self.cr.execute("""select 
                                          to_char(cd.date,'DD-MM-YYYY') as date,
                                          cd.type as type,
                                          pdc.name as chk_no,
                                          rp.display_name,
                                          cd.amount
                                    from cheque_details cd
                                    join post_date_cheque pdc on (pdc.id = cd.cheque_id)
                                    join res_partner rp on (rp.id = cd.partner_id) 
                                    where rp.customer is True and cd.type = 'cheque' and cd.state = '%s' and cd.date = '%s' and cd.company_id = '%s' and pdc.chk_type = '%s'
                                    order by 1 """ % (state[0],from_date[0], com[0][0], chk_type[0]))
            line_list = [i for i in self.cr.dictfetchall()]
            return line_list
            
    def _get_com1(self,data):
        com = 'company_id' in data['form'] and [data['form']['company_id']] or []
        inv_br_obj = self.pool.get('res.company').browse(self.cr, self.uid, com[0])
        for i in inv_br_obj:
         na = i.name
         if na[0:3] == 'AEA':
            na = 'Associated Electrical Agencies'
         else:
            na = 'Apex Agencies'
         return na
         
    #~ def _get_com1(self):
        #~ ids = self.context.get('active_ids')
        #~ inv_obj = self.pool['account.invoice']
        #~ inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        #~ na = inv_br_obj.company_id.name
        #~ if na[0:3] == 'AEA':
            #~ na = 'Associated Electrical Agencies'
        #~ else:
            #~ na = 'Apex Agencies'
        #~ return na
     
    def Number2Words(self,data,join=True):
        wGenerator = Number2Words()
        return wGenerator.convertNumberToWords(data)
        
    #~ def set_to_comma(self,data):
        #~ print "HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH",type(data)
        #~ locale.setlocale(locale.LC_ALL, ' ')
        #~ a= locale.currency(data,grouping=True)
        #~ print "SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS",a
        #~ t=a.split('')
        #~ return t[1]
        

class wrapped_check_report_details(osv.AbstractModel):
    _name = 'report.fnet_aea_report.report_bank_details'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_report.report_bank_details'
    _wrapped_report_class = check_report_details

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
