
from openerp import models, fields, api
from datetime import datetime
import logging
_logger = logging.getLogger(__name__)

class AccountTaxTemplate(models.Model):
    _name = 'account.tax.template'
    
    def _get_tax_vals(self, company):
        """ This method generates a dictionnary of all the values for the tax that will be created.
        """
        self.ensure_one()
        val = {
            'name': self.name,
            'type_tax_use': self.type_tax_use,
            'amount_type': self.amount_type,
            'active': self.active,
            'company_id': company.id,
            'sequence': self.sequence,
            'amount': self.amount,
            'description': self.description,
            'price_include': self.price_include,
            'include_base_amount': self.include_base_amount,
            'analytic': self.analytic,
            'tag_ids': [(6, 0, [t.id for t in self.tag_ids])],
            'tax_adjustment': self.tax_adjustment,
        }
        if self.tax_group_id:
            val['tax_group_id'] = self.tax_group_id.id
        return val    
    @api.multi
    def _generate_tax(self, company):
        """ This method generate taxes from templates.

            :param company: the company for which the taxes should be created from templates in self
            :returns: {
                'tax_template_to_tax': mapping between tax template and the newly generated taxes corresponding,
                'account_dict': dictionary containing a to-do list with all the accounts to assign on new taxes
            }
        """
        todo_dict = {}
        tax_template_to_tax = {}
        for tax in self:
            # Compute children tax ids
            children_ids = []
            for child_tax in tax.children_tax_ids:
                if tax_template_to_tax.get(child_tax.id):
                    children_ids.append(tax_template_to_tax[child_tax.id])
            vals_tax = tax._get_tax_vals(company)
            vals_tax['children_tax_ids'] = children_ids and [(6, 0, children_ids)] or []
            new_tax = self.env['account.chart.template'].create_record_with_xmlid(company, tax, 'account.tax', vals_tax)
            tax_template_to_tax[tax.id] = new_tax
            # Since the accounts have not been created yet, we have to wait before filling these fields
            todo_dict[new_tax] = {
                'account_id': tax.account_id.id,
                'refund_account_id': tax.refund_account_id.id,
            }

        return {
            'tax_template_to_tax': tax_template_to_tax,
            'account_dict': todo_dict
        }
