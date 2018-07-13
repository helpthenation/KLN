# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
class crm_lead(models.Model):

    _inherit ='crm.lead'
    
    tender_counter=fields.Integer(compute='get_tender_count',readonly=True)
    quote_counter=fields.Integer(compute='get_quote_count',readonly=True)
   

    @api.one
    def get_tender_count(self):
        '''
        This function is used to get the count of the tender
        '''
        var=0
        purchase_id=self.env['purchase.order'].search([('lead_id','=',self.ids[0])])
        for i in purchase_id:
            var +=1
        self.tender_counter=var 
        
    @api.one
    def get_quote_count(self):
        '''
        This function is used to get the count of the tender
        '''
        var=0
        sale_id=self.env['sale.order'].search([('lead_id','=',self.ids[0])])
        for i in sale_id:
            var +=1
        self.quote_counter=var 
              
              
    @api.multi   
    def open_tender(self):
        """ This opens purchase tender view to view all opportunity associated to the call for tenders
            @return: the tender tree view
        """
        var=[]
        if self._context is None:
            context = {}
        res = self.env['ir.actions.act_window'].for_xml_id('purchase', 'purchase_rfq')
        res['context'] = self._context
        purchase_id=self.env['purchase.order'].search([('lead_id','=',self.ids[0])])
        for i in purchase_id:
            var.append(i.id)
        res['domain'] = [('id', 'in', var)]
        return res 
                  
    @api.multi   
    def open_sale_quote(self):
        """ This opens sale quotation view to view all quote associated to the enquiry
            @return: the tender tree view
        """
        var=[]
        if self._context is None:
            context = {}
        res = self.env['ir.actions.act_window'].for_xml_id('sale', 'action_quotations')
        res['context'] = self._context
        sale_id=self.env['sale.order'].search([('lead_id','=',self.ids[0])])
        for i in sale_id:
            var.append(i.id)
        res['domain'] = [('id', 'in', var)]
        return res           
        
class purchase_requisition(models.Model):
    _inherit='purchase.requisition'
    
    quote_count=fields.Integer(compute='get_quote_count',readonly=True)
    enquiry_count=fields.Integer(compute='get_enquiry_count',readonly=True)
    
    @api.one
    def get_quote_count(self):
        """
        This function is return the count of the sale quotations 
        """
        count_quote=0
        #crm_obj=self.env['crm.lead'].search([('oppor_order','=',self.origin)]) 
        purchase_id=self.env['sale.order'].search([('request_id','=',self.id)])
        
        for purchase in purchase_id:
            count_quote +=1
        
        self.quote_count=count_quote
                    
    @api.multi
    def open_quotation(self):
        """
        This is used for view the sale quotation against the current tender
        """
        var=[]
        if self._context is None:
            context = {}
        res = self.env['ir.actions.act_window'].for_xml_id('sale', 'action_quotations')
        res['context'] = self._context
        #crm_obj=self.env['crm.lead'].search([('oppor_order','=',self.origin)]) 
        purchase_id=self.env['sale.order'].search([('request_id','=',self.id)])
        for i in purchase_id:
            var.append(i.id)
        res['domain'] = [('id', 'in', var)]
        return res
     
    @api.one
    def get_enquiry_count(self):
        """
        This function is return the count of the sale quotations 
        """
        count_quote=0
        #crm_obj=self.env['crm.lead'].search([('oppor_order','=',self.origin)]) 
        if self.lead_seq_id:
            purchase_id=self.env['crm.lead'].search([('id','=',self.lead_seq_id.id)])
            
            for purchase in purchase_id:
                count_quote +=1
        
        self.enquiry_count=count_quote
                    
    @api.multi
    def open_enquiry(self):
        """
        This is used for view the sale quotation against the current tender
        """
        var=[]
        if self._context is None:
            context = {}
        res = self.env['ir.actions.act_window'].for_xml_id('crm', 'crm_case_category_act_oppor11')
        res['context'] = self._context
        #crm_obj=self.env['crm.lead'].search([('oppor_order','=',self.origin)]) 
        purchase_id=self.env['crm.lead'].search([('id','=',self.lead_seq_id.id)])
        for i in purchase_id:
            var.append(i.id)
        res['domain'] = [('id', 'in', var)]
        return res  
    
    
    
