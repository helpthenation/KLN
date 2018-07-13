from openerp import models, fields, api, _


class crm_lead_inherit_hr(models.Model):
    _inherit = 'crm.lead'
    _description = "Lead/Opportunity"
    _rec_name = 'seq_no'
    
    seq_no = fields.Char('Number', size=64, required=True, readonly=True)
     
    _defaults = {
    'seq_no': lambda obj, cr, uid, context: '/',
    }
    
    @api.model
    def create(self,vals):
        if vals.get('seq_no', '/') == '/':
            vals['seq_no'] = self.env['ir.sequence'].get('employee.code.sequence') or '/'
        new_id = super(crm_lead_inherit_hr, self).create(vals)
        return new_id
