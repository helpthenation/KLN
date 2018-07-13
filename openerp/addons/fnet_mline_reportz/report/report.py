from openerp import api, models
import datetime
import math
from openerp.exceptions import ValidationError,Warning
                                                                                  
                                                                                                                          
class ParticularReport(models.AbstractModel):
    _name = 'report.fnet_mline_reportz.del_note'
                
    def min_date(self,obj):     
        if obj:
            leave_form = self.env['stock.picking'].search([('origin','=',obj.origin)])
            date_time = datetime.datetime.strptime((leave_form[0].date), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')                                                                        
            return date_time 
    
    def move_line(self,obj):
        count=0
        lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
        if obj:
            self.env.cr.execute(" select sm.product_uom_qty as product, pt.description as name, pp.part_no, pp.make_no "\
                            " from stock_move sm join product_product pp on  "\
                            " (pp.id=sm.product_id) join product_template pt "\
                            " on (pt.id=pp.product_tmpl_id) where sm.picking_id=%s order by sm.id asc" % (str(obj.id)))
        line_list = [i for i in self.env.cr.dictfetchall()]
        desc_len=[]
        for i in line_list:
            txt=i['name'].split('\n')
            desc_len.append(len(txt))               
        if sum(desc_len) <= 15:
            count= count + 1
        elif sum(desc_len) > 15:
            count= math.ceil(float(count + sum(desc_len))/float(15.0))
        value=[]
        if count <= 1:
            value.append(0)
        else:
            for val in range(0,int(count)):
                value.append(val)
        return value
    
    def get_move_line(self,obj,val):
        if obj:
            self.env.cr.execute(" select sm.product_uom_qty as product, pt.description as name, sm.uom as uom, sm.item_no as item_no "\
                            " from stock_move sm join product_product pp on  "\
                            " (pp.id=sm.product_id) join product_template pt "\
                            " on (pt.id=pp.product_tmpl_id) where sm.picking_id=%s order by sm.id asc" % (str(obj.id)))
        line_list = [i for i in self.env.cr.dictfetchall()]
        desc=[]
        lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
        final=[]
        for i in line_list:
            txt=i['name'].split('\n')
            desc.append({'prod_desc':txt,'prod_qty':i['product'],'prod_uom':i['uom'],'sno':i['item_no']})
        for i in desc:
            lop=[]
            lop=lol(i['prod_desc'],15)
            bob=[]
            for j in range(len(lop)):
                  if j == 0:
                      for k in lop[j]:
                            bob.append({'desc':k,'qty':None,'sno':None,'uom':None})
                      if  bob[0]['desc']:
                          bob[0]['qty']=int(i['prod_qty'])
                          bob[0]['uom']=i['prod_uom']
                          bob[0]['sno']=i['sno']
                      else:
                          bob[1]['qty']=int(i['prod_qty'])
                          bob[1]['uom']=i['prod_uom']     
                          bob[1]['sno']=i['sno']     
                  else:
                      for k in lop[j]:
                            bob.append({'desc':k,'qty':None,'sno':None,'uom':None})
            final.extend(bob)              
        count=0
        for i in range(len(final)):
            if final[i]['qty'] != None:
                count+=1
                final[i]['desc']='<b>'+final[i]['desc']+'</b>' 
                if final[i]['sno'] == None:
                    final[i]['sno']= str(count)
   
        return_list=lol(final,15)    
        return return_list[val]
               

               
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.del_note')
        stock_pick=self.env['stock.picking'].browse(self.ids)
        #~ sale_order=self.env['sale.order'].search([('name','=',stock_pick.origin)])
        for order in stock_pick.browse(self.ids):
            docargs = {
                'doc_ids': stock_pick,
                #~ 'sale':sale_order,
                'doc_model': report.model,
                'docs': self,
            }
            if order.picking_type_id.code=='outgoing':
                return report_obj.render('fnet_mline_reportz.del_note', docargs)
            else:
                raise ValidationError('Please choose the valid report!')
 
    
 
