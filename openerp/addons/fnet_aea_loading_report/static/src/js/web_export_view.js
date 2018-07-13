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
openerp.fnet_aea_loading_report = function (instance) {

    var _t = instance.web._t, QWeb = instance.web.qweb;
    instance.web.Sidebar.include({
        redraw: function () {
            var self = this;            
            this._super.apply(this, arguments);
            if(self.getParent()){
                console.log("555555555555555555",self.getParent().view_type)
            if(self.getParent().dataset.model=='account.invoice' && self.getParent().view_type == 'tree'){
                self.$el.find('.oe_sidebar').append(QWeb.render('AddExportLoading', {widget: self}));
                self.$el.find('.oe_sidebar_export_view_xls_loadding_report').on('click', self.on_sidebar_export_view_xls_loadding_report);
            }
        }
        },
        
        //for Tamilnadu Purchase Return Tax (XLS)
        on_sidebar_export_view_xls_loadding_report: function(){
            var self = this,
            view = this.getParent(),        
            ids =self.getParent().get_selected_ids()
            
            
        //~ //Download the file        /web/export/xls_view/ac/loading
        $.blockUI();
        view.session.get_file({
            url: '/web/export/xls_view/ac/loading',
            data: {data: JSON.stringify({
                model: view.model,
                ids: ids,                
            })},
            complete: $.unblockUI
        });
        },
   
       
    });

};
