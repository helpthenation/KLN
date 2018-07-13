//  @@@ web_export_view custom JS @@@
//#############################################################################
//    
//    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
//    Copyright (C) 2012 Therp BV (<http://therp.nl>)
//
//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU Affero General Public License as published
//    by the Free Software Foundation, either version 3 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU Affero General Public License for more details.
//
//    You should have received a copy of the GNU Affero General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
//#############################################################################
openerp.excel_export = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;
    console.log('froeeeeeeeeeeeee')
    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;
            
            this._super.apply(this, arguments);

            if(self.getParent()){
            if(self.getParent().dataset.model=='tn.po.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportViewMain', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_po_tax_report').on('click', self.on_sidebar_export_view_xls_po_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_po_tax_report').on('click', self.on_sidebar_export_view_xml_po_tax_report);
            }
            else if(self.getParent().dataset.model=='tn.sale.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportsaletaxreport', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_sale_tax_report').on('click', self.on_sidebar_export_view_xls_sale_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_sale_tax_report').on('click', self.on_sidebar_export_view_xml_sale_tax_report);
            }
            else if(self.getParent().dataset.model=='ka.po.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportpotaxreport', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_ka_po_tax_report').on('click', self.on_sidebar_export_view_xls_ka_po_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_ka_po_tax_report').on('click', self.on_sidebar_export_view_xml_ka_po_tax_report);
            }
            else if(self.getParent().dataset.model=='ka.sale.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportkasaletaxreport', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_ka_sale_tax_report').on('click', self.on_sidebar_export_view_xls_ka_sale_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_ka_sale_tax_report').on('click', self.on_sidebar_export_view_xml_ka_sale_tax_report);
            }
            else if(self.getParent().dataset.model=='ap.sale.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportapsaletaxreport', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_ap_sale_tax_report').on('click', self.on_sidebar_export_view_xls_ap_sale_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_ap_sale_tax_report').on('click', self.on_sidebar_export_view_xml_ap_sale_tax_report);
            } 
            else if(self.getParent().dataset.model=='ap.po.report'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportappotaxreport', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_ap_po_tax_report').on('click', self.on_sidebar_export_view_xls_ap_po_tax_report);
                self.$el.find('.oe_sidebar_export_view_xml_ap_po_tax_report').on('click', self.on_sidebar_export_view_xml_ap_po_tax_report);
            } 

            }   
        },
        
        //for Tamilnadu Purchase Return Tax (XLS)
        on_sidebar_export_view_xls_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id      
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        //for Tamilnadu Purchase Return Tax (XML)
        on_sidebar_export_view_xml_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id      
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        
                
        //for Tamilnadu Sale Return Tax (XLS)
        on_sidebar_export_view_xls_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),       
        id=self.getParent().datarecord.id     
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },                      
        //for Tamilnadu Sale Return Tax (XML)
        on_sidebar_export_view_xml_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),
        
        id=self.getParent().datarecord.id
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },        
        
       
       //for Karnataka PO Return Tax (XLS)
        on_sidebar_export_view_xls_ka_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id       
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/ka/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        //for Karnataka PO Return Tax (XML)
        on_sidebar_export_view_xml_ka_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id       
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/ka/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        
        //for Karnataka Sale Return Tax (XLS)
        on_sidebar_export_view_xls_ka_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id             
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/ka/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },        
        //for Karnataka Sale Return Tax (XML)
        on_sidebar_export_view_xml_ka_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),
        
        id=self.getParent().datarecord.id
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/ka/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        
        //for Andra pradesh Sale Return Tax (XLS)
        on_sidebar_export_view_xls_ap_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id              
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/ap/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },        
        //for Andra pradesh Sale Return Tax (XML)
        on_sidebar_export_view_xml_ap_sale_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id              
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/ap/sale/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        
        //for Andra pradesh PO Return Tax (XLS)
        on_sidebar_export_view_xls_ap_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id              
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/ap/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
        //for Andra pradesh PO Return Tax (XML)
        on_sidebar_export_view_xml_ap_po_tax_report: function(){
            var self = this,
            view = this.getParent(),        
        id=self.getParent().datarecord.id              
        //Download the file        
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xml_view/ap/po/tax',
            data: {data: JSON.stringify({
                model: view.model,
                id: id,                
            })},
            complete: $.unblockUI
        });
        },
       
    });

};
