# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
try:
    import json
except ImportError:
    import simplejson as json
import xlsxwriter
import openerp.http as http
from openerp.http import request
from openerp import _
from openerp.exceptions import Warning
from openerp.addons.web.controllers.main import ExcelExport
import datetime
import xlrd
import os
from openerp.exceptions import except_orm, Warning, RedirectWarning
#~ url="/home/ubuntu/ERP_ApexAeA/"
url=os.path.dirname(os.path.realpath('excel_export'))

class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)



    @http.route('/web/export/xls_view/ac/loading', type='http', auth='user')
    def export_xls_view_loadding_sheet(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        ids=data.get('ids',[])
        account_invices =request.env[model].browse(ids)
        if len(account_invices) > 1:
            ac_ids = " in %s" %(tuple(account_invices.ids),)
        else:
            ac_ids = " = %s " %(account_invices.ids[0])


        workbook = xlsxwriter.Workbook(url+'loading_sheet.xlsx')
        worksheet = workbook.add_worksheet()

        merge_format1 = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'align': 'center',
                    'fg_color':'#ffff66',
                    'valign': 'vcenter',})

        merge_format2 = workbook.add_format({
            'align': 'left',
            'valign': 'vcenter',})

        merge_format3 = workbook.add_format({
             'align': 'center',
             'bold': 1,
             'border': 1,
             'font_size':14,
             'align': 'bottom',})

        merge_format4 = workbook.add_format({
            'align': 'right',
            'bold': 1,
            'valign': 'vcenter',})
        format_date = workbook.add_format({
            'num_format': 'd mmm yyyy hh:mm AM/PM',
            'align': 'left',
            })
        worksheet.merge_range('A1:E1','Loading Sheet',merge_format3)
        worksheet.write_datetime('B3', datetime.datetime.now(),format_date)
        worksheet.write(4,0,'S.No',merge_format1)
        worksheet.write(4,1,"STOCKIST NAME  - TOWN",merge_format1)
        request.env.cr.execute("""select pp.id as product_id,pt.name as product_name,sum(ail.quantity) as quantity,pc.name as pc_name  ,ai.del_method,ai.tpt_name,rp.name as trns_name from account_invoice as ai
                                            left join account_invoice_line ail on (ail.invoice_id = ai.id)
                                            left join res_partner rp on (rp.id = ai.tpt_name)
                                            left join product_product pp on (pp.id = ail.product_id)
                                            left join product_template pt on (pt.id = pp.product_tmpl_id)
                                            left join product_category pc on (pc.id=pt.categ_id)
                                            where ai.id  %s and pt.type != 'service' group by pp.id,pt.name,ai.del_method,ai.tpt_name,pc.name,rp.name  order by pp.id""" %(ac_ids,))
        product_ids = [i for i in request.cr.dictfetchall()]


        request.env.cr.execute("""select rp.id as stockist_id,rp.name as partner_name, sum(ail.quantity) as quantity ,rp.city as city from account_invoice as ai
                                                left join account_invoice_line ail on (ail.invoice_id = ai.id)
                                                left join res_partner rp on (rp.id = ai.partner_id)
                                                left join product_product pp on (pp.id = ail.product_id)
                                                left join product_template pt on (pt.id = pp.product_tmpl_id)                                                
                                                where ai.id %s  and pt.type != 'service'  group by rp.id order by rp.id""" %(ac_ids,))
        stockist_ids = [i for i in request.cr.dictfetchall()]

        worksheet.set_column(0,0,5)
        hc = 2
        deilvery_method = []
        tpt_name = []
        pc_name = []
        trns_name = []
        for p in product_ids:
            worksheet.write(4,hc, p['product_name'],merge_format1)
            worksheet.set_column(4,hc, len(p['product_name'])+5)
            deilvery_method.append(p['del_method'])
            tpt_name.append(p['tpt_name'])
            pc_name.append(p['pc_name'])
            trns_name.append(p['trns_name'])
            hc += 1
        worksheet.write(4,hc, "TOTAL",merge_format1)
        worksheet.set_column(4,hc,15)         
           
        worksheet.merge_range('B4:E4',"Product Category : " +", ".join(list(set(pc_name) )),merge_format2)
         #~ worksheet.write(1,1,"TPT.Co. Name  " +", ",join(list(set(pc_name) )),merge_format1)
        if len(set(deilvery_method)) > 1 or len(set(tpt_name)) > 1:
            return True
            
        worksheet.merge_range('B2:E2',"TPT.Co. Name    : " +", ".join(list(set(trns_name) )),merge_format2)    
        r = 5
        sn = 1
        #~ alpha = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
        #~ alpadict = dict(zip(string.ascii_lowercase, range(1,27)))
        set_comp_col = []
        for k in stockist_ids:
            worksheet.write("A"+str(r+1), sn, merge_format2)
            if k["city"]:
                worksheet.write("B"+str(r+1), k['partner_name'] + " - "+ k["city"], merge_format2)
                set_comp_col.append(len(k['partner_name'])+len(k["city"]))
            else:
                worksheet.write("B"+str(r+1), k['partner_name'] , merge_format2)
                set_comp_col.append(len(k['partner_name']))
            request.env.cr.execute("""select rp.name as stockist,pp.id as prd_id,pt.name as product_name, sum(ail.quantity) as quantity from account_invoice as ai
                left join account_invoice_line ail on (ail.invoice_id = ai.id)
                left join product_product pp on (pp.id = ail.product_id)
                left join product_template pt on (pt.id = pp.product_tmpl_id)
                left join res_partner rp on (rp.id = ai.partner_id)
                where ai.id %s and ai.partner_id = %s  and pt.type != 'service'  group by rp.id,pt.name,pp.id order by rp.id""" %(ac_ids,k['stockist_id']))
            all_stockist_details = [i for i in request.cr.dictfetchall()]
            for c in all_stockist_details:
                p = 2
                #~ t = r +1
                t = r
                for s in product_ids:
                    if s['product_id'] == c['prd_id']:
                        #~ worksheet.write(alpha[p]+str(t), c['quantity'], merge_format2)
                        worksheet.write(t,p, c['quantity'], merge_format4)
                        t += 1
                    p +=  1
            worksheet.write(r,p, k['quantity'], merge_format4)
            r += 1
            sn +=1
        
        worksheet.set_column(1,1,max(set_comp_col)+5)
        worksheet.write(r+1,1,"TOTAL",merge_format2)
        cc = 2
        cum_qty = 0
        for u in product_ids:           
            worksheet.write(r+1,cc,u['quantity'],merge_format4)
            cum_qty += u['quantity']            
            cc += 1
            
        worksheet.write(r+1,cc,cum_qty,merge_format4)
        workbook.close()
        fo = open(url+"loading_sheet.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="Loading_Sheet.xlsx"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
#
