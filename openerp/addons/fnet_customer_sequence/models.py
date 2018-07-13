# -*- coding: utf-8 -*-

from openerp import models, fields, api

class customer_id_field(models.Model):
    _inherit = 'res.partner'

    customer_id = fields.Char(string="Customer ID", readonly=True, required=False)

    @api.model
    def create(self, data):
        sequence = self.env['ir.sequence']
        print'CCCCCCCCCCCCCCCCCCCCCCCCCCC',self._context.get('company_id', self.env.user.company_id.id)
        company=self.env['res.company'].browse(self._context.get('company_id', self.env.user.company_id.id)).com_type or ' '
        if data['customer'] == True:
            prefix = company.upper()
            sequence = self.env['ir.sequence'].search([('prefix','=',prefix),('code','=','res.partner.customers')])
            if not sequence:
                padding = 4
                implementation='no_gap'
                active=True
                company_id=self._context.get('company_id', self.env.user.company_id.id)
                sequence = self.env['ir.sequence'].create({'prefix':prefix,'padding':padding,'implementation':implementation,'active':active, 'name':'Customer Id '+prefix,'code':'res.partner.customers','company_id':self._context.get('company_id', self.env.user.company_id.id)})
            data['customer_id'] = sequence.get_id(sequence.id,'id')
        return super(customer_id_field, self).create(data)

    @api.multi
    def write(self, vals):
        sequence = self.env['ir.sequence']
        company=self.company_id.com_type or ' '
        if 'customer' in vals.keys():
            if vals['customer'] == True:
                prefix = company.upper()
                sequence = self.env['ir.sequence'].search([('prefix','=',prefix),('code','=','res.partner.customers')])
                if not sequence:
                    padding = 4
                    implementation='no_gap'
                    active=True
                    company_id=self.company_id
                    sequence = self.env['ir.sequence'].create({'prefix':prefix,'padding':padding,'implementation':implementation,'active':active, 'name':'Customer Id '+prefix,'code':'res.partner.customers','company_id':self.company_id})
                vals['customer_id'] = sequence.get_id(sequence.id,'id')
        return super(customer_id_field, self).write(vals)

    @api.model
    @api.multi
    def _updating_customer_sequence(self):
        self.env.cr.execute("""select id,com_type from res_company where com_type != ' '""")
        com_list=self.env.cr.dictfetchall() 
        last_val=[]
        for i in com_list:
           n=0000
           self.env.cr.execute('''select id from res_partner where company_id=%d and active != False and customer=True order by name asc'''%(i['id']))
           partner_list=self.env.cr.dictfetchall() 
           for j in partner_list:
               n=n+1
               num='%04d' % n
               seq=i['com_type'].upper()+str(num)
               self.env.cr.execute("""update res_partner set customer_id='%s' where id=%d and company_id=%d and customer=True"""%(seq,j['id'],i['id']))
           last_val.append({'prefix':i['com_type'].upper(),'company':i['id']})
           n=0000
        for k in last_val:      
           prefix=k['prefix']
           sequence = self.env['ir.sequence'].search([('prefix','=',prefix),('code','=','res.partner.customers')])
           self.env.cr.execute("select count(id) as val from res_partner where company_id=%d and active != False and customer=True"%(k['company']))
           nxt=self.env.cr.dictfetchone() 
           if not sequence:  
               padding = 4
               implementation='no_gap'
               active=True
               company_id=k['company']
               number_next_actual=int(nxt['val'])+1
               sequence = self.env['ir.sequence'].create({'prefix':prefix,'padding':padding,'implementation':implementation,'active':active, 'name':'Customer Id '+prefix,'code':'res.partner.customers','company_id':k['company'],'number_next_actual':number_next_actual})    
