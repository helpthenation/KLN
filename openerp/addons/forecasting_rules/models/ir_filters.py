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

import logging
from datetime import datetime

from openerp import _, api, models
from openerp.exceptions import ValidationError
from openerp.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    _logger.debug('Cannot `import pandas`.')


class IrFilters(models.Model):

    _inherit = 'ir.filters'

    @api.model
    def is_field(self, model_obj, value):
        """Check if a given name correspond as field in the given model.

        :model_obj: string with the name of the model
        :value: the name of the field that want to check.
        :return: True or False
        """
        if isinstance(value, (str,)):
            field_list = model_obj.fields_get().keys()
            if value in field_list:
                return True
        return False

    @api.model
    def process_context_value(self, model_obj, value):
        """Get the key in the context and return the way to process.

         - If value is a field into the model defined in the rule then will
           return a string with the field name
         - If value is not a field is support to be is a field into the model
           defined in the rule then will return a string with the field name

        If not a field then raise an error.

        :value: a string value extract from the context.
        :return: string with the field name to be execute
        """
        res = False
        value_type = False
        if self.is_field(model_obj, value):
            res = value
            value_type = 'field'
        else:
            raise ValidationError('\n'.join([
                _('Not valid context value.'), value,
                _(' is not a valid field in'), model_obj.name]))
        return res, value_type

    @api.multi
    def check_forecast_step(self, forecast_step):
        """ Check if the step given by the user is a valid step.
        Raise an ValidationError if not.

        :forecast_step: string with the forecast_step value.
        """
        valid_steps = ['day', 'week', 'month', 'year']
        if forecast_step not in valid_steps:
            raise ValidationError('\n'.join([
                _('Not valid context forecast_step value.'), forecast_step,
                _(' You can use this options as forecast step'),
                str(valid_steps)]))

    @api.multi
    def process_filter_data(self):
        """Read and pre-process the rule data (rule_id field) that will be use
        to fulfill the value_ids field.

        :return:
        """

        context = safe_eval(self.context)
        domain = safe_eval(self.domain)
        model_obj = self.env[self.model_id]
        group_by = context.get('group_by', False)

        # process order
        order = context.get('forecast_order')
        order, _ = self.process_context_value(model_obj, order)

        # process value
        value = context.get('forecast_value')
        value, vtype = self.process_context_value(model_obj, value)

        return model_obj, domain, order, value, group_by, vtype

    @api.model
    def check_forecast_order_type(self, orderfield, model_obj):
        """Check the forecast order field is of admit date/datetime field.

        :orderfield: name of the order field to check
        :model_obj: model were the field correspond.
        """
        fields = model_obj.fields_get(orderfield)
        fieldtype = fields.get(orderfield).get('type')
        if fieldtype not in ['date', 'datetime']:
            raise ValidationError(_(
                'You are using forecast step so the forecast order must be'
                ' date/datime type field'))

    @api.multi
    def group_and_fill(self, recordset, order, group_by, value, domain):
        """Run a read off the data with the given domain and order.
        If the order type is datetime then post-procress the value and extract
        only the day information.

        All the generated data then is added to a dataframe. Here the data is
        processed, filled empty dates and grouped.

        NOTE: If the order and the groupby field are the same then need to make
        a validation over the type of the groupby. If the groupby is a
        compossed group like 'date:month', 'date:year', etc then the order
        field need to be the same compossed element. This is nedeed because in
        the result the order field will not be found and will return an error.

        :recordset: are the fields result for the odoo search that correspond
                    to the domain and order given by the filter.
        :order: the field used to order the retrieve elements.
        :group_by: how to group by the results
        :value: the field to extract from the result to use as value
        :domain: the domain to apply to the search

        :return: a list of tuples od the form (0, 0, {}) with the basic data to
        create new forecasting data objects.
        """
        values = recordset.read([value, order])
        if recordset.fields_get(order).get(order).get('type') == 'datetime':
            for val in values:
                val.update({order: datetime.strptime(
                    val.get(order), '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')
                })

        # Create data frame.
        data = pd.DataFrame(values)

        # Order by date
        if len(data):
            data[order] = pd.to_datetime(data[order])
            data = data.set_index(order)

        # Fill empty values
        forecast_step = safe_eval(self.context).get('forecast_step', False)
        if forecast_step:
            data = self.fill_empty_dates(data, order, value, domain)

        if group_by:
            # Group values using pandas.dataFrame object.
            data['day'] = data.index.to_period('D')
            data['week'] = data.index.to_period('W')
            data['month'] = data.index.to_period('M')
            data['year'] = data.index.to_period('Y')

            # process group_by info, return real group_by field
            group_info = group_by[0].split(':')
            if len(group_info) == 2:
                _, groupby = group_info
            data = data.groupby(data[groupby]).sum()

        # Fill missing labels taking into account the date
        date_format = self.get_date_fortmat(group_by and groupby or 'day')
        data[order] = data.index.to_datetime()
        data['label'] = data[order].apply(lambda row: row.strftime(
            date_format))

        # Add sequence column by date.
        data['sequence'] = list(range(1, len(data) + 1))

        # Update all the forecast values. Add new and overwrite old one
        # sequences.
        value_ids = self.get_value_ids(data, value, all_new=True)

        return value_ids

    @api.model
    def fill_empty_dates(self, data, order, value, domain):
        """Add new value lines for those empty data dates taking into account
        the step.
        """
        # Extract all date range information
        # TODO if step then the date range must exist in the domain of
        # the rule.

        forecast_date = [item[-1] for item in domain if order in item]
        all_dates = pd.DataFrame(
            index=pd.date_range(min(forecast_date), max(forecast_date)),
            columns=[value]).fillna(0.0)

        if 'id' in data.columns:
            data.pop('id')
        data = data.add(all_dates).fillna(0.0)
        return data

    @api.model
    def get_date_fortmat(self, forecast_step):
        """Return the string with the date format to write as the
        values label.

        :forecast_step: forecast step type; Could be ['day', 'week', 'month',
        'year']

        :return: string with the date format.  If not defined step type raise
                 exception
        """
        date_format = dict(
            day='%d %b %Y',
            week='W%U %Y',
            month='%B %Y',
            year='%Y')
        if forecast_step not in date_format:
            raise ValidationError(_('Forecast Step type not defined ') +
                                  forecast_step)
        return date_format[forecast_step]

    @api.model
    def get_value_ids(self, data, value, all_new=False):
        """Transform the pandas.DataFrame object to a list of values to be
        written as a o2m field in odoo named value_ids.

        :data: DataFrame object with the forecasting results per point

        :returns: list with the values to update the o2m forecast.value_ids
        field
        """
        value_ids = list()
        for row in data.iterrows():
            rowi = row[1]
            field_op = 0 if all_new else int(rowi.id)
            id_int = 0 if all_new else int(rowi.id)
            value_ids.append((field_op, id_int, {
                'sequence': int(rowi.sequence),
                'label': rowi.label,
                'value': rowi[value]})
            )
        return value_ids

    @api.multi
    def special_search(self):
        """Read and pre-process the filter data and then peform the search

        :return: a list with the dictionary need to fill the forecast data
                 values. keys = ['sequence', 'label', 'value']
        """
        value_ids = []
        (model_obj, domain, order, value, group_by, value_type) = \
            self.process_filter_data()

        if value_type == 'field':
            data = model_obj.search(domain, order=order)
            value_ids = self.group_and_fill(data, order, group_by, value,
                                            domain)
        return value_ids

    @api.multi
    def get_related_rules(self):
        """:return: the recordset list of related rules
        """
        rule_obj = self.env['forecasting.rule']
        return rule_obj.sudo().search([('filter_id', 'in', self.ids)])

    @api.constrains('context')
    def _check_context(self):
        """Check context introduce by user is valid, for that:

            - Check context is a valid python expression
            - Check context is a dictionary
            - Check context have ['forecast_order', 'forecast_value'] keys
            - Check context ['forecast_order', 'forecast_value'] keys are valid

        """
        error = _('The context value you introduce is not a valid context')
        related_rules = self.get_related_rules()
        if related_rules:

            # Check context is a valid python expression
            try:
                forecast_context = safe_eval(self.context)
            except:
                msg = _('Context is not a valid python expression')
                raise ValidationError('\n'.join([error, msg, self.context]))

            # Check context is a dictionary
            if not isinstance(forecast_context, (dict,)):
                msg = _('Context must be a dictionary')
                raise ValidationError('\n'.join([error, msg, self.context]))

            # Check context have ['forecast_order', 'forecast_value'] keys
            missing_key_error = str()
            for nkey in ['forecast_order', 'forecast_value']:
                if nkey not in forecast_context.keys():
                    missing_key_error += _(
                        " - The {context_key} key must exist in the filter"
                        " record to be use as forcasting rule.\n").format(
                            context_key=nkey)
            if missing_key_error:
                raise ValidationError('\n'.join([error, missing_key_error,
                                                 self.context]))

            # Check forecast step
            forecast_step = forecast_context.get('forecast_step', False)
            forecast_order = forecast_context.get('forecast_order', False)
            model_obj = self.env[self.model_id]
            if forecast_step:
                self.check_forecast_step(forecast_step)
                self.check_forecast_order_type(forecast_order, model_obj)

            # Check valid ['forecast_order', 'forecast_value', 'forecast_step']
            self.process_filter_data()

    @api.constrains('domain')
    def _check_domain(self):
        """ Check that the domain is valid:

            - Check domain is a python expression
            - Check domain is a list of tuples
        """
        error = _('The domain value you introduce is not a valid domain')
        related_rules = self.get_related_rules()
        if related_rules:

            # Check domain is a valid python expression
            try:
                domain = safe_eval(self.domain)
            except:
                msg = _('Domain is not a valid python expression')
                raise ValidationError('\n'.join([error, msg, self.domain]))

            # Check domain is a list of tuples
            if not isinstance(domain, (list,)):
                msg = _('Domain must be a list')
                raise ValidationError('\n'.join([error, msg, self.domain]))
            else:
                list_item_type = set([type(item) for item in domain])
                if not list_item_type == set([type(tuple())]):
                    msg = _('Domain must be a list of tuples')
                    raise ValidationError('\n'.join([error, msg, self.domain]))
