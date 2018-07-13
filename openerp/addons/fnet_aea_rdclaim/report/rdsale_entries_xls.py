import xlwt
from datetime import datetime
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.fnet_aea_rdclaim.wizard.rdclaim_wizard \
    import rdclaim_wizard
from openerp.tools.translate import _
from openerp import pooler
from openerp.report import report_sxw
from common_header import common_header
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from xlsxwriter.utility import xl_cell_to_rowcol
from itertools import groupby
import itertools
from operator import itemgetter
class rdclaim_xls(ReportXlsx):
    
    def _get_sale_entries_product(self,data):
        self.env.cr.execute("""SELECT DISTINCT
                                      pp.id as product_id,
                                      pp.name_template,
                                      pp.default_code,
                                      pt.categ_id
                                      From
                                      product_template pt
                                      JOIN product_product pp ON pp.product_tmpl_id = pt.id
                                      WHERE pt.categ_id=%d  and pt.company_id=%s and pp.name_template::text not like '%s'
                                      ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['company_id'][0],'%ROUND%'))
        line_list = [i for i in self.env.cr.dictfetchall()]
        return line_list
            
    def _get_stockiest_line(self,data):
        head=self._get_sale_entries_product(data)
        final_list=[]
        date_query=''
        if data['form']['date_from'] and data['form']['date_to']:
            date_query=" and se.date_from >= '%s' and se.date_from <= '%s' "%(data['form']['date_from'],data['form']['date_to'])        
        manager_list=[]
        if  data['form']['manager_id']:
            manager_list.append(data['form']['manager_id'][0])
        else:
            self.env.cr.execute("""select distinct user_id as id from crm_case_section where company_id = %d"""%(data['form']['company_id'][0]))
            sale_rep=self.env.cr.dictfetchall()
            for rec in  sale_rep:
                manager_list.append(rec['id'])
        #~ print'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',manager_list
        if manager_list != []:
            for m in manager_list:
                ss=[]
                user = self.env['res.users'].browse(m)
                self.env.cr.execute("""select sml.member_id as id from res_users rs 
                    join crm_case_section ccs on ccs.user_id = rs.id 
                    join sale_member_rel sml on ccs.id = sml.section_id
                    where ccs.user_id = %d"""%(m))
                sr_list=self.env.cr.dictfetchall()
                #~ print'SRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',sr_list
                if sr_list != []:
                    
                    for k in sr_list:
                        #~ print'########################################',k['id'],m
                        stockiest_list = []
                        self.env.cr.execute("""SELECT DISTINCT
                                      res_partner.name,res_partner.city,res_partner.id
                                      FROM res_partner
                                      JOIN res_users on res_users.id = res_partner.user_id where  res_users.id = %d and res_partner.company_id=%s
                                      ORDER BY res_partner.id ASC"""%(k['id'],data['form']['company_id'][0]))
                        line_list =  self.env.cr.dictfetchall()
                        #~ print'LINE_LISTTTTTTTTTTTTTTT',line_list
                        self.env.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d and res_partner.company_id=%s"""%(k['id'],data['form']['company_id'][0]))
                        stockiest= self.env.cr.dictfetchall()
                        #~ print'STOCKIESTTTTTTTTTTTTTTTTTTTT',stockiest
                        salesrep_qty=[]
                        for j in line_list:
                            slist=[]
                            awt=[]
                            #~ print'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query
                            prod = self.env['res.partner'].browse(j['id'])
                            self.env.cr.execute("""
                                    SELECT pp.default_code as code,
                                    coalesce(sum(sel.amount),0.0) as quantity,
                                    coalesce(sum(sel.current_stock),0.0) as opening,
                                    coalesce(sum(sel.sale_stock),0.0) as sale,
                                    coalesce(coalesce(sum(sel.current_stock),0.0) + coalesce(sum(sel.sale_stock),0.0)  - coalesce(sum(sel.amount),0.0),0.0) as closing
                                    FROM  sale_entry  se
                                    left join sale_entry_line sel on se.id = sel.sale_entry_id
                                    left join product_product pp on pp.id = sel.product_id
                                    where se.partner_id=%d and se.prod_categ_id=%d and se.company_id=%d %s
                                    group by pp.default_code
                                    order by pp.default_code asc
                                
                                """%(j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query))
                            OPEN_list = [q for q in self.env.cr.dictfetchall()]
                            
                            
                            if OPEN_list != []:
                                salesrep_qty.extend(OPEN_list)
                                slist.append({'opening':OPEN_list})
                                stockiest_list.append({'name':prod.name,'city':prod.city,'lines':slist})
                        #~ ss.append({'saleperson':stockiest[0]['name'],
                            #~ 'sp_city':stockiest[0]['city'],
                            #~ 'customer_lines':stockiest_list})
                        salerep_total=sorted(salesrep_qty,key=itemgetter('code'))
                        grouped_salerep_total={}
                        for key,value in itertools.groupby(salerep_total,key=itemgetter('code')):
                            for i in value:
                                grouped_salerep_total.setdefault(key, []).append(i) 
                        sales_reps_totals=[]
                        for key,value in sorted(grouped_salerep_total.iteritems()):
                            opening=0.0 
                            rd=0.0  
                            awd=0.0
                            close=0.0
                            for val in value:
                                opening+=val['opening']
                                rd+=val['quantity']
                                awd+=val['sale']
                                close+=val['closing']
                            sales_reps_totals.append({'code':key,'opening':opening,'awd':awd,'rd':rd,'close':close})      
                        #~ print'OE###############################################',   sales_reps_totals
                        ss.append({'saleperson':stockiest[0]['name'],
                            'sp_city':stockiest[0]['city'],
                            'customer_lines':stockiest_list,                        
                            'sales_reps_totals':sales_reps_totals})                     
                final_list.append({'manager_name':user.login,'salesrep':ss})      
        #~ print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',final_list
        return final_list                 
    def _get_sale_entries_categ_name(self,data):
        #~ print"DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",data
        self.env.cr.execute("""SELECT DISTINCT
                                  pc.id,
                                  pc.name
                                  FROM product_category pc
                                  where pc.company_id=%d
                                  ORDER BY pc.name ASC"""%(data['form']['company_id'][0]))
        categ_list=self.env.cr.dictfetchall()
        return  categ_list  
    def _get_sale_manager_name(self,data):
        if data['form']['manager_id']:
            return data['form']['manager_id'][1]
        else:
            return "N/A"
            
    def generate_xlsx_report(self, workbook, data, obj):
        product_name=self._get_sale_entries_product(data)
        stockiest_line=self._get_stockiest_line(data)
        product_categ=self._get_sale_entries_categ_name(data)      
        sales_manager=self._get_sale_manager_name(data)      
        sheet = workbook.add_worksheet()
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bg_color': '#D3D3D3', 'bold': True})
        format1.set_font_color('#000080')
        format2 = workbook.add_format({'font_size': 10,'bg_color': '#D3D3D3', 'bold': True})
        format3 = workbook.add_format({'font_size': 10, 'bold': True})
        format4 = workbook.add_format({'font_size': 10})
        format5 = workbook.add_format({'font_size': 10, 'bold': True, 'bg_color': '#D3D3D3'})
        format6 = workbook.add_format({'font_size': 10, 'bold': True,'bg_color':'#67CCEB'})
        format7 = workbook.add_format({'font_size': 10, 'bold': True,'bg_color':'#EBAA2A'})
        format5.set_font_color('#000000')
        format1.set_align('center')
        format2.set_align('left')
        format2.set_font_color('#000080')
        format3.set_align('left')
        format3.set_num_format('#,##0')
        format2.set_num_format('#,##0')
        format6.set_num_format('#,##0')
        format7.set_num_format('#,##0')
        format4.set_align('center')
        form = data['form']
        com_obj=self.env['res.company'].browse(form['company_id'][0])
        sheet.merge_range('A2:K3', str(form['company_id'][1])+' - Sale Entries Analysis', format1)
        row = 5
        col = 0
        
        
        #~ print'FORMMMMMMMMMMMMMMMMMMMMMMM',form['is_open']
        sheet.merge_range(row, col, row, col+1, 'Start Date :', format2)
        sheet.merge_range(row, col+2, row, col+6, form['date_from'], format2)
        sheet.merge_range(row, col+7, row, col+8,'Stop Date :', format2)
        sheet.merge_range(row, col+9, row, col+10, form['date_to'], format2)
        row += 1
        sheet.merge_range(row, col, row, col+1, 'Product Category', format2)
        sheet.merge_range(row, col+2, row, col+6, form['prod_categ_id'][1], format2)
        sheet.merge_range(row, col+7, row, col+8, "Sales Manager", format2)
        sheet.merge_range(row, col+9, row, col+10, sales_manager,format2)
        row += 2
        num=3
        sheet.write(row, col,str("Stockiest Name"),format5)
        sheet.write(row, col+1,str("Product Code"),format5)
        col=2
        for prod in product_name:
            #~ sheet.merge_range(row, col, row, col + 2, prod['default_code'] and str(prod['default_code']), format3)
            sheet.write(row, col,
                        prod['default_code'] and str(prod['default_code']),
                        format5)       
            col+=1
        sheet.write(row,col,"Total Qty",format5)                     
        row += 1
        num=3
        col=2
        for rec in stockiest_line:
            manager_opening=0
            manager_awd=0
            manager_sale=0
            manager_closing=0
            for line in rec['salesrep']:
                #~ print'LINEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',line
                col=0
                sheet.merge_range(row, col,row, col+2,"Sale Representative - " + str(line['saleperson']),format6)           
                #~ print'LINESSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',line['sales_reps_totals']
                stockiest_opening=0.0
                stockiest_awd=0.0
                stockiest_sale=0.0
                stockiest_closing=0.0             
                for kk in line['customer_lines']:
                    row+=2              
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,str(kk['name'])+str(' - ')+str(kk['city']),format3) 
                    row+=1              
                    #~ print'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj',j
                    for j in kk['lines']:
                        cols=1
                        columns = xl_col_to_name(cols)
                        ref=str(columns)+str(row)
                        sheet.write(ref,"Opening Stock Qty",format3)  
                        open_qty=0.0
                        if form['is_open']:
                            for p in j['opening']: 
                                cols+=1
                                open_qty+=int(p['opening'])
                                stockiest_opening+=int(p['opening'])
                                manager_opening+=int(p['opening'])
                                columns = xl_col_to_name(cols)
                                ref=str(columns)+str(row) 
                                sheet.write(ref,int(p['opening']) or 0,format3)
                            columns = xl_col_to_name(cols+1)
                            ref=str(columns)+str(row)
                            sheet.write(ref,int(open_qty) or 0,format3)
                        if form['is_awd']:
                            row+=1
                            cols=1 
                            awd=0.0
                            columns = xl_col_to_name(cols)
                            ref=str(columns)+str(row)
                            sheet.write(ref,"AWD To Stockiest Qty",format3)
                            for a in j['opening']: 
                                cols+=1
                                awd+=int(a['sale'])
                                stockiest_awd+=int(a['sale'])
                                manager_awd+=int(a['sale'])
                                columns = xl_col_to_name(cols)
                                ref=str(columns)+str(row) 
                                sheet.write(ref,int(a['sale']) or 0,format3)                    
                            columns = xl_col_to_name(cols+1)
                            ref=str(columns)+str(row)
                            sheet.write(ref,int(awd) or 0,format3)                
                        if form['is_sale']:
                            row+=1
                            cols=1
                            columns = xl_col_to_name(cols)
                            ref=str(columns)+str(row)
                            rd_qty=0.0
                            sheet.write(ref,"RD Sales Qty",format3) 
                            for p in j['opening']: 
                                cols+=1
                                rd_qty+=int(p['quantity'])
                                stockiest_sale+=int(p['quantity'])
                                manager_sale+=int(p['quantity'])
                                columns = xl_col_to_name(cols)
                                ref=str(columns)+str(row) 
                                sheet.write(ref,int(p['quantity']) or 0,format3)
                            columns = xl_col_to_name(cols+1)
                            ref=str(columns)+str(row)
                            sheet.write(ref,int(rd_qty) or 0,format3)                    
                        if form['is_closing']:
                            row+=1
                            cols=1
                            columns = xl_col_to_name(cols)
                            ref=str(columns)+str(row)
                            sheet.write(ref,"Closing Stock Qty",format3)
                            close=0.0                 
                            for p in j['opening']: 
                                cols+=1
                                close+=int(p['closing'])
                                stockiest_closing+=int(p['closing'])
                                manager_closing+=int(p['closing'])
                                columns = xl_col_to_name(cols)
                                ref=str(columns)+str(row) 
                                sheet.write(ref,int(p['closing']) or 0,format3)
                            columns = xl_col_to_name(cols+1)
                            ref=str(columns)+str(row)
                            sheet.write(ref,int(close) or 0,format3)

                row+=1       
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,line['saleperson'],format6)                
                row+=1
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref," ",format6)  
                cols=1
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"Opening Stock Qty",format6)  
                open_qty=0.0
                if form['is_open']:
                    for tot in line['sales_reps_totals']:
                        #~ print'%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%',tot
                        cols+=1
                        open_qty+=tot['opening']
                        columns = xl_col_to_name(cols)
                        ref=str(columns)+str(row) 
                        sheet.write(ref,int(tot['opening']) or 0,format6)
                    columns = xl_col_to_name(cols+1)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(open_qty) or 0,format6)
                if form['is_awd']:
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                     
                    cols=1 
                    awd=0.0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"AWD To Stockiest Qty",format6)
                    for a in line['sales_reps_totals']: 
                        cols+=1
                        awd+=int(a['awd'])
                        columns = xl_col_to_name(cols)
                        ref=str(columns)+str(row) 
                        sheet.write(ref,int(a['awd']) or 0,format6)                    
                    columns = xl_col_to_name(cols+1)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(awd) or 0,format6)                
                if form['is_sale']:
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                                 
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    rd_qty=0.0
                    sheet.write(ref,"RD Sales Qty",format6) 
                    for p in line['sales_reps_totals']: 
                        cols+=1
                        rd_qty+=int(p['rd'])
                        columns = xl_col_to_name(cols)
                        ref=str(columns)+str(row) 
                        sheet.write(ref,int(p['rd']) or 0,format6)
                    columns = xl_col_to_name(cols+1)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(rd_qty) or 0,format6)                    
                if form['is_closing']:
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                                         
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"Closing Stock Qty",format6)
                    close=0.0                 
                    for p in line['sales_reps_totals']: 
                        cols+=1
                        close+=int(p['close'])
                        columns = xl_col_to_name(cols)
                        ref=str(columns)+str(row) 
                        sheet.write(ref,int(p['close']) or 0,format6)
                    columns = xl_col_to_name(cols+1)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(close) or 0,format6)
 
                if form['is_open']:
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"Total Opening Stock",format6) 
                    cols=2
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(stockiest_opening),format6) 
                if form['is_awd']:                  
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"Total AWD To Stockiest Stock",format6) 
                    cols=2
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(stockiest_awd),format6) 
                if form['is_sale']:                 
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"Total RD Sales Stock",format6) 
                    cols=2
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(stockiest_sale),format6) 
                if form['is_closing']:                  
                    row+=1
                    cols=0
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref," ",format6)                
                    cols=1
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,"Total Closing Stock",format6) 
                    cols=2
                    columns = xl_col_to_name(cols)
                    ref=str(columns)+str(row)
                    sheet.write(ref,int(stockiest_closing),format6) 
            row+=1
            #~ row+=1       
            cols=0
            columns = xl_col_to_name(cols)
            ref=str(columns)+str(row)
            sheet.write(ref,rec['manager_name'],format7) 
            if form['is_open']:            
                row+=1
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"",format7)             
                cols=1
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"Opening Stock",format7) 
                cols=2
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,int(manager_opening),format7) 
            if form['is_awd']:              
                row+=1
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"",format7)                         
                cols=1
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"AWD To Stockiest Qty",format7) 
                cols=2
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,int(manager_awd),format7) 
            if form['is_sale']:             
                row+=1
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"",format7)            
                cols=1
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"RD Sales Qty",format7) 
                cols=2
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,int(manager_sale),format7) 
            if form['is_closing']:              
                row+=1
                cols=0
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"",format7)            
                cols=1
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,"Closing Stock Qty",format7) 
                cols=2
                columns = xl_col_to_name(cols)
                ref=str(columns)+str(row)
                sheet.write(ref,int(manager_closing),format7)            
            #~ sheet.write(row,col,rec['manager_name'],format5)
rdclaim_xls('report.fnet_aea_rdclaim.rdsale_entries_xlsx.xlsx',
                   'rdsale.entries')
