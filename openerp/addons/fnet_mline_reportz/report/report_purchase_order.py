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


class purchase_order_report1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(purchase_order_report1, self).__init__(cr, uid, name, context)
        ids = context.get('active_ids')
        self.localcontext.update({
            'get_int': self._get_int,
            'get_job': self._get_job,
        })

    def _get_job(self,val):
        s=' '
        self.cr.execute("""
                    SELECT distinct aaa.name
                    FROM purchase_order_line pol
                    JOIN account_analytic_account aaa ON pol.account_analytic_id = aaa.id 
                    JOIN purchase_order po ON pol.order_id = po.id
                    WHERE po.id = %d"""%(val.id))
        q=self.cr.fetchall()
        if len(q) >= 1:
            for i in range(len(q)):         
                 s+=str(q[i][0])+ ", "  
            s1=s.rindex(',')      
            s2=s[:s1] +' '  
            return s2
        else:
            return None            
                
    def _get_int(self,obj):
        if obj:
            return int(obj)
         

class wrapped_report_purchaseorder(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_purchaseorder'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_reportz.report_purchaseorder'
    _wrapped_report_class = purchase_order_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
