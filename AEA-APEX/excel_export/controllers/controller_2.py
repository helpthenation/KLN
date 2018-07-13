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
from datetime import datetime
url=os.path.dirname(os.path.realpath('Purchase'))

class ExcelExportView_2(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView_2, self).__getattribute__(name)
    
    
    @http.route('/web/export/xls_view/lca_projwise', type='http', auth='user')
    def lca_projwise_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        lca_obj=request.env['lca.projectwise.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'lca_projwise_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                  
          
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.merge_range('A1:D1', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('A4:C4', 'LCA Individual Project Wise Costing ', merge_format2)
        worksheet.write('A8',"Project Number",merge_format2)
        worksheet.write('B8',"Project Name",merge_format2)
        worksheet.write('C8',"Machine Name",merge_format2)
        worksheet.write('D8',"Model No",merge_format2)
        worksheet.write('E8',"Version",merge_format2)
        worksheet.write('F8',"Budget",merge_format2)
        worksheet.write('G8',"Used",merge_format2)
        worksheet.write('H8',"Remaining",merge_format2)
        
        row=8
        col=0  
         
        for line in lca_obj.detail_ids:
            worksheet.write(row,col,(line.project_number if line.project_number else ''))
            worksheet.write(row,col+1,(line.project_name if line.project_name else ''))
            worksheet.write(row,col+2,(line.machine_id.name if line.machine_id.name else ''))
            worksheet.write(row,col+3,(line.model_no if line.model_no else ''))
            worksheet.write(row,col+4,(line.project_version if line.project_version else ''))
            worksheet.write(row,col+5,(line.budget if line.budget else ''))
            worksheet.write(row,col+6,(line.amount_used if line.amount_used else ''))
            worksheet.write(row,col+7,(line.amount_remaining if line.amount_remaining else ''))
            row=row+1
             
             
        
        worksheet.write(row,col+2,"Total Cost",merge_format2)
        worksheet.write(row,col+3,lca_obj.total_cost,merge_format2)
        
        workbook.close()
        fo = open(url+'lca_projwise_report.xlsx', "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('LCA ProjWise')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    
    @http.route('/web/export/xls_view/lca_stock_report', type='http', auth='user')
    def lca_stock_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        stock_obj=request.env['lca.stock.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'lca_stock_report.xlsx')
        worksheet = workbook.add_worksheet()
        
        merge_format_align_left = workbook.add_format({
        'bold':1,
        'border': 1,
        'font_size':12,
        'align': 'left',
        'valign': 'vcenter',
        })
       
        merge_format25=workbook.add_format({
         'align': 'center',   
               
        })
        merge_format35=workbook.add_format({
         'align': 'center',
        
              'top':2,
              'left':2,
              'right':2,
             'bottom':2
             
               
        })
        merge_left=workbook.add_format({
                                    'bold':1,
                                    
                                    'align':'center',
                                    'font_size':11,
                                    })
        merge_center_title=workbook.add_format({
                                    'bold':1,
                                    'align':'center',
                                    'font_size':14,
                                    })
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 10)        
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('F:F', 10)
        worksheet.merge_range('A'+str(0+2)+':'+'G'+str(0+1),"Leitz Tooling Systems India Pvt. Ltd." + "" ,merge_center_title)
        worksheet.merge_range('A4:G4', 'LCA STOCK REPORT',merge_left)
        worksheet.write('B6','From Date',merge_format25)
        worksheet.write('C6',stock_obj.from_date,merge_format25)
        worksheet.write('E6','To Date',merge_format25)
        worksheet.write('F6',stock_obj.to_date,merge_format25)
        worksheet.write('A8','S.No',merge_format35)
        worksheet.write('B8','Project',merge_format35)
        worksheet.write('C8','Purchase No',merge_format35)
        worksheet.write('D8','Machine',merge_format35)
        worksheet.write('E8','Model No',merge_format35)
        worksheet.write('F8','Machine Qty',merge_format35)
        worksheet.write('G8','Machine Cost',merge_format35)
        row=9
        col=0
        count=1
        for rec in stock_obj.machine_line_ids:
            worksheet.write(row,col,count,merge_format_align_left)
            worksheet.write(row,col+1,(rec.stock_project if rec.stock_project else ''),merge_format_align_left)
            worksheet.write(row,col+2,(rec.stock_po_no if rec.stock_po_no else ''),merge_format_align_left)
            worksheet.write(row,col+3,(rec.stock_machine if rec.stock_machine else ''),merge_format_align_left)
            worksheet.write(row,col+4,(rec.stock_model_no if rec.stock_model_no else '')
                            ,merge_format_align_left)
            worksheet.write(row,col+5,(rec.stock_machine_qty if rec.stock_machine_qty else ''),merge_format_align_left)
            worksheet.write(row,col+6,(rec.stock_machine_cost if rec.stock_machine_cost else ''),merge_format_align_left)
            row=row+1
            count=count+1
        
        workbook.close()
        fo = open(url+"lca_stock_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Stock report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    @http.route('/web/export/xls_view/customer_history', type='http', auth='user')
    def customer_hsitory_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        cust_obj=request.env['customer.history.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'cust_history_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                  
          
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('A1:D1', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('A4:C4', 'LCA Individual Project Wise Costing ', merge_format2)
        
         
        worksheet.write('A8',"Customer",merge_format2)
        worksheet.write('B8',"Invoice Number",merge_format2)
        worksheet.write('C8',"Tool ID",merge_format2)
        worksheet.write('D8',"Description",merge_format2)
        worksheet.write('E8',"Quantity",merge_format2)
        worksheet.write('F8',"Invoice Amt",merge_format2)
        
        worksheet.write('G8',"Invoice Remark",merge_format2)
        worksheet.write('H8',"OC Number",merge_format2)
        worksheet.write('I8',"OC Remark",merge_format2)
        worksheet.write('J8',"Quotation Number",merge_format2)
        worksheet.write('K8',"Quotation Remark",merge_format2)
        
        row=8
        col=0  
         
        for line in cust_obj.detail_ids:
            worksheet.write(row,col,(line.partner_id.name if line.partner_id.name else ''))
            worksheet.write(row,col+1,(line.invoice_number if line.invoice_number else ''))
            worksheet.write(row,col+2,(line.tool_id if line.tool_id else ''))
            worksheet.write(row,col+3,(line.tool_name if line.tool_name else ''))
            worksheet.write(row,col+4,(line.invoice_qty if line.invoice_qty else ''))
            worksheet.write(row,col+5,(line.invoice_amt if line.invoice_amt else ''))
            worksheet.write(row,col+6,(line.invoice_remark if line.invoice_remark else ''))
            worksheet.write(row,col+7,(line.oc_number if line.oc_number else ''))
            worksheet.write(row,col+8,(line.oc_remark if line.oc_remark else ''))
            worksheet.write(row,col+9,(line.quo_number if line.quo_number else ''))
            worksheet.write(row,col+10,(line.quo_remark if line.quo_remark else ''))
        
            row=row+1
             
             
         
        workbook.close()
        fo = open(url+'cust_history_report.xlsx', "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Customer History')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/lca_landed_cost_report', type='http', auth='user')
    def lca_landed_cost_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        landed_cost_obj=request.env['lca.landed.cost'].browse(id)
        workbook = xlsxwriter.Workbook(url+'lca_landed_cost.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format_align_left = workbook.add_format({
        'bold':0,
        'border': 1,
        'font_size':12,
        'align': 'left',
        'valign': 'vcenter',
        })
        merge_format25=workbook.add_format({
             'align': 'center',   
                   
            })
        merge_format35=workbook.add_format({
             'align': 'center',
                  'bold':0,
                  'top':2,
                  'left':2,
                  'right':2,
                 'bottom':2
                 
                   
            })
        
        merge_left=workbook.add_format({
                                        'bold':1,
                                        'align':'center',
                                        'font_size':11,
                                        })
        merge_center_title=workbook.add_format({
                                        'bold':1,
                                        'align':'center',
                                        'font_size':14,
                                        })
        
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 18)
        worksheet.set_column('E:E', 15)
        worksheet.set_column('F:F', 15)
        worksheet.set_column('G:G', 18)
        worksheet.set_column('H:H', 15)
        worksheet.merge_range('A'+str(0+2)+':'+'H'+str(0+1),"Leitz Tooling Systems India Pvt. Ltd." + "" ,merge_center_title)
        worksheet.merge_range('A4:H4', 'LCA LANDED COST DETAILS OF EACH MACHINE',merge_left)
        worksheet.write('C6','From Date',merge_format25)
        worksheet.write('D6',landed_cost_obj.from_date,merge_format25)
        worksheet.write('F6','To Date',merge_format25)
        worksheet.write('G6',landed_cost_obj.to_date,merge_format25)
        worksheet.write('A8','S.No',merge_format35)
        worksheet.write('B8','Machine',merge_format35)
        worksheet.write('C8','Project',merge_format35)
        worksheet.write('D8','Purchase No',merge_format35)
        worksheet.write('E8','Model No',merge_format35)
        worksheet.write('F8','Machine Qty',merge_format35)
        worksheet.write('G8','Machine Cost',merge_format35)
        row=9
        col=0
        count=1
        for rec in landed_cost_obj.machine_landed_cost_ids:
            worksheet.write(row,col,count,merge_format_align_left)
            worksheet.write(row,col+1,(rec.landed_cost_machine if rec.landed_cost_machine else ''),merge_format_align_left)
            worksheet.write(row,col+2,(rec.landed_cost_project if rec.landed_cost_project else ''),merge_format_align_left)
            worksheet.write(row,col+3,(rec.landed_cost_po_no if rec.landed_cost_po_no else ''),merge_format_align_left)
            worksheet.write(row,col+4,(rec.landed_cost_model_no if rec.landed_cost_model_no else '')
                            ,merge_format_align_left)
            worksheet.write(row,col+5,(rec.landed_cost_machine_qty if rec.landed_cost_machine_qty else ''),merge_format_align_left)
            worksheet.write(row,col+6,(rec.landed_cost_machine_cost if rec.landed_cost_machine_cost else ''),merge_format_align_left) 
            row=row+1
            count=count+1
        
        workbook.close()
        fo = open(url+"lca_landed_cost.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Landed cost report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    
    @http.route('/web/export/xls_view/lca_bought_out_report', type='http', auth='user')
    def lca_bought_out_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        bought_out_obj=request.env['lca.bought.out'].browse(id)
        workbook = xlsxwriter.Workbook(url+'lca_bought_out.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format_align_left = workbook.add_format({
        'bold':0,
        'border': 1,
        'font_size':12,
        'align': 'left',
        'valign': 'vcenter',
        })
        merge_format25=workbook.add_format({
             'align': 'center',   
                   
            })
        merge_format35=workbook.add_format({
             'align': 'center',
                  'bold':0,
                  'top':2,
                  'left':2,
                  'right':2,
                 'bottom':2
                 
                   
            })
        
        merge_left=workbook.add_format({
                                        'bold':1,
                                        'align':'center',
                                        'font_size':11,
                                        })
        merge_center_title=workbook.add_format({
                                        'bold':1,
                                        'align':'center',
                                        'font_size':14,
                                        })
        
        worksheet.set_column('A:A', 10)
        worksheet.set_column('B:B', 10)
        worksheet.set_column('C:C', 10)
        worksheet.set_column('D:D', 10)
        worksheet.set_column('E:E', 10)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.merge_range('A'+str(0+2)+':'+'L'+str(0+1),"Leitz Tooling Systems India Pvt. Ltd." + "" ,merge_center_title)
        worksheet.merge_range('A4:L4', 'REPORT OF BOUGHT OUT AND MANUFACTURED ITEMS ',merge_left)
        worksheet.write('B6','From Date',merge_format25)
        worksheet.write('C6',bought_out_obj.from_date,merge_format25)
        worksheet.write('F6','To Date',merge_format25)
        worksheet.write('G6',bought_out_obj.to_date,merge_format25)
        worksheet.write('A8','S.No',merge_format35)
        worksheet.write('B8','Project',merge_format35)
        worksheet.write('C8','Purchase No',merge_format35)
        worksheet.write('D8','Machine',merge_format35)
        worksheet.write('E8','Model No',merge_format35)
        worksheet.write('F8','Machine Qty',merge_format35)
        worksheet.write('G8','Machine Cost',merge_format35)
        worksheet.write('H8','STD/MFG',merge_format35)
        worksheet.write('I8','Machine Parts No',merge_format35)
        worksheet.write('J8','Machine Parts Qty',merge_format35)
        worksheet.write('K8','Machine Parts Cost',merge_format35)
        row=9
        col=0
        count=1
        for rec in bought_out_obj.machine_bought_out_ids:
            worksheet.write(row,col,count,merge_format_align_left)
            worksheet.write(row,col+1,rec.bought_out_project,merge_format_align_left)
            worksheet.write(row,col+2,rec.bought_out_po_no,merge_format_align_left)
            worksheet.write(row,col+3,rec.bought_out_machine,merge_format_align_left)
            worksheet.write(row,col+4,rec.bought_out_model_no
                            ,merge_format_align_left)
            worksheet.write(row,col+5,rec.bought_out_machine_qty,merge_format_align_left)
            worksheet.write(row,col+6,rec.bought_out_machine_cost,merge_format_align_left)
            worksheet.write(row,col+7,rec.bought_out_lca_std_mfg,merge_format_align_left)
            worksheet.write(row,col+8,rec.bought_out_parts_no,merge_format_align_left)
            worksheet.write(row,col+9,rec.bought_out_parts_qty,merge_format_align_left)
            worksheet.write(row,col+10,rec.bought_out_parts_cost,merge_format_align_left) 
            row=row+1
            count=count+1
        workbook.close()
        fo = open(url+"lca_bought_out.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Bought Out report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/lca_machine_sold', type='http', auth='user')
    def lca_machine_sold_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        lca_obj=request.env['lca.machine.sold.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'lca_machine_sold.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                  
        bold = workbook.add_format({'bold': True,'font_size':9}) 
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('A1:J1', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('D3:G3', 'LCA Machines Sold Report ', merge_format2)
        if lca_obj.from_date and lca_obj.to_date:
            worksheet.write('B4', 'From date',bold)
            worksheet.write('C4', lca_obj.from_date)
            worksheet.write('E4', 'To Date',bold)
            worksheet.write('F4', lca_obj.to_date)
        elif lca_obj.zone:
            worksheet.write('B4', 'Zone',bold)
            worksheet.write('C4', lca_obj.zone)
        elif lca_obj.partner_id:
            worksheet.write('B4', 'Customer',bold)
            worksheet.write('C4', lca_obj.partner_id.name)
         
        worksheet.write('A8',"Project Number",merge_format2)
        worksheet.write('B8',"Project Name",merge_format2)
        worksheet.write('C8',"Version",merge_format2)
        worksheet.write('D8',"Sold To",merge_format2)
        worksheet.write('E8',"Machine Name",merge_format2)
        worksheet.write('F8',"Model Number",merge_format2)
        worksheet.write('G8',"Serial Number",merge_format2)
        worksheet.write('H8',"Spec",merge_format2)
        worksheet.write('I8',"Qty",merge_format2)
        worksheet.write('J8',"Cost",merge_format2)
        row=8
        col=0  
         
        for line in lca_obj.detail_ids:
            worksheet.write(row,col,(line.project_id.name if line.project_id.name else ''))
            worksheet.write(row,col+1,(line.project_name if line.project_name else ''))
            worksheet.write(row,col+2,(line.project_version if line.project_version else ''))
            worksheet.write(row,col+3,(line.partner_id.name if line.partner_id.name else ''))
            worksheet.write(row,col+4,(line.machine_id.name if line.machine_id.name else ''))
            worksheet.write(row,col+5,(line.model_number if line.model_number else ''))
            worksheet.write(row,col+6,(line.serial_number if line.serial_number else ''))
            worksheet.write(row,col+7,(line.spec if line.spec else ''))
            worksheet.write(row,col+8,(line.qty if line.qty else ''))
            worksheet.write(row,col+9,(line.cost if line.cost else ''))
        
            row=row+1
             
             
         
        workbook.close()
        fo = open(url+'lca_machine_sold.xlsx', "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('LCA Machine Sold')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    @http.route('/web/export/xls_view/service_account_report', type='http', auth='user')
    def service_account_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        inv_obj=request.env['service.account.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'service_account_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        bold = workbook.add_format({'bold': True,'font_size':9})
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':9,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:B', 14)
        worksheet.set_column('C:C', 14)
        worksheet.set_column('D:D', 14)
        worksheet.set_column('E:E', 14)
        worksheet.set_column('F:F', 14)
        worksheet.set_column('G:G', 14)
        worksheet.merge_range('A2:H2', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('B3:G3', ' Service Account Report', merge_format)
        worksheet.write('B4', 'From',bold)
        worksheet.write('C4', inv_obj.from_date)
        worksheet.write('E4', 'To',bold)
        worksheet.write('F4', inv_obj.to_date)
        bold = workbook.add_format({'bold': True,'font_size':9})
        normal = workbook.add_format({'font_size':9})
        worksheet.write('A6', 'Customer',bold)
        worksheet.write('B6', 'Zone',bold)
        worksheet.write('C6', 'Invoice No',bold)
        worksheet.write('D6', 'Value',bold)
        worksheet.write('E6', 'Discount',bold)
        worksheet.write('F6', 'Service Tax',bold)
        worksheet.write('G6', 'SBC',bold)
        worksheet.write('H6', 'Courier and Freight',bold)
        worksheet.write('I6', 'Total Value',bold)

        row = 7
        col = 0
        taxed=0.0
        for rec in inv_obj.account_report_ids:
            cur_obj=request.env['tax.detail'].search([('name','=',rec.tax_id)])
            for line in cur_obj:
                taxed=taxed+(rec.amount_untaxed*(line.tax_calc/100))
            disc_price=(rec.amount_untaxed * rec.discount)/100
            total=rec.amount_untaxed+taxed+rec.freight-disc_price
            worksheet.write(row, col,(rec.partner_id.name if rec.partner_id.name else '' ),normal)
            worksheet.write(row, col + 1, (rec.zone if rec.zone else '' ),normal)
            worksheet.write(row, col + 2, (rec.invoice_no if rec.invoice_no else '' ),normal )
            worksheet.write(row, col + 3, (rec.amount_untaxed if rec.amount_untaxed else 0 ),normal)
            worksheet.write(row, col + 4, (rec.discount if rec.discount else ''),normal)
            worksheet.write(row, col + 5, (rec.tax_id if rec.tax_id else ''),normal)
            worksheet.write(row, col + 6, (rec.tax_ids if rec.tax_ids else ''),normal)
            worksheet.write(row, col + 7, (rec.freight if rec.freight else ''),normal)
            worksheet.write(row, col + 8, (total if total else ''),normal)
            
            
        
            row+=1
         
        workbook.close()
        fo = open(url+"service_account_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Service Account Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/service_special_report', type='http', auth='user')
    def service_special_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        inv_obj=request.env['service.speical.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'service_special_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        bold = workbook.add_format({'bold': True,'font_size':9})
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':9,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:B', 14)
        worksheet.set_column('C:C', 14)
        worksheet.set_column('D:D', 14)
        worksheet.set_column('E:E', 14)
        worksheet.set_column('F:F', 14)
        worksheet.set_column('G:G', 14)
        worksheet.merge_range('A2:G2', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('B3:F3', ' Service Special Report', merge_format)
        worksheet.write('B4', 'Customer',bold)
        worksheet.write('C4', inv_obj.partner_id.name)
        worksheet.write('E4', 'Product',bold)
        worksheet.write('F4', inv_obj.product_id.name)
        bold = workbook.add_format({'bold': True,'font_size':9})
        normal = workbook.add_format({'font_size':9})
        worksheet.write('A6', 'Customer',bold)
        worksheet.write('B6', 'Zone',bold)
        worksheet.write('C6', 'Customer category',bold)
        worksheet.write('D6', 'Product',bold)
        worksheet.write('E6', 'Tool Category',bold)
        worksheet.write('F6', 'Qty',bold)
        worksheet.write('G6', 'Amount',bold)

        row = 7
        col = 0
        for rec in inv_obj.special_report_ids:
            worksheet.write(row, col,(rec.partner_id.name if rec.partner_id.name else '' ),normal)
            worksheet.write(row, col + 1, (rec.zone if rec.zone else '' ),normal)
            worksheet.write(row, col + 2, (rec.customer_categ.name if rec.customer_categ.name else '' ),normal )
            worksheet.write(row, col + 3, (rec.product_id.name if rec.product_id.name else 0 ),normal)
            worksheet.write(row, col + 4, (rec.tool_category.name if rec.tool_category.name else ''),normal)
            worksheet.write(row, col + 5, (rec.order_qty if rec.order_qty else ''),normal)
            worksheet.write(row, col + 6, (rec.amount if rec.amount else ''),normal)
            row+=1
         
        workbook.close()
        fo = open(url+"service_special_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Service Special Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/entry_tax_report', type='http', auth='user')
    def entry_tax_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        entry_tax=request.env['entry.tax.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'entry_tax_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                 
         
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('F2:I2','Leitz Tooling Systems India Pvt. Ltd.', merge_format)
        worksheet.write('H7','Entry Tax', merge_format2)
        worksheet.write('G10', 'From', merge_format1)
        worksheet.write('H10',entry_tax.from_date,merge_format1)
        worksheet.write('I10', 'To', merge_format1)
        worksheet.write('J10',entry_tax.to_date,merge_format1)
        worksheet.merge_range('D12:F12','Details of Import Bill of Entry', merge_format)
        worksheet.write('J12','Landed Cost - INR',merge_format1)
        worksheet.merge_range('N12:P12','Details of Sales, Transfers, Free Samples & Replacement', merge_format)

        worksheet.write('A13',"Lot No",merge_format2)
        worksheet.write('B13',"LOT Date",merge_format2)
        worksheet.write('C13',"B/E No",merge_format2)
        worksheet.write('D13',"B/E Date",merge_format2)
        worksheet.write('E13',"Import Invoice Number",merge_format2)
        worksheet.write('F13',"Import Invoice Date",merge_format2)
        worksheet.write('G13',"Total Euro Valuie",merge_format2)
        worksheet.write('H13',"Rate as per Yahoo Rate",merge_format2)
        worksheet.write('I13',"INR Cost",merge_format2)
        worksheet.write('J13',"Duty as per BOE",merge_format2)
        worksheet.write('K13',"Total LC ",merge_format2)
        worksheet.write('L13',"Invoice Date",merge_format2)
        worksheet.write('M13',"Customer Name",merge_format2)
        worksheet.write('N13',"Place",merge_format2)
        worksheet.write('O13',"Invoice No",merge_format2)
        worksheet.write('P13',"Landed Cost",merge_format2)
        worksheet.write('Q13',"Invoice NetPrice",merge_format2)

        row=15
        col=0  
        count=1
        for line in entry_tax.entry_tax_ids:
            worksheet.write(row,col,line.lot_no if line.lot_no else '')
            worksheet.write(row,col+1,line.lot_date if line.lot_date else '')
            worksheet.write(row,col+2,line.bill_of_entry if line.bill_of_entry else '')
            worksheet.write(row,col+3,line.bill_of_entry_date if line.bill_of_entry_date else '')
            worksheet.write(row,col+4,line.import_invoice_number if line.import_invoice_number else '')
            worksheet.write(row,col+5,line.import_invoice_date if line.import_invoice_date else '')
            worksheet.write(row,col+6,line.total_euro if line.total_euro else '')
            worksheet.write(row,col+7,line.rate_per_yahoo if line.rate_per_yahoo else '')
            worksheet.write(row,col+8,line.inr_cost if line.inr_cost else '')
            worksheet.write(row,col+9,line.duty_as_per_boe if line.duty_as_per_boe else '')
            worksheet.write(row,col+10,line.total_lc if line.total_lc else '')
            worksheet.write(row,col+11,line.invoice_date if line.invoice_date else '')
            worksheet.write(row,col+12,line.customer_name if line.customer_name else '')
            worksheet.write(row,col+13,line.place if line.place else '')
            worksheet.write(row,col+14,line.invoice_no if line.invoice_no else '')
            worksheet.write(row,col+15,line.landed_cost if line.landed_cost else '')
            worksheet.write(row,col+16,line.invoice_net_price if line.invoice_net_price else '')
            count=count+1
            row=row+1
        workbook.close()
        fo = open(url+"entry_tax_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Entry Tax Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/oc_in_stock', type='http', auth='user')
    def export_xls_view_oc_in_stock(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        oc_in_stock_obj=request.env['oc.in.stock.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'oc_in_stock.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                 
         
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('C1:G1', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('D3:F3', 'Pending Customer Orders (In-Stock)', merge_format)
        worksheet.write('C5', 'From :', merge_format)
        worksheet.write('E5', oc_in_stock_obj.from_date, merge_format)
        worksheet.write('F5', 'To:', merge_format)
        worksheet.write('G5', oc_in_stock_obj.to_date, merge_format)
        worksheet.write('A7','Customer',merge_format2)
        worksheet.write('B7','O.C.No.',merge_format2)
        worksheet.write('C7','O.C.Dt',merge_format2)
        worksheet.write('D7', 'Tool ID',merge_format2)
        worksheet.write('E7', 'Required Qty.',merge_format2)
        worksheet.write('F7', 'Blocked Qty.',merge_format2)
        worksheet.write('G7', 'Despatched Qty.',merge_format2)
        worksheet.write('H7', 'Pending Qty.',merge_format2)
        worksheet.write('I7', 'Stock After Blocking',merge_format2)
        worksheet.write('J7', 'Amount',merge_format2)
        worksheet.write('K7', 'Remarks',merge_format2)
        row=7
        col=0
        for line in oc_in_stock_obj.oc_in_stock_ids:
            worksheet.write(row, col,line.partner_id.name if line.partner_id else '')
            worksheet.write(row, col+1,line.sale_id.name if line.sale_id else '')
            worksheet.write(row, col+2,line.oc_date if line.oc_date else '')
            worksheet.write(row, col+3,line.tool_id.name if line.tool_id else '')
            worksheet.write(row, col+4,line.quantity if line.quantity else '')
            worksheet.write(row, col+5,line.block_qty if line.block_qty else '')
            worksheet.write(row, col+6,line.despatched_qty if line.despatched_qty else '')
            worksheet.write(row, col+7,line.pending_qty if line.pending_qty else '')
            worksheet.write(row, col+8,line.stock_after_block if line.stock_after_block else '')
            worksheet.write(row, col+9,line.total_amount if line.total_amount else '')
            worksheet.write(row, col+10,line.remarks if line.remarks else '')

            row=row+1
        
        req_qty=0.0
        blocked_qty=0.0
        dispatched_qty=0.0
        pending_qty=0.0
        stock_after_blocking=0.0
        amount=0.0
        for line in oc_in_stock_obj.oc_in_stock_ids:
            req_qty=req_qty+line.quantity              
            blocked_qty=blocked_qty+line.block_qty
            dispatched_qty=dispatched_qty+line.despatched_qty
            stock_after_blocking=stock_after_blocking+line.stock_after_block
            pending_qty=pending_qty+line.pending_qty
            amount=amount+line.total_amount
        row=row+1
        worksheet.write(row, col+1,"Grand Total")
        worksheet.write(row, col+4,req_qty) 
        worksheet.write(row, col+5,blocked_qty)
        worksheet.write(row, col+6,dispatched_qty)
        worksheet.write(row, col+7,pending_qty)
        worksheet.write(row, col+8,stock_after_blocking)
        worksheet.write(row, col+9,amount)



       
        
        workbook.close()
        fo = open(url+"oc_in_stock.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('OC IN Stock')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/credit_approval_report', type='http', auth='user')
    def credit_approval_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        credit_obj=request.env['credit.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'credit_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                 
         
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('A1:C1', 'Credit Approval Report', merge_format)
        worksheet.write('A5', 'From', merge_format1)
        worksheet.write('B5',credit_obj.from_date,merge_format1)
        worksheet.write('C5', 'To', merge_format1)
        worksheet.write('D5',credit_obj.to_date,merge_format1)
        worksheet.write('A8',"SINO")
        worksheet.write('B8',"Sale Order",merge_format2)
        worksheet.write('C8',"Partner Name",merge_format2)
        worksheet.write('D8',"Total Amount",merge_format2)
        worksheet.write('E8',"State",merge_format2)
        worksheet.write('F8',"Date Approved",merge_format2)
        worksheet.write('G8',"Date Hold",merge_format2)
        worksheet.write('H8',"Date Partial",merge_format2)
        worksheet.write('I8',"Date Appeal",merge_format2)
        
        row=9
        col=0  
        count=1
        for line in credit_obj.credit_report_ids:
            worksheet.write(row,col,count)
            worksheet.write(row,col+1,line.order_id.name)
            worksheet.write(row,col+2,line.partner_id.name)
            worksheet.write(row,col+3,line.total_amount)
            worksheet.write(row,col+4,line.state)
            worksheet.write(row,col+5,(line.date_approved if line.date_approved else ''))
            worksheet.write(row,col+6,line.date_appeal if line.date_appeal else '')
            worksheet.write(row,col+7,line.date_hold if line.date_hold else '')
            worksheet.write(row,col+8,line.date_partial if line.date_partial else '')
            
            count=count+1
            row=row+1
        workbook.close()
        fo = open(url+"credit_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Credit Approval Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/purchase_register_report', type='http', auth='user')
    def export_xls_view_purchase_register(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        purchase_obj=request.env['purchase.register'].browse(id)
        workbook = xlsxwriter.Workbook(url+'purchase_register_report.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format = workbook.add_format({
                            'bold':1,
                            'border': 2,
                            'font_size':12,
                            'align': 'center',
                            'valign': 'vcenter',
                          })
        merge_format2 = workbook.add_format({
                             'right':2,
                             'bottom':2,            
                            'font_size':9,
                            'align': 'center',
                            'valign': 'vcenter',
                          })
        normal = workbook.add_format({
                    'font_size':9,
                    'align': 'center',
                    'valign': 'vcenter',
                    })
        bold = workbook.add_format({'bold': True})
        worksheet.merge_range('A4:R4', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('A5:R5', 'NO 486C, IV PHASE, 14TH CROSS, PEENYA INDUSTRIAL AREA, BANGALORE - 560 058', merge_format)
        worksheet.merge_range('F6:L6', 'Purchase Register', merge_format2)
        worksheet.write('E9', 'Lot No',bold)
        worksheet.write('F9', purchase_obj.lot_no,normal)
        worksheet.write('J9', 'Lot Invoice No',bold)
        worksheet.write('K9', purchase_obj.lot_invoice_number,normal)
        worksheet.write('E10', 'Bill Of Entry Number',bold)
        worksheet.write('F10', purchase_obj.bill_entry,normal)
        worksheet.write('J10', 'Excahnge rate',bold)
        worksheet.write('K10', purchase_obj.exchange_rate,normal)
        worksheet.write('E11', 'Bank rate',bold)
        worksheet.write('F11', purchase_obj.bank_rate,normal)
        worksheet.write('J11', 'Lot Invoice Date',bold)
        worksheet.write('K11', purchase_obj.lot_invoice_date,normal)
        worksheet.write('A14', 'PO No',bold)
        worksheet.write('B14', 'Tool ID',bold)
        worksheet.write('C14', 'Unit INR Conversion',bold)
        worksheet.write('D14', 'Unit price in EURO',bold)
        worksheet.write('E14', 'Assessable Value',bold)
        worksheet.write('F14', 'Custom Duty',bold)
        worksheet.write('G14', 'CVD 12.5%',bold)
        worksheet.write('H14', 'ED Cess2%',bold)
        worksheet.write('I14', 'HSS Ed Cess1%',bold)
        worksheet.write('J14', 'Addl Duty Import',bold)
        worksheet.write('K14', 'Tariff Classification',bold)
        worksheet.write('L14', 'Qty',bold)
        worksheet.write('M14', 'Total INR',bold)
        worksheet.write('N14', 'Total',bold)
        worksheet.write('O14', 'Total Landed Cost',bold)
        worksheet.write('P14', 'Total Duty Paid',bold)
        worksheet.write('Q14', 'Total Euro',bold)
        worksheet.write('R14', 'CVD/unit',bold)
        row = 15
        col = 0
        for rec in purchase_obj.purchase_details_ids:
            worksheet.write(row, col,(rec.po_id.name if rec.po_id.name else '' ),normal)
            worksheet.write(row, col + 1, (rec.product_id.name if rec.product_id.name else '' ),normal)
            worksheet.write(row, col + 2, (rec.unit_inr_conversion if rec.unit_inr_conversion else '' ),normal )
            worksheet.write(row, col + 3, (rec.unit_euro if rec.unit_euro else 0 ),normal)
            worksheet.write(row, col + 4, (rec.assessable_value if rec.assessable_value else ''),normal)
            worksheet.write(row, col + 5, (rec.custom_duty if rec.custom_duty else ''),normal)
            worksheet.write(row, col + 6, (rec.cvd if rec.cvd else ''),normal)
            worksheet.write(row, col+7,(rec.ed_cess if rec.ed_cess else '' ),normal)
            worksheet.write(row, col + 8, (rec.hss_ed_cess if rec.hss_ed_cess else '' ),normal)
            worksheet.write(row, col + 9, (rec.addl_duty_imports if rec.addl_duty_imports else '' ),normal )
            worksheet.write(row, col + 10, (rec.tariff_classification if rec.tariff_classification else 0 ),normal)
            worksheet.write(row, col + 11, (rec.quantity if rec.quantity else ''),normal)
            worksheet.write(row, col +12, (rec.total_inr if rec.total_inr else ''),normal)
            worksheet.write(row, col + 13, (rec.total if rec.total else ''),normal)
            worksheet.write(row, col + 14, (rec.total_cost if rec.total_cost else ''),normal)
            worksheet.write(row, col + 15, (rec.total_paid if rec.total_paid else ''),normal)
            worksheet.write(row, col + 16, (rec.total_euro if rec.total_euro else ''),normal)
            worksheet.write(row, col + 17, (rec.cvd_unit if rec.cvd_unit else ''),normal)
            row+=1
        
        workbook.close()
        fo = open(url+"purchase_register_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Purchase register Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/pending_quotation_report', type='http', auth='user')
    def lca_pending_quotation_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        lca_obj=request.env['lca.pending.quotation'].browse(id)
        workbook = xlsxwriter.Workbook(url+'pending_quotation_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        bold = workbook.add_format({'bold': True,'font_size':9})
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':9,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:B', 14)
        worksheet.set_column('C:C', 14)
        worksheet.set_column('D:D', 14)
        worksheet.set_column('E:E', 14)
        worksheet.merge_range('A2:G2', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('B3:F3', ' Pending Quotation Report', merge_format)
        if lca_obj.from_date and lca_obj.to_date:
            worksheet.write('B4', 'From date',bold)
            worksheet.write('C4', lca_obj.from_date)
            worksheet.write('E4', 'To Date',bold)
            worksheet.write('F4', lca_obj.to_date)
        elif lca_obj.zone:
            worksheet.write('B4', 'Zone',bold)
            worksheet.write('C4', lca_obj.zone)
        bold = workbook.add_format({'bold': True,'font_size':9})
        normal = workbook.add_format({'font_size':9})
        worksheet.write('A6', 'Quotation NO',bold)
        worksheet.write('B6', 'Customer',bold)
        worksheet.write('C6', 'Project No',bold)
        worksheet.write('D6', 'Project Name',bold)
        
        row = 7
        col = 0
        for rec in lca_obj.pending_quotation_ids:
            worksheet.write(row, col,(rec.quotation_id.name if rec.quotation_id.name else '' ),normal)
            worksheet.write(row, col + 1, (rec.partner_id.name if rec.partner_id.name else '' ),normal)
            worksheet.write(row, col + 2, (rec.project_id.name if rec.project_id.name else '' ),normal )
            worksheet.write(row, col + 3, (rec.project_name if rec.project_name else 0 ),normal)
            row+=1
         
        workbook.close()
        fo = open(url+"pending_quotation_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Pending Quotation Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    @http.route('/web/export/xls_view/exhibition_details', type='http', auth='user')
    def export_xls_leitz_exhibition_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        dic={'first_week':'First Week','second_week':'Second Week','four_week':'Fourth Week'}
        exb_obj=request.env['leitz.exhibition.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'leitz.exhibition.report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':12,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
                 
         
        merge_format1 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
                                             'bold': 1, 'align': 'center',
                                             'valign': 'vcenter',
                                             'underline': 'underline',})
        merge_format3 = workbook.add_format({
                                             'align': 'left',
                                             'valign': 'vcenter','bold': 1,})
        merge_format4 = workbook.add_format({
                                             'align': 'right',
                                             'valign': 'vcenter','bold': 1,}) 
        worksheet.merge_range('A1:G1', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('A2:G2', 'Exhibition Details', merge_format)
        worksheet.write('A4', 'Exhibition No', merge_format)
        worksheet.write('B4', exb_obj.exhibition_id.name, merge_format)
        worksheet.write('E4', 'State', merge_format)
        worksheet.write('F4', exb_obj.state_id.name, merge_format)
        worksheet.write('A6','City',merge_format2)
        worksheet.write('B6',exb_obj.city_id.name,merge_format2)
        worksheet.write('E6','Act Before',merge_format2)
        worksheet.write('F6',dic[str(exb_obj.act_before)],merge_format2)
        worksheet.write('A8', 'Customer',merge_format2)
        worksheet.write('B8', 'Activity',merge_format2)
        worksheet.write('C8', 'Product Dealing With',merge_format2)
        worksheet.write('D8', 'Project Plan',merge_format2)
        worksheet.write('E8', 'Additional Info',merge_format2)
        worksheet.write('F8', 'Data Collected By',merge_format2)
        worksheet.write('G8', 'Is Exist',merge_format2)
        

        
        row=9
        col=0
        for line in exb_obj.leitz_exhibition_ids:
            worksheet.write(row, col,line.customer if line.customer else '')
            worksheet.write(row, col+1,line.activity if line.activity else '')
            worksheet.write(row, col+2,line.product_dealing if line.product_dealing else '')
            worksheet.write(row, col+3,line.project_plan if line.project_plan else '')
            worksheet.write(row, col+4,line.additional_info if line.additional_info else '')
            worksheet.write(row, col+5,line.data_collected if line.data_collected else '')
            worksheet.write(row, col+6,"Existing Customer" if line.is_existing_exhibition else 'New Customer')

            row=row+1
        
      


       
        
        workbook.close()
        fo = open(url+"leitz.exhibition.report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Leitz To Exhibition Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xls_view/pending_order_report', type='http', auth='user')
    def lca_pending_order_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        lca_obj=request.env['lca.pending.order'].browse(id)
        workbook = xlsxwriter.Workbook(url+'pending_order_report.xlsx')
        worksheet = workbook.add_worksheet()
        #creation of header
        bold = workbook.add_format({'bold': True,'font_size':9})
        merge_format = workbook.add_format({
                    'bold': 1,
                    'border': 1,
                    'font_size':9,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'white'})
        worksheet.set_column('A:A', 14)
        worksheet.set_column('B:B', 14)
        worksheet.set_column('C:C', 14)
        worksheet.set_column('D:D', 14)
        worksheet.set_column('E:E', 14)
        worksheet.merge_range('A2:G2', 'LEITZ TOOLING SYSTEMS INDIA PVT LTD', merge_format)
        worksheet.merge_range('B3:F3', ' Pending Order Report', merge_format)
        if lca_obj.from_date and lca_obj.to_date:
            worksheet.write('B4', 'From date',bold)
            worksheet.write('C4', lca_obj.from_date)
            worksheet.write('E4', 'To Date',bold)
            worksheet.write('F4', lca_obj.to_date)
        elif lca_obj.zone:
            worksheet.write('B4', 'Zone',bold)
            worksheet.write('C4', lca_obj.zone)
        bold = workbook.add_format({'bold': True,'font_size':9})
        normal = workbook.add_format({'font_size':9})
        worksheet.write('A6', 'OC NO',bold)
        worksheet.write('B6', 'Customer',bold)
        worksheet.write('C6', 'Project No',bold)
        worksheet.write('D6', 'Project Name',bold)
        
        row = 7
        col = 0
        for rec in lca_obj.pending_order_ids:
            worksheet.write(row, col,(rec.order_id.name if rec.order_id.name else '' ),normal)
            worksheet.write(row, col + 1, (rec.partner_id.name if rec.partner_id.name else '' ),normal)
            worksheet.write(row, col + 2, (rec.project_id.name if rec.project_id.name else '' ),normal )
            worksheet.write(row, col + 3, (rec.project_name if rec.project_name else 0 ),normal)
            row+=1
         
        workbook.close()
        fo = open(url+"pending_order_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Pending Order Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
