# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from openerp import _, api, fields, models
from openerp.exceptions import ValidationError, Warning as UserError


class Forecast(models.Model):

    _inherit = 'forecast'

    manual_data = fields.Boolean(
        'Use Manual Data',
        help='Indicate if the forecast data used is external data introduce'
             ' manually by the user')
    rule_id = fields.Many2one(
        'forecasting.rule',
        string='Forecast Rule',
        help='Forecast Rule used to fill the forecast data values. You add'
             ' a model and a ir.filter and used to extract the data to be used'
             ' as forecast data')

    @api.multi
    def fill_value_ids(self):
        """Overwrite the forecasting.value_ids field.  The new values will be
        created with the current forecast rule.

        NOTE: This method is use in the forecast form view as a button named
        "Fill Values"
        """
        for forecast in self:
            if forecast.manual_data:
                raise UserError(_(
                    ' Fill the forecast values manually or uncheck'
                    ' Use Manual Data.'))
            else:
                if not forecast.rule_id:
                    raise UserError(_(
                        ' There is not forecast rule to fill the values.'))
                forecast._check_required_irfilter()
                forecast.value_ids.unlink()
                forecast.write({
                    'value_ids': forecast.rule_id.filter_id.special_search()})

    @api.multi
    def _check_required_irfilter(self):
        """If the rule is related to a forecast and have not filter then
        Raise a ValidationError.
        """
        if self.rule_id and not self.rule_id.filter_id:
            raise ValidationError(_(
                ' Missing Rule Filter: The current forecast rule have not'
                ' filter defined so can not generate the forecast values.'))
