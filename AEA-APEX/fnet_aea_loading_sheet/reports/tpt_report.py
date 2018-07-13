from openerp import api,models,fields,_
from datetime import datetime
import time
from dateutil import relativedelta


class student_report(models.AbstractModel):
    _inherit="account.invoice"
    _name="report.fnet_aea_loading_sheet.report_tpt"
    
   
    
    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        print"cccccccccccccccccccccccc",data
        tpt_report = Report._get_report_from_name('fnet_aea_loading_sheet.report_tpt')
        context = dict(self._context or {})
        obj = self.env['loading.sheet.wizard'].browse(docids)
        docargs = {'doc_ids': self.ids,
            'doc_model': tpt_report.model,
            'docs': obj,
            'data': data, 
            'header_lines':self._get_header_lines,
                      }
        return Report.render('fnet_aea_loading_sheet.report_tpt', docargs)
    
    def _get_header_lines(self,o):
        print "ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg",o.invoice_ids
        lines=[]
        for rec in o.invoice_ids:
            obj=self.env.cr.execute('''select distinct on (product_id)  pp.default_code as name, pp.id as product_id from account_invoice_line ail
                                        join product_product pp on (pp.id = ail.product_id) 
                                        join product_template pt on (pt.id = pp.product_tmpl_id) 
                                        where ail.invoice_id = %d '''%(rec.id))
            result=self.env.cr.dictfetchall()
            #~ print "sdghfakhgasjgkdsfkjhdgjhgfjhghjdsgfjhdsgfjhsdgfhjdgfdshjgfhgsdghfadshgfsdghfagjsh",result    
            
            for i in result:
                name_split=""
                for rec in i['name']:
                    name_split+=rec+'<br/>'
                i.update({'name':name_split})    
                lines.append(i)
        print"vvvvvvvvvvvvvvvvvvvv",lines
        return lines
        
        
        
        
        
        
        
        
        

    
   
        

        
    
