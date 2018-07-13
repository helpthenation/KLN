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
url=os.path.dirname(os.path.realpath('Downloads'))

class ExcelExportView_2(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView_2, self).__getattribute__(name)

    @http.route('/web/export/xls_view/mfg_completed_oc', type='http', auth='user')
    def export_xls_completed_oc(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['completed.oc.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'completed_oc_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"completed_oc_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Completed Oc Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    
    @http.route('/web/export/xls_view/estimate_vs_quotation', type='http', auth='user')
    def export_xls_estimate_vs_quotation(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['estimate.vs.quotation.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'estimate_vs_quotation_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"estimate_vs_quotation_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Estimate Vs Quotation')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    @http.route('/web/export/xls_view/mfg_invoice_report', type='http', auth='user')
    def export_xls_mfg_invoice_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['mfg.invoice.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'mfg_invoice_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_invoice_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Invoice Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    @http.route('/web/export/xls_view/mfg_machine_utilization', type='http', auth='user')
    def export_xls_mfg_machine_utilization(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['machine.utilization.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'machine_utilization_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"machine_utilization_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Machine Utilization')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    @http.route('/web/export/xls_view/mfg_material_consumption', type='http', auth='user')
    def export_xls_mfg_material_consumption(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['material.consumption.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'machine_consumption_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"machine_consumption_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('Machine Consumption')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
   
    @http.route('/web/export/xls_view/mfg_estimate_report', type='http', auth='user')
    def export_xls_mfg_estimate(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['mfg.estimate.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_estimate_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_estimate_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Estimate')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    @http.route('/web/export/xls_view/mfg_rg_report', type='http', auth='user')
    def export_xls_mfg_rg_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['rg.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_rg_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_rg_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('RG Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/mfg_stock_tranfer_report', type='http', auth='user')
    def export_xls_mfg_stock_transfer(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['stock.transfer.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_stock_transfer.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_stock_transfer.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Stock Transfer')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    @http.route('/web/export/xls_view/mfg_store_stock_report', type='http', auth='user')
    def export_xls_mfg_store_stock(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['mfg.stores.stock'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_store_stock.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_store_stock.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Store Stock')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/mfg_tally_report', type='http', auth='user')
    def export_xls_mfg_tally_report(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['mfg.tally.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_tally_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_tally_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Tally Report')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    
    @http.route('/web/export/xls_view/mfg_tool_wise', type='http', auth='user')
    def export_xls_mfg_tool_wise(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['mfg.tool.wise.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'mfg_tool_wise.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"mfg_tool_wise.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Tool Wise')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/mfg_vollmer_grinding', type='http', auth='user')
    def export_xls_vollmer_grinding(self, data, token):
        print data,token
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])  
        exb_obj=request.env['vollmer.grinding.report'].browse(id)
       
        workbook = xlsxwriter.Workbook(url+'vollmer_grinding_report.xlsx')
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
        

       
        
        workbook.close()
        fo = open(url+"vollmer_grinding_report.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename('MFG Vollmer Grinding')),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )  
               
         
        
         
               
            
